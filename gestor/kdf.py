"""Derivación de clave maestra (Argon2id / PBKDF2) y de subclaves (HKDF).

Flujo:
    contraseña maestra + sal (única por usuario)
        └─ KDF adaptativa (Argon2id o PBKDF2-HMAC-SHA256) ─> clave maestra (32 B)
              └─ HKDF-SHA256 (separación de dominio) ─> clave AES (32 B) + clave HMAC (32 B)

Nunca se usa la misma clave para cifrar y para autenticar.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import unicodedata
from dataclasses import dataclass, replace

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .errors import VaultFormatError, WeakParametersError

SALT_LEN = 16          # 128 bits, recomendado por RFC 9106 / NIST SP 800-132
KEY_LEN = 32           # 256 bits

ARGON2ID = "argon2id"
PBKDF2_SHA256 = "pbkdf2-sha256"

# Valores por defecto (RFC 9106 opción 2 / OWASP 2023+).
DEFAULT_ARGON2 = {"time_cost": 3, "memory_cost": 64 * 1024, "parallelism": 4}  # memory en KiB
DEFAULT_PBKDF2_ITERATIONS = 600_000

# Mínimos aceptados al abrir una bóveda (defensa ante parámetros degradados).
MIN_ARGON2 = {"time_cost": 1, "memory_cost": 8 * 1024, "parallelism": 1}
MIN_PBKDF2_ITERATIONS = 100_000

HKDF_INFO_PREFIX = b"gestor-seguro/v1/"


def generate_salt(length: int = SALT_LEN) -> bytes:
    """Sal aleatoria con el CSPRNG del sistema operativo (módulo `secrets`)."""
    if length < SALT_LEN:
        raise WeakParametersError(f"La sal debe tener al menos {SALT_LEN} bytes")
    return secrets.token_bytes(length)


@dataclass(frozen=True)
class KdfParams:
    """Parámetros públicos de la KDF. Se guardan junto a la bóveda (no son secretos)."""

    algorithm: str
    salt: bytes
    time_cost: int = DEFAULT_ARGON2["time_cost"]
    memory_cost: int = DEFAULT_ARGON2["memory_cost"]
    parallelism: int = DEFAULT_ARGON2["parallelism"]
    iterations: int = DEFAULT_PBKDF2_ITERATIONS

    @classmethod
    def new(cls, algorithm: str = ARGON2ID, **overrides) -> "KdfParams":
        """Crea parámetros nuevos con una sal recién generada."""
        params = replace(cls(algorithm=algorithm, salt=generate_salt()), **overrides)
        params.validate()
        return params

    def validate(self) -> None:
        if len(self.salt) < SALT_LEN:
            raise WeakParametersError("Sal demasiado corta")
        if self.algorithm == ARGON2ID:
            for name, minimum in MIN_ARGON2.items():
                if getattr(self, name) < minimum:
                    raise WeakParametersError(f"Argon2id: {name} < {minimum}")
        elif self.algorithm == PBKDF2_SHA256:
            if self.iterations < MIN_PBKDF2_ITERATIONS:
                raise WeakParametersError(f"PBKDF2: iteraciones < {MIN_PBKDF2_ITERATIONS}")
        else:
            raise WeakParametersError(f"Algoritmo KDF no soportado: {self.algorithm!r}")

    def to_dict(self) -> dict:
        d = {"algorithm": self.algorithm, "salt": base64.b64encode(self.salt).decode("ascii")}
        if self.algorithm == ARGON2ID:
            d.update(time_cost=self.time_cost, memory_cost=self.memory_cost,
                     parallelism=self.parallelism)
        else:
            d["iterations"] = self.iterations
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "KdfParams":
        try:
            kwargs = {"algorithm": d["algorithm"],
                      "salt": base64.b64decode(d["salt"], validate=True)}
            for name in ("time_cost", "memory_cost", "parallelism", "iterations"):
                if name in d:
                    kwargs[name] = int(d[name])
        except (KeyError, TypeError, ValueError) as exc:
            raise VaultFormatError("Parámetros KDF inválidos") from exc
        params = cls(**kwargs)
        params.validate()
        return params


def _normalize_password(password: str) -> bytes:
    """NFKC evita que la misma contraseña escrita con distinta composición Unicode
    (p. ej. 'ñ' precompuesta vs. 'n' + tilde combinante) derive claves distintas."""
    if not password:
        raise ValueError("La contraseña maestra no puede estar vacía")
    return unicodedata.normalize("NFKC", password).encode("utf-8")


def derive_master_key(password: str, params: KdfParams) -> bytes:
    """Deriva la clave maestra de 256 bits a partir de la contraseña y la sal."""
    params.validate()
    secret = _normalize_password(password)
    if params.algorithm == ARGON2ID:
        return hash_secret_raw(
            secret=secret,
            salt=params.salt,
            time_cost=params.time_cost,
            memory_cost=params.memory_cost,
            parallelism=params.parallelism,
            hash_len=KEY_LEN,
            type=Type.ID,
        )
    return hashlib.pbkdf2_hmac("sha256", secret, params.salt, params.iterations, dklen=KEY_LEN)


def derive_subkeys(master_key: bytes, purpose: bytes) -> tuple[bytes, bytes]:
    """HKDF-SHA256: separa la clave maestra en (clave_cifrado, clave_mac) independientes.

    `purpose` aplica separación de dominio: claves para fines distintos nunca coinciden.
    """
    if len(master_key) != KEY_LEN:
        raise ValueError("La clave maestra debe medir 32 bytes")
    okm = HKDF(
        algorithm=hashes.SHA256(),
        length=2 * KEY_LEN,
        salt=None,
        info=HKDF_INFO_PREFIX + purpose,
    ).derive(master_key)
    return okm[:KEY_LEN], okm[KEY_LEN:]

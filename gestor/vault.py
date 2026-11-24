"""Bóveda de contraseñas de conocimiento cero.

Jerarquía de claves (envelope encryption):

    contraseña maestra ──KDF(sal)──> clave maestra ──HKDF──> KEK (cifrado + MAC)
                                                               │
                                       envuelve (AES-CBC + HMAC)│
                                                               ▼
                         clave de bóveda aleatoria (DEK, 64 B = 32 AES + 32 HMAC)
                                                               │
                                                               ▼
                                     cada entrada cifrada con AES-CBC + HMAC

Ventajas:
* Lo que se persiste es: parámetros KDF + sal (públicos), DEK envuelta y entradas
  cifradas. Ni la contraseña maestra, ni la clave maestra, ni un hash de la
  contraseña, ni ningún texto plano salen nunca del cliente.
* Cambiar la contraseña maestra solo re-envuelve la DEK (no re-cifra todo).
* La cabecera (id + parámetros KDF) va como AD del envoltorio: manipularla
  (p. ej. bajar las iteraciones) hace fallar la apertura.
* Cada entrada usa como AD "vault_id|entry_id": no se puede copiar un
  ciphertext de una entrada a otra ni de una bóveda a otra.
"""

from __future__ import annotations

import base64
import json
import secrets
import uuid
from datetime import datetime, timezone

from . import cipher
from .errors import (EntryNotFoundError, IntegrityError, InvalidPasswordError,
                     VaultFormatError)
from .kdf import ARGON2ID, KdfParams, derive_master_key, derive_subkeys
from .storage import StorageBackend

VAULT_FORMAT = "gestor-seguro-vault"
VAULT_VERSION = 1
DEK_LEN = 64
KEK_PURPOSE = b"key-encryption-key"


def _b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.b64decode(text, validate=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _header_ad(vault_id: str, params: KdfParams) -> bytes:
    canonical = json.dumps(params.to_dict(), sort_keys=True, separators=(",", ":"))
    return f"{VAULT_FORMAT}|v{VAULT_VERSION}|{vault_id}|{canonical}".encode("utf-8")


def _entry_ad(vault_id: str, entry_id: str) -> bytes:
    return f"entry|{vault_id}|{entry_id}".encode("utf-8")


def _wrap_dek(password: str, params: KdfParams, vault_id: str, dek: bytes) -> bytes:
    kek_enc, kek_mac = derive_subkeys(derive_master_key(password, params), KEK_PURPOSE)
    return cipher.encrypt(kek_enc, kek_mac, dek, _header_ad(vault_id, params))


def _unwrap_dek(password: str, params: KdfParams, vault_id: str, wrapped: bytes) -> bytes:
    kek_enc, kek_mac = derive_subkeys(derive_master_key(password, params), KEK_PURPOSE)
    try:
        dek = cipher.decrypt(kek_enc, kek_mac, wrapped, _header_ad(vault_id, params))
    except IntegrityError:
        # Contraseña incorrecta y cabecera manipulada son indistinguibles a propósito.
        raise InvalidPasswordError("Contraseña maestra incorrecta o bóveda manipulada") from None
    if len(dek) != DEK_LEN:
        raise VaultFormatError("Clave de bóveda con longitud inválida")
    return dek


class Vault:
    """Bóveda desbloqueada en memoria. Usar `Vault.create` o `Vault.open`."""

    def __init__(self, storage: StorageBackend, vault_id: str, params: KdfParams,
                 wrapped_dek: bytes, dek: bytes, entries: dict[str, str]):
        self._storage = storage
        self._vault_id = vault_id
        self._params = params
        self._wrapped_dek = wrapped_dek
        self._enc_key: bytes | None = dek[:32]
        self._mac_key: bytes | None = dek[32:]
        self._entries = entries  # entry_id -> blob cifrado en base64

    # ------------------------------------------------------------------ ciclo de vida
    @classmethod
    def create(cls, storage: StorageBackend, master_password: str,
               kdf_algorithm: str = ARGON2ID, overwrite: bool = False,
               **kdf_overrides) -> "Vault":
        if storage.exists() and not overwrite:
            raise FileExistsError("Ya existe una bóveda en ese almacenamiento")
        params = KdfParams.new(kdf_algorithm, **kdf_overrides)
        vault_id = str(uuid.uuid4())
        dek = secrets.token_bytes(DEK_LEN)
        wrapped = _wrap_dek(master_password, params, vault_id, dek)
        vault = cls(storage, vault_id, params, wrapped, dek, {})
        vault.save()
        return vault

    @classmethod
    def open(cls, storage: StorageBackend, master_password: str) -> "Vault":
        try:
            data = json.loads(storage.read().decode("utf-8"))
            if data.get("format") != VAULT_FORMAT or data.get("version") != VAULT_VERSION:
                raise VaultFormatError("Formato o versión de bóveda no soportados")
            vault_id = str(uuid.UUID(data["vault_id"]))
            params = KdfParams.from_dict(data["kdf"])
            wrapped = _b64d(data["wrapped_key"])
            entries = dict(data["entries"])
        except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
            raise VaultFormatError("Archivo de bóveda corrupto") from exc
        dek = _unwrap_dek(master_password, params, vault_id, wrapped)
        return cls(storage, vault_id, params, wrapped, dek, entries)

    def lock(self) -> None:
        """Olvida las claves. (En Python no se puede garantizar el borrado de memoria:
        `bytes` es inmutable y el GC decide cuándo liberar.)"""
        self._enc_key = self._mac_key = None

    @property
    def locked(self) -> bool:
        return self._enc_key is None

    def __enter__(self) -> "Vault":
        return self

    def __exit__(self, *exc) -> None:
        self.lock()

    def save(self) -> None:
        doc = {
            "format": VAULT_FORMAT,
            "version": VAULT_VERSION,
            "vault_id": self._vault_id,
            "kdf": self._params.to_dict(),
            "wrapped_key": _b64e(self._wrapped_dek),
            "entries": self._entries,
        }
        self._storage.write(json.dumps(doc, indent=2, sort_keys=True).encode("utf-8"))

    def change_master_password(self, new_password: str) -> None:
        """Nueva sal + re-envoltura de la DEK. Las entradas no se re-cifran."""
        self._require_unlocked()
        new_params = KdfParams.new(
            self._params.algorithm,
            **{k: getattr(self._params, k)
               for k in ("time_cost", "memory_cost", "parallelism", "iterations")})
        dek = self._enc_key + self._mac_key
        self._wrapped_dek = _wrap_dek(new_password, new_params, self._vault_id, dek)
        self._params = new_params
        self.save()

    # ------------------------------------------------------------------ entradas
    def add_entry(self, site: str, username: str, password: str, notes: str = "") -> str:
        self._require_unlocked()
        entry_id = str(uuid.uuid4())
        now = _now()
        self._store(entry_id, {"site": site, "username": username, "password": password,
                               "notes": notes, "created": now, "updated": now})
        return entry_id

    def get_entry(self, entry_id: str) -> dict:
        self._require_unlocked()
        if entry_id not in self._entries:
            raise EntryNotFoundError(entry_id)
        blob = _b64d(self._entries[entry_id])
        plaintext = cipher.decrypt(self._enc_key, self._mac_key, blob,
                                   _entry_ad(self._vault_id, entry_id))
        return {"id": entry_id, **json.loads(plaintext.decode("utf-8"))}

    def update_entry(self, entry_id: str, **changes) -> None:
        entry = self.get_entry(entry_id)
        entry.pop("id")
        allowed = {"site", "username", "password", "notes"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"Campos no permitidos: {sorted(unknown)}")
        entry.update(changes, updated=_now())
        self._store(entry_id, entry)

    def delete_entry(self, entry_id: str) -> None:
        self._require_unlocked()
        if self._entries.pop(entry_id, None) is None:
            raise EntryNotFoundError(entry_id)
        self.save()

    def list_entries(self) -> list[dict]:
        """Resumen sin contraseñas (los nombres de sitio también van cifrados en disco)."""
        result = []
        for entry_id in self._entries:
            e = self.get_entry(entry_id)
            result.append({"id": entry_id, "site": e["site"], "username": e["username"]})
        return sorted(result, key=lambda e: (e["site"].lower(), e["username"].lower()))

    def find(self, site: str) -> list[dict]:
        needle = site.lower()
        return [self.get_entry(e["id"]) for e in self.list_entries()
                if needle in e["site"].lower()]

    # ------------------------------------------------------------------ internos
    def _store(self, entry_id: str, entry: dict) -> None:
        plaintext = json.dumps(entry, ensure_ascii=False).encode("utf-8")
        blob = cipher.encrypt(self._enc_key, self._mac_key, plaintext,
                              _entry_ad(self._vault_id, entry_id))
        self._entries[entry_id] = _b64e(blob)
        self.save()

    def _require_unlocked(self) -> None:
        if self.locked:
            raise RuntimeError("La bóveda está bloqueada")

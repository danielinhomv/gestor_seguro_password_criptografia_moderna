"""AES-256-CBC + HMAC-SHA256 en modo Encrypt-then-MAC.

Formato del blob cifrado:

    +---------+-----------+------------------------+-------------------+
    | versión |  IV (16)  |  ciphertext (n * 16)   |  HMAC-SHA256 (32) |
    |  (1 B)  |           |  AES-256-CBC + PKCS#7  |                   |
    +---------+-----------+------------------------+-------------------+

El HMAC cubre:  versión || len(AD) (8 B big-endian) || AD || IV || ciphertext

* Encrypt-then-MAC: se autentica el *ciphertext*, y al descifrar se verifica el
  HMAC (en tiempo constante) ANTES de tocar AES o el padding. Un atacante que
  modifique un solo bit recibe siempre el mismo error genérico -> no existe
  oráculo de padding.
* AD (datos asociados): contexto que no se cifra pero sí se autentica (p. ej. el
  id de la entrada). Impide "mover" un ciphertext válido a otro registro.
* El IV es aleatorio por cada cifrado (CBC exige IV impredecible).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .errors import IntegrityError

FORMAT_VERSION = b"\x01"
IV_LEN = 16
TAG_LEN = 32
BLOCK_BITS = 128
KEY_LEN = 32
MIN_BLOB_LEN = len(FORMAT_VERSION) + IV_LEN + 16 + TAG_LEN  # al menos un bloque


def _check_keys(enc_key: bytes, mac_key: bytes) -> None:
    if len(enc_key) != KEY_LEN or len(mac_key) != KEY_LEN:
        raise ValueError("Las claves AES y HMAC deben medir 32 bytes cada una")
    if hmac.compare_digest(enc_key, mac_key):
        raise ValueError("La clave de cifrado y la de MAC deben ser distintas")


def compute_hmac(mac_key: bytes, version: bytes, iv: bytes, ciphertext: bytes,
                 associated_data: bytes = b"") -> bytes:
    """HMAC-SHA256 con longitud de AD prefijada (evita ambigüedad de concatenación)."""
    mac = hmac.new(mac_key, digestmod=hashlib.sha256)
    mac.update(version)
    mac.update(len(associated_data).to_bytes(8, "big"))
    mac.update(associated_data)
    mac.update(iv)
    mac.update(ciphertext)
    return mac.digest()


def verify_hmac(mac_key: bytes, version: bytes, iv: bytes, ciphertext: bytes,
                tag: bytes, associated_data: bytes = b"") -> None:
    """Lanza IntegrityError si el tag no coincide. Comparación en tiempo constante."""
    expected = compute_hmac(mac_key, version, iv, ciphertext, associated_data)
    if not hmac.compare_digest(expected, tag):
        raise IntegrityError("Fallo de autenticación de los datos cifrados")


def encrypt(enc_key: bytes, mac_key: bytes, plaintext: bytes,
            associated_data: bytes = b"") -> bytes:
    """Cifra con AES-256-CBC y añade HMAC-SHA256 sobre el resultado (Encrypt-then-MAC)."""
    _check_keys(enc_key, mac_key)
    iv = secrets.token_bytes(IV_LEN)

    padder = padding.PKCS7(BLOCK_BITS).padder()
    padded = padder.update(plaintext) + padder.finalize()

    encryptor = Cipher(algorithms.AES(enc_key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    tag = compute_hmac(mac_key, FORMAT_VERSION, iv, ciphertext, associated_data)
    return FORMAT_VERSION + iv + ciphertext + tag


def decrypt(enc_key: bytes, mac_key: bytes, blob: bytes,
            associated_data: bytes = b"") -> bytes:
    """Verifica el HMAC y, solo si es válido, descifra. Cualquier fallo -> IntegrityError."""
    _check_keys(enc_key, mac_key)
    if len(blob) < MIN_BLOB_LEN or (len(blob) - 1 - IV_LEN - TAG_LEN) % 16 != 0:
        raise IntegrityError("Fallo de autenticación de los datos cifrados")

    version = blob[:1]
    iv = blob[1:1 + IV_LEN]
    ciphertext = blob[1 + IV_LEN:-TAG_LEN]
    tag = blob[-TAG_LEN:]

    # 1) Autenticar primero (la versión también está cubierta por el MAC).
    verify_hmac(mac_key, version, iv, ciphertext, tag, associated_data)
    if version != FORMAT_VERSION:
        raise IntegrityError("Versión de formato no soportada")

    # 2) Solo ahora, con datos auténticos, descifrar y quitar el padding.
    decryptor = Cipher(algorithms.AES(enc_key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    try:
        unpadder = padding.PKCS7(BLOCK_BITS).unpadder()
        return unpadder.update(padded) + unpadder.finalize()
    except ValueError as exc:  # Inalcanzable salvo bug: el MAC ya garantizó integridad.
        raise IntegrityError("Fallo de autenticación de los datos cifrados") from exc

"""Gestor seguro de contraseñas: KDF (Argon2id/PBKDF2) + AES-256-CBC + HMAC-SHA256."""

from .cipher import decrypt, encrypt
from .errors import (EntryNotFoundError, GestorError, IntegrityError, InvalidPasswordError,
                     VaultFormatError, WeakParametersError)
from .kdf import KdfParams, derive_master_key, derive_subkeys, generate_salt
from .storage import FileStorage, MemoryStorage, StorageBackend
from .vault import Vault

__all__ = [
    "Vault", "KdfParams", "FileStorage", "MemoryStorage", "StorageBackend",
    "generate_salt", "derive_master_key", "derive_subkeys", "encrypt", "decrypt",
    "GestorError", "IntegrityError", "InvalidPasswordError", "VaultFormatError",
    "WeakParametersError", "EntryNotFoundError",
]

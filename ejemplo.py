"""Demostración paso a paso del flujo completo.  Ejecutar:  python ejemplo.py"""

import json
import tempfile
from pathlib import Path

from gestor import (FileStorage, IntegrityError, KdfParams, Vault, decrypt, derive_master_key,
                    derive_subkeys, encrypt, generate_salt)

print("=== 1. Primitivas ===")
salt = generate_salt()
params = KdfParams(algorithm="argon2id", salt=salt)
master = derive_master_key("contraseña maestra", params)
enc_key, mac_key = derive_subkeys(master, b"demo")
print("sal          :", salt.hex())
print("clave maestra:", master.hex(), "(solo existe en RAM)")

blob = encrypt(enc_key, mac_key, b"mi secreto", associated_data=b"entrada-1")
print("blob         :", blob.hex())
print("descifrado   :", decrypt(enc_key, mac_key, blob, b"entrada-1"))

tampered = bytearray(blob)
tampered[20] ^= 1
try:
    decrypt(enc_key, mac_key, bytes(tampered), b"entrada-1")
except IntegrityError as e:
    print("manipulación :", "detectada ->", e)

print("\n=== 2. Bóveda ===")
path = Path(tempfile.mkdtemp()) / "vault.json"
with Vault.create(FileStorage(path), "Contraseña-Maestra-2026") as v:
    entry_id = v.add_entry("github.com", "gladys", "gh-p4ss-muy-segura", notes="token 2FA")

print("Contenido en disco (lo único que vería un servidor):")
print(json.dumps(json.loads(path.read_text()), indent=2)[:900], "...")

with Vault.open(FileStorage(path), "Contraseña-Maestra-2026") as v:
    print("\nRecuperado:", v.get_entry(entry_id))

try:
    Vault.open(FileStorage(path), "contraseña-equivocada")
except Exception as e:
    print("Contraseña incorrecta ->", type(e).__name__, ":", e)

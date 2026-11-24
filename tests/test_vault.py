import base64
import json

import pytest
from conftest import FAST_ARGON2, FAST_PBKDF2

from gestor import FileStorage, MemoryStorage, Vault
from gestor.errors import (EntryNotFoundError, IntegrityError, InvalidPasswordError,
                           WeakParametersError)

MASTER = "Mi-Contraseña-Maestra-Larga-2026"
SECRET = "S3cr3t0-De-Gmail!#"


def _new_vault(storage, alg="argon2id"):
    extra = FAST_ARGON2 if alg == "argon2id" else FAST_PBKDF2
    return Vault.create(storage, MASTER, kdf_algorithm=alg, **extra)


@pytest.mark.parametrize("alg", ["argon2id", "pbkdf2-sha256"])
def test_flujo_completo_guardar_y_recuperar(tmp_path, alg):
    path = tmp_path / "vault.json"
    with _new_vault(FileStorage(path), alg) as v:
        entry_id = v.add_entry("gmail.com", "ana@gmail.com", SECRET, notes="2FA activo")

    # Proceso nuevo: solo con la contraseña maestra se recupera el secreto.
    with Vault.open(FileStorage(path), MASTER) as v:
        e = v.get_entry(entry_id)
        assert (e["site"], e["username"], e["password"], e["notes"]) == \
               ("gmail.com", "ana@gmail.com", SECRET, "2FA activo")
        assert v.find("gmail")[0]["password"] == SECRET


def test_conocimiento_cero_nada_en_claro_en_disco(tmp_path):
    path = tmp_path / "vault.json"
    with _new_vault(FileStorage(path)) as v:
        v.add_entry("banco-secreto.com", "usuario_privado", SECRET, notes="nota íntima")

    raw = path.read_bytes()
    for leak in (MASTER, SECRET, "banco-secreto", "usuario_privado", "nota"):
        assert leak.encode() not in raw
    doc = json.loads(raw)
    assert set(doc) == {"format", "version", "vault_id", "kdf", "wrapped_key", "entries"}
    assert "hash" not in json.dumps(doc["kdf"])  # no se guarda hash de la contraseña


def test_password_maestra_incorrecta():
    storage = MemoryStorage()
    _new_vault(storage).lock()
    with pytest.raises(InvalidPasswordError):
        Vault.open(storage, MASTER + "x")


def test_manipular_parametros_kdf_impide_abrir():
    storage = MemoryStorage()
    _new_vault(storage)
    doc = json.loads(storage.read())
    doc["kdf"]["time_cost"] = 2  # cambio "válido" pero no autenticado por el usuario
    storage.write(json.dumps(doc).encode())
    with pytest.raises(InvalidPasswordError):
        Vault.open(storage, MASTER)


def test_parametros_degradados_rechazados():
    storage = MemoryStorage()
    _new_vault(storage)
    doc = json.loads(storage.read())
    doc["kdf"]["memory_cost"] = 16
    storage.write(json.dumps(doc).encode())
    with pytest.raises(WeakParametersError):
        Vault.open(storage, MASTER)


def test_entrada_manipulada_detectada():
    storage = MemoryStorage()
    v = _new_vault(storage)
    entry_id = v.add_entry("a.com", "u", SECRET)
    doc = json.loads(storage.read())
    blob = bytearray(base64.b64decode(doc["entries"][entry_id]))
    blob[20] ^= 0x01
    doc["entries"][entry_id] = base64.b64encode(blob).decode()
    storage.write(json.dumps(doc).encode())

    v2 = Vault.open(storage, MASTER)
    with pytest.raises(IntegrityError):
        v2.get_entry(entry_id)


def test_intercambiar_ciphertexts_entre_entradas_detectado():
    storage = MemoryStorage()
    v = _new_vault(storage)
    id_a = v.add_entry("a.com", "u", "pw-a")
    id_b = v.add_entry("b.com", "u", "pw-b")
    doc = json.loads(storage.read())
    doc["entries"][id_a], doc["entries"][id_b] = doc["entries"][id_b], doc["entries"][id_a]
    storage.write(json.dumps(doc).encode())

    v2 = Vault.open(storage, MASTER)
    for entry_id in (id_a, id_b):
        with pytest.raises(IntegrityError):
            v2.get_entry(entry_id)


def test_cambio_de_password_maestra():
    storage = MemoryStorage()
    v = _new_vault(storage)
    entry_id = v.add_entry("a.com", "u", SECRET)
    old_salt = json.loads(storage.read())["kdf"]["salt"]
    v.change_master_password("Otra-Contraseña-Maestra-99")

    assert json.loads(storage.read())["kdf"]["salt"] != old_salt  # sal renovada
    with pytest.raises(InvalidPasswordError):
        Vault.open(storage, MASTER)
    assert Vault.open(storage, "Otra-Contraseña-Maestra-99").get_entry(entry_id)["password"] == SECRET


def test_actualizar_borrar_listar_y_bloquear():
    storage = MemoryStorage()
    v = _new_vault(storage)
    id_b = v.add_entry("b.com", "u2", "x")
    id_a = v.add_entry("a.com", "u1", "y")
    assert [e["site"] for e in v.list_entries()] == ["a.com", "b.com"]
    assert "password" not in v.list_entries()[0]

    v.update_entry(id_a, password="nueva")
    assert Vault.open(storage, MASTER).get_entry(id_a)["password"] == "nueva"

    v.delete_entry(id_b)
    with pytest.raises(EntryNotFoundError):
        v.get_entry(id_b)

    v.lock()
    with pytest.raises(RuntimeError):
        v.get_entry(id_a)


def test_no_sobrescribe_boveda_existente():
    storage = MemoryStorage()
    _new_vault(storage)
    with pytest.raises(FileExistsError):
        _new_vault(storage)

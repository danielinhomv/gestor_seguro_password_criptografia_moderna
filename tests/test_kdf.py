import hashlib

import pytest
from conftest import FAST_ARGON2, FAST_PBKDF2

from gestor.errors import WeakParametersError
from gestor.kdf import (ARGON2ID, PBKDF2_SHA256, SALT_LEN, KdfParams, derive_master_key,
                        derive_subkeys, generate_salt)


def test_salt_es_aleatoria_y_de_128_bits():
    salts = {generate_salt() for _ in range(1000)}
    assert len(salts) == 1000
    assert all(len(s) == SALT_LEN for s in salts)


def test_salt_corta_rechazada():
    with pytest.raises(WeakParametersError):
        generate_salt(8)


@pytest.mark.parametrize("alg,extra", [(ARGON2ID, FAST_ARGON2), (PBKDF2_SHA256, FAST_PBKDF2)])
def test_derivacion_determinista_y_dependiente_de_la_sal(alg, extra):
    p1 = KdfParams.new(alg, **extra)
    p2 = KdfParams.new(alg, **extra)  # otra sal
    k1 = derive_master_key("correct horse battery staple", p1)
    assert len(k1) == 32
    assert k1 == derive_master_key("correct horse battery staple", p1)
    assert k1 != derive_master_key("correct horse battery staple", p2)
    assert k1 != derive_master_key("correct horse battery stapl3", p1)


def test_pbkdf2_coincide_con_hashlib():
    p = KdfParams.new(PBKDF2_SHA256, **FAST_PBKDF2)
    expected = hashlib.pbkdf2_hmac("sha256", b"secreto", p.salt, p.iterations, 32)
    assert derive_master_key("secreto", p) == expected


def test_normalizacion_unicode():
    p = KdfParams.new(ARGON2ID, **FAST_ARGON2)
    assert derive_master_key("contraseña", p) == derive_master_key("contraseña", p)


def test_subclaves_independientes_y_separadas_por_dominio():
    master = bytes(range(32))
    enc, mac = derive_subkeys(master, b"a")
    enc2, mac2 = derive_subkeys(master, b"b")
    assert len(enc) == len(mac) == 32
    assert enc != mac
    assert (enc, mac) != (enc2, mac2)


def test_params_roundtrip_y_rechazo_de_parametros_debiles():
    p = KdfParams.new(ARGON2ID, **FAST_ARGON2)
    assert KdfParams.from_dict(p.to_dict()) == p
    weak = p.to_dict() | {"memory_cost": 64}
    with pytest.raises(WeakParametersError):
        KdfParams.from_dict(weak)
    with pytest.raises(WeakParametersError):
        KdfParams.new(PBKDF2_SHA256, iterations=1000)


def test_password_vacia_rechazada():
    with pytest.raises(ValueError):
        derive_master_key("", KdfParams.new(ARGON2ID, **FAST_ARGON2))

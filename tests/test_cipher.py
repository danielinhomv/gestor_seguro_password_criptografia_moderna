import os
from unittest import mock

import pytest

from gestor import cipher
from gestor.errors import IntegrityError

ENC = os.urandom(32)
MAC = os.urandom(32)


@pytest.mark.parametrize("msg", [b"", b"a", b"x" * 15, b"x" * 16, b"x" * 1000,
                                 "contraseña ñ 🔐".encode()])
def test_roundtrip(msg):
    blob = cipher.encrypt(ENC, MAC, msg, b"ad")
    assert cipher.decrypt(ENC, MAC, blob, b"ad") == msg


def test_iv_aleatorio_produce_ciphertexts_distintos():
    a = cipher.encrypt(ENC, MAC, b"mismo mensaje")
    b = cipher.encrypt(ENC, MAC, b"mismo mensaje")
    assert a != b
    assert a[1:17] != b[1:17]  # IVs distintos


def test_cualquier_bit_modificado_es_detectado():
    blob = cipher.encrypt(ENC, MAC, b"secreto importante", b"ad")
    for i in range(len(blob)):
        for bit in (0x01, 0x80):
            tampered = bytearray(blob)
            tampered[i] ^= bit
            with pytest.raises(IntegrityError):
                cipher.decrypt(ENC, MAC, bytes(tampered), b"ad")


@pytest.mark.parametrize("cut", [1, 16, 32, 48])
def test_truncado_detectado(cut):
    blob = cipher.encrypt(ENC, MAC, b"secreto" * 10)
    with pytest.raises(IntegrityError):
        cipher.decrypt(ENC, MAC, blob[:-cut])


def test_ad_distinta_o_clave_incorrecta_fallan():
    blob = cipher.encrypt(ENC, MAC, b"secreto", b"entrada-1")
    with pytest.raises(IntegrityError):
        cipher.decrypt(ENC, MAC, blob, b"entrada-2")
    with pytest.raises(IntegrityError):
        cipher.decrypt(ENC, os.urandom(32), blob, b"entrada-1")
    with pytest.raises(IntegrityError):
        cipher.decrypt(os.urandom(32), os.urandom(32), blob, b"entrada-1")


def test_mac_se_verifica_antes_de_descifrar():
    """Encrypt-then-MAC: con un MAC inválido AES nunca llega a ejecutarse
    (no hay oráculo de padding posible)."""
    blob = bytearray(cipher.encrypt(ENC, MAC, b"secreto"))
    blob[-40] ^= 0xFF  # altera el último bloque del ciphertext (zona del padding)
    with mock.patch.object(cipher, "Cipher", wraps=cipher.Cipher) as spy:
        with pytest.raises(IntegrityError):
            cipher.decrypt(ENC, MAC, bytes(blob))
        spy.assert_not_called()


def test_claves_invalidas_rechazadas():
    with pytest.raises(ValueError):
        cipher.encrypt(b"corta", MAC, b"x")
    with pytest.raises(ValueError):
        cipher.encrypt(ENC, ENC, b"x")  # misma clave para AES y HMAC

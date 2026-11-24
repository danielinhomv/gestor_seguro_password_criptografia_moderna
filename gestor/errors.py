"""Excepciones del gestor.

Los mensajes son deliberadamente genéricos: no deben revelar *por qué* falló
una verificación criptográfica (evita convertir el error en un oráculo).
"""


class GestorError(Exception):
    """Error base del gestor."""


class IntegrityError(GestorError):
    """El HMAC no coincide: datos manipulados, clave incorrecta o AD distinta."""


class InvalidPasswordError(GestorError):
    """Contraseña maestra incorrecta (o cabecera de la bóveda manipulada)."""


class VaultFormatError(GestorError):
    """El archivo de la bóveda no tiene un formato válido."""


class WeakParametersError(GestorError):
    """Parámetros de KDF por debajo del mínimo de seguridad aceptado."""


class EntryNotFoundError(GestorError, KeyError):
    """No existe una entrada con ese identificador."""

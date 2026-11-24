"""Backends de almacenamiento.

El almacenamiento solo recibe bytes ya cifrados/autenticados: es "tonto" a
propósito. Eso permite sustituir el archivo local por un servidor remoto, S3,
una base de datos, etc. (bóveda distribuida) sin cambiar la criptografía y sin
que ese backend aprenda nada (conocimiento cero).
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    def exists(self) -> bool: ...

    @abstractmethod
    def read(self) -> bytes: ...

    @abstractmethod
    def write(self, data: bytes) -> None: ...


class FileStorage(StorageBackend):
    """Archivo local con escritura atómica (archivo temporal + os.replace)."""

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)

    def exists(self) -> bool:
        return self.path.exists()

    def read(self) -> bytes:
        return self.path.read_bytes()

    def write(self, data: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self.path)  # atómico: nunca queda una bóveda a medio escribir


class MemoryStorage(StorageBackend):
    """Backend en memoria (tests / simulación de un servidor remoto)."""

    def __init__(self) -> None:
        self.data: bytes | None = None

    def exists(self) -> bool:
        return self.data is not None

    def read(self) -> bytes:
        if self.data is None:
            raise FileNotFoundError("Bóveda vacía")
        return self.data

    def write(self, data: bytes) -> None:
        self.data = bytes(data)

# app/models/__init__.py

from .credor import Credor
from .precatorio import Precatorio
from .documento_pessoal import DocumentoPessoal
from .certidao import Certidao

__all__ = [
    "Credor",
    "Precatorio",
    "DocumentoPessoal",
    "Certidao"
]

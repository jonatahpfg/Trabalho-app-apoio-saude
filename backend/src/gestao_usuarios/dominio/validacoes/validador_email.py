"""Validação das regras de negócio do e-mail."""

from __future__ import annotations

import re

from ..erros import ErroDeValidacao
from .validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)

_FORMATO_EMAIL = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


class ValidadorEmail:
    """Valida e normaliza o endereço de e-mail do usuário."""

    @staticmethod
    def validar(email: str) -> str:
        """Devolve um e-mail válido ou lança ``ErroDeValidacao``."""
        email = ValidadorTextoObrigatorio.validar(
            email,
            "email",
        )

        if not _FORMATO_EMAIL.match(email):
            raise ErroDeValidacao(
                f"E-mail inválido: {email!r}"
            )

        return email
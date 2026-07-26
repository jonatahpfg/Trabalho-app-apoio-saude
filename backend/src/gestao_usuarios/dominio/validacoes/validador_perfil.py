"""Validação de valores baseados em Enum."""

from __future__ import annotations

from enum import Enum
from typing import TypeVar

from ..erros import ErroDeValidacao

TPerfil = TypeVar(
    "TPerfil",
    bound=Enum,
)


class ValidadorPerfil:
    """Valida e converte o perfil informado para seu Enum correspondente."""

    @staticmethod
    def validar(
        perfil: TPerfil | str,
        tipo_perfil: type[TPerfil],
    ) -> TPerfil:
        """Devolve o perfil convertido para o Enum informado.

        O tipo do Enum é recebido como argumento para evitar dependência
        circular entre o validador e a entidade Usuario.
        """
        if isinstance(perfil, tipo_perfil):
            return perfil

        try:
            return tipo_perfil(perfil)

        except (ValueError, TypeError) as erro:
            raise ErroDeValidacao(
                f"Perfil inválido: {perfil!r}"
            ) from erro
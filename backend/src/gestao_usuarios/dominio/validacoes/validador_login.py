"""Validação das regras de negócio do login."""

from __future__ import annotations

from ..erros import ErroDeValidacao
from .validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)

TAMANHO_MAXIMO_LOGIN = 12


class ValidadorLogin:
    """Valida o login utilizado para autenticação no sistema."""

    @staticmethod
    def validar(login: str) -> str:
        """Devolve um login válido e normalizado.

        Regras (Laboratório 2 — tratamento de erros):
        - o login é obrigatório;
        - espaços nas extremidades são removidos;
        - deve possuir no máximo 12 caracteres;
        - não pode conter números.
        """
        login = ValidadorTextoObrigatorio.validar(
            login,
            "login",
        )

        if len(login) > TAMANHO_MAXIMO_LOGIN:
            raise ErroDeValidacao(
                "O login deve possuir no máximo "
                f"{TAMANHO_MAXIMO_LOGIN} caracteres."
            )

        if any(
            caractere.isdigit()
            for caractere in login
        ):
            raise ErroDeValidacao(
                "O login não pode conter números."
            )

        return login
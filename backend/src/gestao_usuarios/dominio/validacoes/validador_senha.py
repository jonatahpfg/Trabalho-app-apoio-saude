"""Validação das regras de força da senha."""

from __future__ import annotations

from ..erros import ErroDeValidacao
from .validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)

TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128

_CARACTERES_ESPECIAIS_SENHA = set(
    "!@#$%^&*()_+-=[]{}|'"
)


class ValidadorSenha:
    """Valida as regras de segurança aplicadas à senha do usuário."""

    @staticmethod
    def validar(
        senha: str,
        *,
        nome: str,
        email: str,
    ) -> str:
        """Devolve a senha validada ou lança ``ErroDeValidacao``.

        Regras:
        - campo obrigatório;
        - entre 8 e 128 caracteres;
        - não pode ser igual ao nome;
        - não pode ser igual ao e-mail;
        - deve possuir pelo menos 3 dos 4 grupos:
          maiúsculas, minúsculas, números e caracteres especiais.
        """
        senha = ValidadorTextoObrigatorio.validar(
            senha,
            "senha",
        )

        if (
            len(senha) < TAMANHO_MINIMO_SENHA
            or len(senha) > TAMANHO_MAXIMO_SENHA
        ):
            raise ErroDeValidacao(
                "A senha deve ter entre "
                f"{TAMANHO_MINIMO_SENHA} e "
                f"{TAMANHO_MAXIMO_SENHA} caracteres."
            )

        if senha == nome or senha == email:
            raise ErroDeValidacao(
                "A senha não pode ser igual ao nome ou e-mail."
            )

        tipos_presentes = 0

        if any(
            caractere.isupper()
            for caractere in senha
        ):
            tipos_presentes += 1

        if any(
            caractere.islower()
            for caractere in senha
        ):
            tipos_presentes += 1

        if any(
            caractere.isdigit()
            for caractere in senha
        ):
            tipos_presentes += 1

        if any(
            caractere in _CARACTERES_ESPECIAIS_SENHA
            for caractere in senha
        ):
            tipos_presentes += 1

        if tipos_presentes < 3:
            raise ErroDeValidacao(
                "A senha deve conter no mínimo 3 dos 4 tipos: "
                "maiúsculas, minúsculas, números e caracteres "
                "especiais permitidos."
            )

        return senha
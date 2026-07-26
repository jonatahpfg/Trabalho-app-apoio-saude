"""Validação de campos textuais obrigatórios."""

from __future__ import annotations

from ..erros import ErroDeValidacao


class ValidadorTextoObrigatorio:
    """Valida e normaliza campos textuais obrigatórios."""

    @staticmethod
    def validar(
        valor: str,
        campo: str,
    ) -> str:
        """Devolve o texto normalizado ou lança ``ErroDeValidacao``.

        Espaços no início e no final são removidos antes de devolver
        o valor validado.
        """
        if valor is None or not str(valor).strip():
            raise ErroDeValidacao(
                f"Campo obrigatório ausente: {campo}"
            )

        return str(valor).strip()
"""Entidade UnidadeBasicaSaude — domínio do gerenciamento de unidades."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .erros import ErroDeValidacao

_APENAS_DIGITOS = re.compile(r"\D")


@dataclass
class UnidadeBasicaSaude:
    """Unidade Básica de Saúde. Use ``criar`` para garantir as invariantes."""

    nome: str
    cnpj: str
    endereco: str
    telefone: str
    ativa: bool = True
    id: int | None = None

    @classmethod
    def criar(
        cls,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        """Cria uma UBS válida ou lança ``ErroDeValidacao``."""
        nome = _texto_obrigatorio(nome, "nome")
        cnpj = _cnpj_valido(cnpj)
        endereco = _texto_obrigatorio(endereco, "endereco")
        telefone = _texto_obrigatorio(telefone, "telefone")

        return cls(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )


def _texto_obrigatorio(valor: str, campo: str) -> str:
    if valor is None or not str(valor).strip():
        raise ErroDeValidacao(f"Campo obrigatório ausente: {campo}")
    return str(valor).strip()


def _cnpj_valido(cnpj: str) -> str:
    cnpj = _texto_obrigatorio(cnpj, "cnpj")
    cnpj = _APENAS_DIGITOS.sub("", cnpj)

    if len(cnpj) != 14:
        raise ErroDeValidacao("CNPJ deve conter 14 dígitos.")

    if cnpj == cnpj[0] * 14:
        raise ErroDeValidacao("CNPJ inválido.")

    return cnpj

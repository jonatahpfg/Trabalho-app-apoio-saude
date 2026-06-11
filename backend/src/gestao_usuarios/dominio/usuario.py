"""Entidade Usuario e o enum Perfil — o núcleo do domínio."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .erros import ErroDeValidacao

_FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Perfil(str, Enum):
    """Perfil de acesso do usuário (RF03)."""

    ADMINISTRADOR = "ADMINISTRADOR"
    GESTOR = "GESTOR"
    MEDICO = "MEDICO"


@dataclass
class Usuario:
    """Usuário do sistema. Use ``Usuario.criar`` para garantir as invariantes."""

    nome: str
    cpf: str
    email: str
    telefone: str
    perfil: Perfil
    ativo: bool = True
    id: int | None = None

    @classmethod
    def criar(
        cls,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Cria um usuário válido ou lança ``ErroDeValidacao``."""
        nome = _texto_obrigatorio(nome, "nome")
        cpf = _texto_obrigatorio(cpf, "cpf")
        email = _texto_obrigatorio(email, "email")
        telefone = _texto_obrigatorio(telefone, "telefone")

        if not _FORMATO_EMAIL.match(email):
            raise ErroDeValidacao(f"E-mail inválido: {email!r}")

        return cls(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            perfil=_perfil_valido(perfil),
        )


def _texto_obrigatorio(valor: str, campo: str) -> str:
    if valor is None or not str(valor).strip():
        raise ErroDeValidacao(f"Campo obrigatório ausente: {campo}")
    return str(valor).strip()


def _perfil_valido(perfil: Perfil | str) -> Perfil:
    try:
        return perfil if isinstance(perfil, Perfil) else Perfil(perfil)
    except ValueError as erro:
        raise ErroDeValidacao(f"Perfil inválido: {perfil!r}") from erro

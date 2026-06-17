"""Entidade Usuario e o enum Perfil — o núcleo do domínio."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .erros import ErroDeValidacao

_FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
_CARACTERES_ESPECIAIS_SENHA = set("!@#$%^&*()_+-=[]{}|'")


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
    senha: str
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
        senha: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Cria um usuário válido ou lança ``ErroDeValidacao``."""
        nome = _texto_obrigatorio(nome, "nome")
        cpf = _texto_obrigatorio(cpf, "cpf")
        email = _texto_obrigatorio(email, "email")
        telefone = _texto_obrigatorio(telefone, "telefone")
        senha = _texto_obrigatorio(senha, "senha")

        if not _FORMATO_EMAIL.match(email):
            raise ErroDeValidacao(f"E-mail inválido: {email!r}")

        _validar_senha(senha, nome, email)

        return cls(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            senha=senha,
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


def _validar_senha(senha: str, nome: str, email: str) -> None:
    if len(senha) < TAMANHO_MINIMO_SENHA or len(senha) > TAMANHO_MAXIMO_SENHA:
        raise ErroDeValidacao(
            f"A senha deve ter entre {TAMANHO_MINIMO_SENHA} e {TAMANHO_MAXIMO_SENHA} caracteres."
        )

    if senha == nome or senha == email:
        raise ErroDeValidacao("A senha não pode ser igual ao nome ou e-mail.")

    tipos_presentes = 0
    if any(c.isupper() for c in senha):
        tipos_presentes += 1
    if any(c.islower() for c in senha):
        tipos_presentes += 1
    if any(c.isdigit() for c in senha):
        tipos_presentes += 1
    if any(c in _CARACTERES_ESPECIAIS_SENHA for c in senha):
        tipos_presentes += 1

    if tipos_presentes < 3:
        raise ErroDeValidacao(
            "A senha deve conter no mínimo 3 dos 4 tipos: maiúsculas, "
            "minúsculas, números e caracteres especiais permitidos."
        )

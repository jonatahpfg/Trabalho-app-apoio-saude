"""Entidade Usuario e o enum Perfil — o núcleo do domínio."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .senha import gerar_hash
from .validacoes.validador_email import ValidadorEmail
from .validacoes.validador_login import ValidadorLogin
from .validacoes.validador_perfil import ValidadorPerfil
from .validacoes.validador_senha import ValidadorSenha
from .validacoes.validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)


class Perfil(str, Enum):
    """Perfil de acesso do usuário (RF03)."""

    ADMINISTRADOR = "ADMINISTRADOR"
    GESTOR = "GESTOR"
    MEDICO = "MEDICO"


@dataclass
class Usuario:
    """Usuário do sistema.

    Use ``Usuario.criar`` para garantir as invariantes.
    """

    nome: str
    cpf: str
    email: str
    telefone: str
    login: str
    senha_hash: str
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
        login: str,
        senha: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Cria um usuário válido ou lança ``ErroDeValidacao``.

        As regras de validação são delegadas para classes específicas,
        reduzindo o acoplamento da entidade e facilitando a manutenção
        e a evolução das regras de negócio.

        O login é obrigatório e deve possuir no máximo 12 caracteres.

        A senha é validada em texto puro e armazenada apenas como hash.
        A entidade nunca armazena a senha original.
        """
        nome = ValidadorTextoObrigatorio.validar(
            nome,
            "nome",
        )

        cpf = ValidadorTextoObrigatorio.validar(
            cpf,
            "cpf",
        )

        email = ValidadorEmail.validar(
            email,
        )

        telefone = ValidadorTextoObrigatorio.validar(
            telefone,
            "telefone",
        )

        login = ValidadorLogin.validar(
            login,
        )

        senha = ValidadorSenha.validar(
            senha,
            nome=nome,
            email=email,
        )

        perfil = ValidadorPerfil.validar(
            perfil,
            Perfil,
        )

        return cls(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            senha_hash=gerar_hash(senha),
            perfil=perfil,
        )
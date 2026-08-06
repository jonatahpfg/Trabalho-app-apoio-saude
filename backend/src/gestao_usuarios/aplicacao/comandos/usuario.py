"""Comandos concretos para operações com Usuários."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...dominio.usuario import Perfil, Usuario
from .base import Comando

if TYPE_CHECKING:
    from ..gerenciador_de_usuarios import GerenciadorDeUsuarios


class ComandoAdicionarUsuario(Comando):
    """Comando concreto para cadastrar um novo usuário no sistema."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        senha: str,
        perfil: Perfil | str,
    ) -> None:
        self._gerenciador = gerenciador
        self._nome = nome
        self._cpf = cpf
        self._email = email
        self._telefone = telefone
        self._login = login
        self._senha = senha
        self._perfil = perfil

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def email(self) -> str:
        return self._email

    @property
    def telefone(self) -> str:
        return self._telefone

    @property
    def login(self) -> str:
        return self._login

    @property
    def perfil(self) -> Perfil | str:
        return self._perfil

    def executar(self) -> Usuario:
        return self._gerenciador.adicionar_usuario(
            nome=self._nome,
            cpf=self._cpf,
            email=self._email,
            telefone=self._telefone,
            login=self._login,
            senha=self._senha,
            perfil=self._perfil,
        )


class ComandoListarUsuarios(Comando):
    """Comando concreto para listar todos os usuários cadastrados."""

    def __init__(self, gerenciador: GerenciadorDeUsuarios) -> None:
        self._gerenciador = gerenciador

    def executar(self) -> list[Usuario]:
        return self._gerenciador.listar_usuarios()


class ComandoAutenticarUsuario(Comando):
    """Comando concreto para autenticar um usuário com login e senha."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        *,
        login: str,
        senha: str,
    ) -> None:
        self._gerenciador = gerenciador
        self._login = login
        self._senha = senha

    @property
    def login(self) -> str:
        return self._login

    def executar(self) -> Usuario:
        return self._gerenciador.autenticar(
            login=self._login,
            senha=self._senha,
        )


# Alias para maior flexibilidade
ComandoAutenticar = ComandoAutenticarUsuario

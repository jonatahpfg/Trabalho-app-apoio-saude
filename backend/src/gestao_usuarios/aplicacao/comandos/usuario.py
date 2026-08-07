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
    """Comando concreto para listar os usuários cadastrados."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        *,
        apenas_ativos: bool = False,
    ) -> None:
        self._gerenciador = gerenciador
        self._apenas_ativos = apenas_ativos

    @property
    def apenas_ativos(self) -> bool:
        return self._apenas_ativos

    def executar(self) -> list[Usuario]:
        return self._gerenciador.listar_usuarios(
            apenas_ativos=self._apenas_ativos
        )


class ComandoBuscarUsuarioPorId(Comando):
    """Comando concreto para buscar um usuário pelo seu identificador único."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        usuario_id: int,
    ) -> None:
        self._gerenciador = gerenciador
        self._usuario_id = usuario_id

    @property
    def usuario_id(self) -> int:
        return self._usuario_id

    def executar(self) -> Usuario:
        return self._gerenciador.buscar_usuario_por_id(
            self._usuario_id
        )


class ComandoBuscarUsuarioPorLogin(Comando):
    """Comando concreto para buscar um usuário pelo seu login."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        login: str,
    ) -> None:
        self._gerenciador = gerenciador
        self._login = login

    @property
    def login(self) -> str:
        return self._login

    def executar(self) -> Usuario:
        return self._gerenciador.buscar_usuario_por_login(
            self._login
        )


class ComandoAtualizarUsuario(Comando):
    """Comando concreto para atualizar os dados de um usuário existente."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        *,
        usuario_id: int,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        perfil: Perfil | str,
        senha: str | None = None,
    ) -> None:
        self._gerenciador = gerenciador
        self._usuario_id = usuario_id
        self._nome = nome
        self._cpf = cpf
        self._email = email
        self._telefone = telefone
        self._login = login
        self._perfil = perfil
        self._senha = senha

    @property
    def usuario_id(self) -> int:
        return self._usuario_id

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

    @property
    def altera_senha(self) -> bool:
        """Indica se o comando também redefine a senha do usuário."""
        return self._senha is not None

    def executar(self) -> Usuario:
        return self._gerenciador.atualizar_usuario(
            usuario_id=self._usuario_id,
            nome=self._nome,
            cpf=self._cpf,
            email=self._email,
            telefone=self._telefone,
            login=self._login,
            perfil=self._perfil,
            senha=self._senha,
        )


class ComandoDesativarUsuario(Comando):
    """Comando concreto para desativar logicamente um usuário (soft delete)."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        usuario_id: int,
    ) -> None:
        self._gerenciador = gerenciador
        self._usuario_id = usuario_id

    @property
    def usuario_id(self) -> int:
        return self._usuario_id

    def executar(self) -> Usuario:
        return self._gerenciador.desativar_usuario(
            self._usuario_id
        )


class ComandoReativarUsuario(Comando):
    """Comando concreto para reativar um usuário previamente desativado."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
        usuario_id: int,
    ) -> None:
        self._gerenciador = gerenciador
        self._usuario_id = usuario_id

    @property
    def usuario_id(self) -> int:
        return self._usuario_id

    def executar(self) -> Usuario:
        return self._gerenciador.reativar_usuario(
            self._usuario_id
        )


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

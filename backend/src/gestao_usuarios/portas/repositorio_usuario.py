"""Porta secundária de persistência de usuários."""

from __future__ import annotations

from typing import Protocol

from ..dominio.usuario import Usuario


class RepositorioUsuario(Protocol):
    """Contrato de persistência. O núcleo depende desta interface, não de uma implementação."""

    def salvar(self, usuario: Usuario) -> Usuario:
        """Persiste o usuário, atribuindo um id se ainda não tiver, e o devolve."""
        ...

    def buscar_todos(self) -> list[Usuario]:
        """Devolve todos os usuários cadastrados."""
        ...

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        """Devolve o usuário com o CPF informado, ou ``None`` se não existir."""
        ...

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Devolve o usuário com o e-mail informado, ou ``None`` se não existir."""
        ...

    def buscar_por_login(self, login: str) -> Usuario | None:
        """Devolve o usuário com o login informado, ou ``None`` se não existir."""
        ...
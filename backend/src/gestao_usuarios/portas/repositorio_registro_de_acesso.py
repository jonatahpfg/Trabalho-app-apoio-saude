"""Porta secundária de persistência dos registros de acesso."""

from __future__ import annotations

from typing import Protocol

from ..dominio.registro_de_acesso import RegistroDeAcesso


class RepositorioRegistroDeAcesso(Protocol):
    """Contrato de persistência dos eventos de login. O núcleo depende desta interface, não de uma implementação."""

    def salvar(self, registro: RegistroDeAcesso) -> RegistroDeAcesso:
        """Persiste o registro, atribuindo um id se ainda não tiver, e o devolve."""
        ...

    def buscar_todos(self) -> list[RegistroDeAcesso]:
        """Devolve todos os registros de acesso, na ordem em que foram salvos."""
        ...

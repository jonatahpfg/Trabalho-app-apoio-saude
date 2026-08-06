"""Comandos para operações do sistema como um todo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Comando

if TYPE_CHECKING:
    from ..gerenciador_de_unidades import GerenciadorDeUnidades
    from ..gerenciador_de_usuarios import GerenciadorDeUsuarios


class ComandoContarTotalEntidades(Comando):
    """Comando concreto para calcular a quantidade total de entidades cadastradas."""

    def __init__(
        self,
        gerenciador_usuarios: GerenciadorDeUsuarios,
        gerenciador_unidades: GerenciadorDeUnidades,
    ) -> None:
        self._gerenciador_usuarios = gerenciador_usuarios
        self._gerenciador_unidades = gerenciador_unidades

    def executar(self) -> int:
        total_usuarios = len(self._gerenciador_usuarios.listar_usuarios())
        total_unidades = len(self._gerenciador_unidades.listar_unidades())
        return total_usuarios + total_unidades

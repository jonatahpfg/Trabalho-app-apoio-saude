"""Subpacote de comandos que implementa o padrão GoF Command."""

from .base import Comando
from .executor import ExecutorDeComandos
from .sistema import ComandoContarTotalEntidades
from .unidade import (
    ComandoAdicionarUnidade,
    ComandoAtualizarUnidade,
    ComandoBuscarUnidadePorId,
    ComandoListarUnidades,
    ComandoRemoverUnidade,
)
from .usuario import (
    ComandoAdicionarUsuario,
    ComandoAutenticar,
    ComandoAutenticarUsuario,
    ComandoListarUsuarios,
)

__all__ = [
    "Comando",
    "ExecutorDeComandos",
    "ComandoAdicionarUsuario",
    "ComandoListarUsuarios",
    "ComandoAutenticarUsuario",
    "ComandoAutenticar",
    "ComandoAdicionarUnidade",
    "ComandoListarUnidades",
    "ComandoBuscarUnidadePorId",
    "ComandoAtualizarUnidade",
    "ComandoRemoverUnidade",
    "ComandoContarTotalEntidades",
]

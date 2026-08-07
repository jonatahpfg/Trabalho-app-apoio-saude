"""Subpacote de comandos que implementa o padrão GoF Command."""

from .base import Comando
from .executor import ExecutorDeComandos
from .sistema import ComandoContarTotalEntidades
from .unidade import (
    ComandoAdicionarUnidade,
    ComandoAtualizarUnidade,
    ComandoBuscarUnidadePorId,
    ComandoDesfazerAtualizacaoDeUnidade,
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
    "ComandoAdicionarUnidade",
    "ComandoAdicionarUsuario",
    "ComandoAtualizarUnidade",
    "ComandoAutenticar",
    "ComandoAutenticarUsuario",
    "ComandoBuscarUnidadePorId",
    "ComandoContarTotalEntidades",
    "ComandoDesfazerAtualizacaoDeUnidade",
    "ComandoListarUnidades",
    "ComandoListarUsuarios",
    "ComandoRemoverUnidade",
    "ExecutorDeComandos",
]
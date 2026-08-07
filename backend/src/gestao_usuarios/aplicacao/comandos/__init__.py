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
    ComandoAtualizarUsuario,
    ComandoAutenticar,
    ComandoAutenticarUsuario,
    ComandoBuscarUsuarioPorId,
    ComandoBuscarUsuarioPorLogin,
    ComandoDesativarUsuario,
    ComandoListarUsuarios,
    ComandoReativarUsuario,
)

__all__ = [
    "Comando",
    "ComandoAdicionarUnidade",
    "ComandoAdicionarUsuario",
    "ComandoAtualizarUnidade",
    "ComandoAtualizarUsuario",
    "ComandoAutenticar",
    "ComandoAutenticarUsuario",
    "ComandoBuscarUnidadePorId",
    "ComandoBuscarUsuarioPorId",
    "ComandoBuscarUsuarioPorLogin",
    "ComandoContarTotalEntidades",
    "ComandoDesativarUsuario",
    "ComandoDesfazerAtualizacaoDeUnidade",
    "ComandoListarUnidades",
    "ComandoListarUsuarios",
    "ComandoReativarUsuario",
    "ComandoRemoverUnidade",
    "ExecutorDeComandos",
]
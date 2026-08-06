"""Executor (Invoker) para o padrão GoF Command.

Centraliza o disparo de comandos da camada de aplicação e mantém um
histórico das operações executadas.
"""

from __future__ import annotations

from typing import Any

from .base import Comando


class ExecutorDeComandos:
    """Invoker / Executor responsável por executar comandos e registrar o histórico."""

    def __init__(self) -> None:
        self._historico: list[Comando] = []

    def executar(self, comando: Comando) -> Any:
        """Executa o comando fornecido e registra-o no histórico."""
        if not isinstance(comando, Comando):
            raise TypeError(
                f"Objeto fornecido não é uma instância de Comando: {type(comando).__name__}"
            )

        resultado = comando.executar()
        self._historico.append(comando)
        return resultado

    @property
    def historico(self) -> list[Comando]:
        """Retorna uma cópia da lista de comandos já executados."""
        return list(self._historico)

    @property
    def ultimo_comando(self) -> Comando | None:
        """Retorna o último comando executado, ou None se nenhum comando foi executado."""
        return self._historico[-1] if self._historico else None

    def limpar_historico(self) -> None:
        """Limpa o histórico de comandos executados."""
        self._historico.clear()

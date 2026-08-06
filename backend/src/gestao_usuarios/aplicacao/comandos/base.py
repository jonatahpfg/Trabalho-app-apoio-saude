"""Interface abstrata base para o padrão GoF Command.

O padrão Command encapsula uma requisição como um objeto, permitindo
parametrizar clientes com diferentes requisições, enfileirar ou registrar
operações e suportar operações reversíveis quando aplicável.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Comando(ABC):
    """Interface abstrata para comandos executáveis da camada de aplicação."""

    @abstractmethod
    def executar(self) -> Any:
        """Executa a operação encapsulada pelo comando."""
        raise NotImplementedError

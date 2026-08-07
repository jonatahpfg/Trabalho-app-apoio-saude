"""Interface abstrata do Observer — padrão GoF Observer (Sprint 6).

Todo observador concreto deve implementar ``atualizar`` para receber
notificações do publicador de eventos de autenticação.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .evento import EventoDeAutenticacao


class ObservadorDeAutenticacao(ABC):
    """Interface abstrata para observadores de eventos de autenticação.

    Participante Observer do padrão GoF Observer.
    """

    @abstractmethod
    def atualizar(self, evento: EventoDeAutenticacao) -> None:
        """Recebe e processa um evento de autenticação publicado.

        Args:
            evento: objeto com os dados da tentativa de autenticação.
        """
        raise NotImplementedError

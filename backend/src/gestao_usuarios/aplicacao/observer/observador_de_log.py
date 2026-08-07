"""Observador concreto de log — padrão GoF Observer (Sprint 6).

Registra cada evento de autenticação em memória e permite recuperar
o histórico completo de tentativas de login.
"""

from __future__ import annotations

from .evento import EventoDeAutenticacao
from .observador import ObservadorDeAutenticacao


class ObservadorDeLogDeAutenticacao(ObservadorDeAutenticacao):
    """Observador concreto que registra eventos de autenticação.

    Mantém um histórico interno de todos os eventos recebidos e
    disponibiliza-os para consulta. Também imprime cada evento no
    console para fins de demonstração.
    """

    def __init__(self) -> None:
        self._historico: list[EventoDeAutenticacao] = []

    def atualizar(self, evento: EventoDeAutenticacao) -> None:
        """Registra o evento no histórico e imprime-o no console."""
        self._historico.append(evento)
        status = "SUCESSO" if evento.sucesso else "FALHA"
        print(
            f"[LOG-AUTH] {evento.data_hora.strftime('%Y-%m-%d %H:%M:%S')} "
            f"| login='{evento.login}' | {status}"
        )

    @property
    def historico(self) -> list[EventoDeAutenticacao]:
        """Retorna uma cópia do histórico de eventos registrados."""
        return list(self._historico)

    def limpar(self) -> None:
        """Limpa o histórico de eventos."""
        self._historico.clear()

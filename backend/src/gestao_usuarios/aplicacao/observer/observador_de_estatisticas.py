"""Observador concreto de estatísticas — padrão GoF Observer (Sprint 6).

Acumula contadores de tentativas de autenticação (total, sucessos e falhas)
e disponibiliza um resumo estruturado para relatórios e monitoramento.
"""

from __future__ import annotations

from .evento import EventoDeAutenticacao
from .observador import ObservadorDeAutenticacao


class ObservadorDeEstatisticasDeAutenticacao(ObservadorDeAutenticacao):
    """Observador concreto que acumula estatísticas de autenticação.

    Mantém contadores incrementais de cada tipo de resultado de login,
    permitindo consultar métricas do sistema sem precisar varrer um
    repositório de registros.
    """

    def __init__(self) -> None:
        self._total: int = 0
        self._sucessos: int = 0
        self._falhas: int = 0

    def atualizar(self, evento: EventoDeAutenticacao) -> None:
        """Incrementa os contadores com base no resultado do evento."""
        self._total += 1
        if evento.sucesso:
            self._sucessos += 1
        else:
            self._falhas += 1

    # --- propriedades de leitura ---

    @property
    def total_tentativas(self) -> int:
        """Total de tentativas de autenticação recebidas."""
        return self._total

    @property
    def total_sucessos(self) -> int:
        """Total de autenticações bem-sucedidas."""
        return self._sucessos

    @property
    def total_falhas(self) -> int:
        """Total de autenticações malsucedidas."""
        return self._falhas

    def resumo(self) -> dict[str, int]:
        """Retorna um dicionário com o resumo atual das estatísticas.

        Returns:
            Dicionário com as chaves ``total``, ``sucessos`` e ``falhas``.
        """
        return {
            "total": self._total,
            "sucessos": self._sucessos,
            "falhas": self._falhas,
        }

    def zerar(self) -> None:
        """Reinicia todos os contadores para zero."""
        self._total = 0
        self._sucessos = 0
        self._falhas = 0

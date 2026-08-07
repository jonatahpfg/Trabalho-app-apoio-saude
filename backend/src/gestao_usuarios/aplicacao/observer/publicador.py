"""Subject (Publicador) do padrão GoF Observer — eventos de autenticação.

Gerencia a lista de observadores inscritos e os notifica a cada evento
de autenticação (sucesso ou falha) publicado pelo GerenciadorDeUsuarios.

Participantes do padrão (GoF):
- Subject:   PublicadorDeEventosDeAutenticacao (esta classe)
- Observer:  ObservadorDeAutenticacao (ABC)
- Concrete Observers: ObservadorDeLogDeAutenticacao,
                      ObservadorDeEstatisticasDeAutenticacao
"""

from __future__ import annotations

from .evento import EventoDeAutenticacao
from .observador import ObservadorDeAutenticacao


class PublicadorDeEventosDeAutenticacao:
    """Gerencia os observadores e notifica-os sobre eventos de autenticação.

    Segue o padrão Subject do GoF Observer:
    - ``assinar``              → registra um observador;
    - ``cancelar_assinatura``  → remove um observador;
    - ``notificar``            → envia o evento a todos os observadores.
    """

    def __init__(self) -> None:
        self._observadores: list[ObservadorDeAutenticacao] = []

    def assinar(self, observador: ObservadorDeAutenticacao) -> None:
        """Inscreve um observador para receber eventos futuros.

        Se o observador já estiver inscrito, a chamada é ignorada.
        """
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar_assinatura(self, observador: ObservadorDeAutenticacao) -> None:
        """Remove um observador previamente inscrito.

        Se o observador não estiver inscrito, a chamada é ignorada.
        """
        try:
            self._observadores.remove(observador)
        except ValueError:
            pass

    def notificar(self, evento: EventoDeAutenticacao) -> None:
        """Notifica todos os observadores inscritos com o evento fornecido."""
        for observador in list(self._observadores):
            observador.atualizar(evento)

    @property
    def total_observadores(self) -> int:
        """Retorna o número de observadores atualmente inscritos."""
        return len(self._observadores)

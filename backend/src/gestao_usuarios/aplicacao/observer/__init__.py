"""Subpacote observer — padrão GoF Observer para eventos de autenticação (Sprint 6).

O Observer desacopla o GerenciadorDeUsuarios dos seus ouvintes: em vez de
chamar diretamente o log ou as estatísticas, o gerenciador publica um
EventoDeAutenticacao e o PublicadorDeEventosDeAutenticacao despacha-o
para todos os observadores inscritos.
"""

from .evento import EventoDeAutenticacao
from .observador import ObservadorDeAutenticacao
from .observador_de_estatisticas import ObservadorDeEstatisticasDeAutenticacao
from .observador_de_log import ObservadorDeLogDeAutenticacao
from .publicador import PublicadorDeEventosDeAutenticacao

__all__ = [
    "EventoDeAutenticacao",
    "ObservadorDeAutenticacao",
    "ObservadorDeLogDeAutenticacao",
    "ObservadorDeEstatisticasDeAutenticacao",
    "PublicadorDeEventosDeAutenticacao",
]

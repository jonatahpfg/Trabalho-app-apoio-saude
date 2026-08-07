"""Evento de autenticação publicado pelo Observer (Sprint 6).

O EventoDeAutenticacao é o objeto de dados transportado do Subject
(GerenciadorDeUsuarios / PublicadorDeEventosDeAutenticacao) para
cada observador inscrito.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EventoDeAutenticacao:
    """Dados de uma tentativa de autenticação.

    Attributes:
        login:      login informado na tentativa.
        sucesso:    True se o login foi bem-sucedido, False caso contrário.
        data_hora:  momento em que o evento ocorreu (UTC por padrão).
    """

    login: str
    sucesso: bool
    data_hora: datetime = field(default_factory=datetime.now)

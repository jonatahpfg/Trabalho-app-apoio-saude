"""Subpacote proxy — padrão GoF Proxy para autorização por perfil (Sprint 6).

O Proxy envolve os gerenciadores reais e verifica se o usuário autenticado
possui o perfil necessário antes de delegar cada operação.
"""

from .gerenciador_unidades_proxy import ProxyGerenciadorDeUnidades
from .gerenciador_usuarios_proxy import ProxyGerenciadorDeUsuarios

__all__ = [
    "ProxyGerenciadorDeUsuarios",
    "ProxyGerenciadorDeUnidades",
]

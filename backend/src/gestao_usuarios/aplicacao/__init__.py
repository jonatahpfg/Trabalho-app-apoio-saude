"""Pacote da camada de aplicação do sistema."""

from .comandos import (
    Comando,
    ComandoAdicionarUnidade,
    ComandoAdicionarUsuario,
    ComandoAtualizarUnidade,
    ComandoAutenticar,
    ComandoAutenticarUsuario,
    ComandoBuscarUnidadePorId,
    ComandoContarTotalEntidades,
    ComandoDesfazerAtualizacaoDeUnidade,
    ComandoListarUnidades,
    ComandoListarUsuarios,
    ComandoRemoverUnidade,
    ExecutorDeComandos,
)
from .facade_singleton_controller import (
    FacadeDoSistema,
    FacadeSingletonController,
)
from .gerenciador_de_unidades import GerenciadorDeUnidades
from .gerenciador_de_usuarios import GerenciadorDeUsuarios
from .historico_de_unidade import HistoricoDeUnidade
from .observer import (
    EventoDeAutenticacao,
    ObservadorDeAutenticacao,
    ObservadorDeEstatisticasDeAutenticacao,
    ObservadorDeLogDeAutenticacao,
    PublicadorDeEventosDeAutenticacao,
)
from .proxy import ProxyGerenciadorDeUnidades, ProxyGerenciadorDeUsuarios
from .relatorio_de_acessos import RelatorioDeAcessos
from .relatorio_de_acessos_csv import RelatorioDeAcessosCsv
from .relatorio_de_acessos_texto import RelatorioDeAcessosTexto

__all__ = [
    "Comando",
    "ComandoAdicionarUnidade",
    "ComandoAdicionarUsuario",
    "ComandoAtualizarUnidade",
    "ComandoAutenticar",
    "ComandoAutenticarUsuario",
    "ComandoBuscarUnidadePorId",
    "ComandoContarTotalEntidades",
    "ComandoDesfazerAtualizacaoDeUnidade",
    "ComandoListarUnidades",
    "ComandoListarUsuarios",
    "ComandoRemoverUnidade",
    "ExecutorDeComandos",
    "EventoDeAutenticacao",
    "FacadeDoSistema",
    "FacadeSingletonController",
    "GerenciadorDeUnidades",
    "GerenciadorDeUsuarios",
    "HistoricoDeUnidade",
    "ObservadorDeAutenticacao",
    "ObservadorDeEstatisticasDeAutenticacao",
    "ObservadorDeLogDeAutenticacao",
    "ProxyGerenciadorDeUnidades",
    "ProxyGerenciadorDeUsuarios",
    "PublicadorDeEventosDeAutenticacao",
    "RelatorioDeAcessos",
    "RelatorioDeAcessosCsv",
    "RelatorioDeAcessosTexto",
]
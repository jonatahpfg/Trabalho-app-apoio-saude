"""Relatório de acessos em texto legível — concretização do Template Method."""

from __future__ import annotations

from .relatorio_de_acessos import (
    EstatisticaPorLogin,
    EstatisticasDeAcesso,
    RelatorioDeAcessos,
)

_FORMATO_DATA_HORA = "%d/%m/%Y %H:%M"


class RelatorioDeAcessosTexto(RelatorioDeAcessos):
    """Formata as estatísticas de acesso para leitura humana."""

    def _cabecalho(self) -> str:
        return "RELATÓRIO DE ACESSOS"

    def _linha_por_login(
        self,
        estatistica: EstatisticaPorLogin,
    ) -> str:
        return (
            f"{estatistica.login}: {estatistica.tentativas} tentativa(s) "
            f"({estatistica.sucessos} sucesso(s), {estatistica.falhas} falha(s)) "
            f"— último acesso em "
            f"{estatistica.ultimo_acesso.strftime(_FORMATO_DATA_HORA)}"
        )

    def _rodape(
        self,
        estatisticas: EstatisticasDeAcesso,
    ) -> str:
        return (
            f"Total: {estatisticas.total} tentativa(s) | "
            f"{estatisticas.sucessos} sucesso(s) | "
            f"{estatisticas.falhas} falha(s) | "
            f"taxa de sucesso: {estatisticas.taxa_de_sucesso:.1f}%"
        )
"""Relatório de acessos em CSV — concretização do Template Method."""

from __future__ import annotations

from .relatorio_de_acessos import (
    EstatisticaPorLogin,
    EstatisticasDeAcesso,
    RelatorioDeAcessos,
)


class RelatorioDeAcessosCsv(RelatorioDeAcessos):
    """Formata as estatísticas de acesso como CSV para uso por outras ferramentas."""

    def _cabecalho(self) -> str:
        return "login,tentativas,sucessos,falhas,ultimo_acesso"

    def _linha_por_login(
        self,
        estatistica: EstatisticaPorLogin,
    ) -> str:
        return ",".join(
            [
                f'"{estatistica.login}"',
                str(estatistica.tentativas),
                str(estatistica.sucessos),
                str(estatistica.falhas),
                estatistica.ultimo_acesso.isoformat(),
            ]
        )

    def _rodape(
        self,
        estatisticas: EstatisticasDeAcesso,
    ) -> str:
        return (
            f'"TOTAL",{estatisticas.total},{estatisticas.sucessos},'
            f"{estatisticas.falhas},{estatisticas.taxa_de_sucesso:.1f}%"
        )
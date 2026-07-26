"""Relatório de estatísticas de acesso — Template Method (GoF, Tarefa 5).

``RelatorioDeAcessos.gerar()`` é o método-molde: fixa o esqueleto do
algoritmo (coletar registros → calcular estatísticas → compor cabeçalho,
corpo e rodapé) e delega às subclasses apenas os passos de formatação.
Subclasses nunca alteram a ordem dos passos — só implementam os hooks
``_cabecalho``, ``_linha_por_login`` e ``_rodape``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ..dominio.registro_de_acesso import RegistroDeAcesso
from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso


@dataclass(frozen=True)
class EstatisticaPorLogin:
    """Consolidado das tentativas de autenticação de um login."""

    login: str
    tentativas: int
    sucessos: int
    falhas: int
    ultimo_acesso: datetime


@dataclass(frozen=True)
class EstatisticasDeAcesso:
    """Consolidado geral das tentativas de login registradas."""

    total: int
    sucessos: int
    falhas: int
    por_login: list[EstatisticaPorLogin]

    @property
    def taxa_de_sucesso(self) -> float:
        """Percentual de tentativas bem-sucedidas (0.0 quando não há registros)."""
        if self.total == 0:
            return 0.0

        return self.sucessos / self.total * 100


class RelatorioDeAcessos(ABC):
    """Classe-base do Template Method para relatórios de acesso."""

    def __init__(
        self,
        repositorio_acessos: RepositorioRegistroDeAcesso,
    ) -> None:
        self._repositorio_acessos = repositorio_acessos

    def gerar(self) -> str:
        """Método-molde: monta o relatório completo na ordem fixa do padrão.

        1. Coleta os registros pela porta.
        2. Calcula as estatísticas (passo comum a todos os formatos).
        3. Compõe cabeçalho, uma linha por login e rodapé (hooks).
        """
        registros = self._repositorio_acessos.buscar_todos()
        estatisticas = self._calcular_estatisticas(registros)

        linhas = [self._cabecalho()]

        linhas.extend(
            self._linha_por_login(estatistica)
            for estatistica in estatisticas.por_login
        )

        linhas.append(
            self._rodape(estatisticas)
        )

        return "\n".join(linhas)

    @staticmethod
    def _calcular_estatisticas(
        registros: list[RegistroDeAcesso],
    ) -> EstatisticasDeAcesso:
        """Passo comum do molde: consolida os registros por login (ordem alfabética)."""
        por_login: dict[str, list[RegistroDeAcesso]] = {}

        for registro in registros:
            por_login.setdefault(
                registro.login,
                [],
            ).append(registro)

        consolidados = [
            EstatisticaPorLogin(
                login=login,
                tentativas=len(eventos),
                sucessos=sum(
                    1
                    for evento in eventos
                    if evento.sucesso
                ),
                falhas=sum(
                    1
                    for evento in eventos
                    if not evento.sucesso
                ),
                ultimo_acesso=max(
                    evento.data_hora
                    for evento in eventos
                ),
            )
            for login, eventos in sorted(
                por_login.items()
            )
        ]

        return EstatisticasDeAcesso(
            total=len(registros),
            sucessos=sum(
                1
                for registro in registros
                if registro.sucesso
            ),
            falhas=sum(
                1
                for registro in registros
                if not registro.sucesso
            ),
            por_login=consolidados,
        )

    @abstractmethod
    def _cabecalho(self) -> str:
        """Primeira linha do relatório."""

    @abstractmethod
    def _linha_por_login(
        self,
        estatistica: EstatisticaPorLogin,
    ) -> str:
        """Uma linha do corpo, com o consolidado de um login."""

    @abstractmethod
    def _rodape(
        self,
        estatisticas: EstatisticasDeAcesso,
    ) -> str:
        """Última linha do relatório, com os totais gerais."""
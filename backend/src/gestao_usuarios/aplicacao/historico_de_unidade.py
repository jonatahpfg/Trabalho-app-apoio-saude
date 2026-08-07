from __future__ import annotations

from ..dominio.erros import NenhumaAtualizacaoParaDesfazer
from ..dominio.memento_unidade_basica_saude import (
    MementoUnidadeBasicaSaude,
)


class HistoricoDeUnidade:
    """Caretaker que mantém somente o último estado de uma UBS."""

    def __init__(self) -> None:
        self._ultimo: MementoUnidadeBasicaSaude | None = None

    def salvar(
        self,
        memento: MementoUnidadeBasicaSaude,
    ) -> None:
        """Guarda o último estado da UBS."""
        self._ultimo = memento

    def obter_ultimo(
        self,
    ) -> MementoUnidadeBasicaSaude:
        """Retorna o último estado salvo."""
        if self._ultimo is None:
            raise NenhumaAtualizacaoParaDesfazer(
                "Não existe atualização de UBS para desfazer."
            )

        return self._ultimo

    def descartar_ultimo(self) -> None:
        """Descarta o estado depois de uma restauração."""
        self._ultimo = None

    @property
    def possui_estado(self) -> bool:
        """Indica se existe um estado disponível para restauração."""
        return self._ultimo is not None
"""Porta secundária de persistência de Unidades Básicas de Saúde."""

from __future__ import annotations

from typing import Protocol

from ..dominio.unidade_basica_saude import UnidadeBasicaSaude


class RepositorioUnidadeBasicaSaude(Protocol):
    """Contrato de persistência de UBS."""

    def salvar(self, unidade: UnidadeBasicaSaude) -> UnidadeBasicaSaude:
        """Persiste a unidade, atribuindo um id se ainda não tiver."""
        ...

    def buscar_todas(self) -> list[UnidadeBasicaSaude]:
        """Devolve todas as unidades cadastradas."""
        ...

    def buscar_por_id(self, unidade_id: int) -> UnidadeBasicaSaude | None:
        """Devolve a unidade com o id informado, ou ``None`` se não existir."""
        ...

    def buscar_por_cnpj(self, cnpj: str) -> UnidadeBasicaSaude | None:
        """Devolve a unidade com o CNPJ informado, ou ``None`` se não existir."""
        ...

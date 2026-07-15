"""Adaptador de persistência em memória (RAM) da porta RepositorioUnidadeBasicaSaude."""

from __future__ import annotations

from dataclasses import replace

from ..dominio.unidade_basica_saude import UnidadeBasicaSaude


class RepositorioUnidadeEmMemoria:
    """Guarda as UBS numa coleção em memória. Some quando o processo termina."""

    def __init__(self) -> None:
        self._unidades: dict[int, UnidadeBasicaSaude] = {}
        self._proximo_id = 1

    def salvar(self, unidade: UnidadeBasicaSaude) -> UnidadeBasicaSaude:
        if unidade.id is None:
            unidade = replace(unidade, id=self._proximo_id)
            self._proximo_id += 1
        self._unidades[unidade.id] = unidade
        return replace(unidade)

    def buscar_todas(self) -> list[UnidadeBasicaSaude]:
        return [replace(u) for u in self._unidades.values()]

    def buscar_por_id(self, unidade_id: int) -> UnidadeBasicaSaude | None:
        u = self._unidades.get(unidade_id)
        return replace(u) if u is not None else None

    def buscar_por_cnpj(self, cnpj: str) -> UnidadeBasicaSaude | None:
        for u in self._unidades.values():
            if u.cnpj == cnpj:
                return replace(u)
        return None

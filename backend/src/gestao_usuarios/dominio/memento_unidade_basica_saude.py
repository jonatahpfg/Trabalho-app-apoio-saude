from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MementoUnidadeBasicaSaude:
    nome: str
    cnpj: str
    endereco: str
    telefone: str
    ativa: bool
    id: int | None
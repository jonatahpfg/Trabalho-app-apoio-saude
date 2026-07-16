"""Seletor de fábrica concreta (Factory Method)."""

from __future__ import annotations

from ..portas.fabrica_repositorio import FabricaRepositorio
from .fabrica_repositorio_banco_de_dados import FabricaRepositorioBancoDeDados
from .fabrica_repositorio_em_memoria import FabricaRepositorioEmMemoria


def obter_fabrica_repositorio(tipo: str) -> FabricaRepositorio:
    """Retorna a fábrica concreta com base no tipo de armazenamento especificado.

    Funciona como o Factory Method para resolver a fábrica abstrata de repositórios.

    Args:
        tipo: O tipo de armazenamento desejado ('bd' ou 'memoria').

    Returns:
        Uma implementação de FabricaRepositorio.
    """
    if tipo == "bd":
        return FabricaRepositorioBancoDeDados()
    return FabricaRepositorioEmMemoria()

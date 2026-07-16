"""Porta secundária (abstração) de fábrica de repositórios."""

from __future__ import annotations

from typing import Protocol

from .repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
from .repositorio_unidade_basica_saude import RepositorioUnidadeBasicaSaude
from .repositorio_usuario import RepositorioUsuario


class FabricaRepositorio(Protocol):
    """Contrato de fábrica abstrata para criação dos repositórios do sistema.

    O núcleo da aplicação interage com esta interface para obter instâncias
    dos repositórios sem depender das implementações concretas (memória, banco de dados, etc.).
    """

    def criar_repositorio_usuario(self) -> RepositorioUsuario:
        """Cria e retorna uma implementação compatível de RepositorioUsuario."""
        ...

    def criar_repositorio_unidade_basica_saude(self) -> RepositorioUnidadeBasicaSaude:
        """Cria e retorna uma implementação compatível de RepositorioUnidadeBasicaSaude."""
        ...

    def criar_repositorio_registro_de_acesso(self) -> RepositorioRegistroDeAcesso:
        """Cria e retorna uma implementação compatível de RepositorioRegistroDeAcesso."""
        ...

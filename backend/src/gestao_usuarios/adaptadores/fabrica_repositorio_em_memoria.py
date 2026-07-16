"""Fábrica de repositórios em memória (RAM)."""

from __future__ import annotations

from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
from ..portas.repositorio_unidade_basica_saude import RepositorioUnidadeBasicaSaude
from ..portas.repositorio_usuario import RepositorioUsuario
from .repositorio_registro_de_acesso_em_memoria import RepositorioRegistroDeAcessoEmMemoria
from .repositorio_unidade_em_memoria import RepositorioUnidadeEmMemoria
from .repositorio_usuario_em_memoria import RepositorioUsuarioEmMemoria


class FabricaRepositorioEmMemoria:
    """Implementação concreta de FabricaRepositorio que cria objetos em memória (RAM)."""

    def criar_repositorio_usuario(self) -> RepositorioUsuario:
        return RepositorioUsuarioEmMemoria()

    def criar_repositorio_unidade_basica_saude(self) -> RepositorioUnidadeBasicaSaude:
        return RepositorioUnidadeEmMemoria()

    def criar_repositorio_registro_de_acesso(self) -> RepositorioRegistroDeAcesso:
        return RepositorioRegistroDeAcessoEmMemoria()

"""Fábrica de repositórios baseados em banco de dados e arquivos."""

from __future__ import annotations

from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
from ..portas.repositorio_unidade_basica_saude import RepositorioUnidadeBasicaSaude
from ..portas.repositorio_usuario import RepositorioUsuario
from .adaptador_arquivo_de_log import AdaptadorArquivoDeLog
from .arquivo_de_log_simples import ArquivoDeLogSimples
from .repositorio_unidade_em_memoria import RepositorioUnidadeEmMemoria
from .repositorio_usuario_banco_de_dados import RepositorioUsuarioBancoDeDados


class FabricaRepositorioBancoDeDados:
    """Implementação concreta de FabricaRepositorio que cria objetos persistentes.

    Utiliza SQLite para usuários, arquivo de log para acessos e mantém UBS em memória
    conforme comportamento original do sistema.
    """

    def __init__(self, db_path: str = "usuarios.db", log_path: str = "acessos.log") -> None:
        self._db_path = db_path
        self._log_path = log_path

    def criar_repositorio_usuario(self) -> RepositorioUsuario:
        return RepositorioUsuarioBancoDeDados(self._db_path)

    def criar_repositorio_unidade_basica_saude(self) -> RepositorioUnidadeBasicaSaude:
        # Por padrão UBS permanece em memória
        return RepositorioUnidadeEmMemoria()

    def criar_repositorio_registro_de_acesso(self) -> RepositorioRegistroDeAcesso:
        return AdaptadorArquivoDeLog(ArquivoDeLogSimples(self._log_path))

from __future__ import annotations

from pathlib import Path
# pyrefly: ignore [missing-import]
import pytest

from gestao_usuarios.adaptadores.adaptador_arquivo_de_log import AdaptadorArquivoDeLog
# pyrefly: ignore [missing-import]
from gestao_usuarios.adaptadores.fabrica_repositorio_banco_de_dados import (
    FabricaRepositorioBancoDeDados,
)
# pyrefly: ignore [missing-import]
from gestao_usuarios.adaptadores.fabrica_repositorio_em_memoria import (
    FabricaRepositorioEmMemoria,
)
# pyrefly: ignore [missing-import]
from gestao_usuarios.adaptadores.repositorio_registro_de_acesso_em_memoria import (
    RepositorioRegistroDeAcessoEmMemoria,
)
from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.adaptadores.repositorio_usuario_banco_de_dados import (
    RepositorioUsuarioBancoDeDados,
)
from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.adaptadores.seletor_fabrica import obter_fabrica_repositorio


def test_seletor_retorna_fabrica_em_memoria():
    fabrica = obter_fabrica_repositorio("memoria")
    assert isinstance(fabrica, FabricaRepositorioEmMemoria)


def test_seletor_retorna_fabrica_banco_de_dados():
    fabrica = obter_fabrica_repositorio("bd")
    assert isinstance(fabrica, FabricaRepositorioBancoDeDados)


def test_seletor_padrao_para_outros_valores():
    fabrica = obter_fabrica_repositorio("qualquer_coisa")
    assert isinstance(fabrica, FabricaRepositorioEmMemoria)


def test_fabrica_em_memoria_cria_instancias_corretas():
    fabrica = FabricaRepositorioEmMemoria()

    repo_usuario = fabrica.criar_repositorio_usuario()
    assert isinstance(repo_usuario, RepositorioUsuarioEmMemoria)

    repo_unidade = fabrica.criar_repositorio_unidade_basica_saude()
    assert isinstance(repo_unidade, RepositorioUnidadeEmMemoria)

    repo_acesso = fabrica.criar_repositorio_registro_de_acesso()
    assert isinstance(repo_acesso, RepositorioRegistroDeAcessoEmMemoria)


def test_fabrica_banco_de_dados_cria_instancias_corretas(tmp_path):
    db_file = str(tmp_path / "test.db")
    log_file = str(tmp_path / "test.log")

    fabrica = FabricaRepositorioBancoDeDados(db_path=db_file, log_path=log_file)

    repo_usuario = fabrica.criar_repositorio_usuario()
    assert isinstance(repo_usuario, RepositorioUsuarioBancoDeDados)
    assert repo_usuario.caminho_db == db_file

    repo_unidade = fabrica.criar_repositorio_unidade_basica_saude()
    assert isinstance(repo_unidade, RepositorioUnidadeEmMemoria)

    repo_acesso = fabrica.criar_repositorio_registro_de_acesso()
    assert isinstance(repo_acesso, AdaptadorArquivoDeLog)
    assert repo_acesso._arquivo_de_log._caminho == Path(log_file)

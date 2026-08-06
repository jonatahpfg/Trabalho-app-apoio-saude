"""Testes unitários dos comandos de remoção e listagem de UBS (Padrão Command)."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    ComandoAdicionarUnidade,
    ComandoBuscarUnidadePorId,
    ComandoListarUnidades,
    ComandoRemoverUnidade,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from gestao_usuarios.dominio.erros import UnidadeNaoEncontrada


@pytest.fixture
def gerenciador_unidades() -> GerenciadorDeUnidades:
    return GerenciadorDeUnidades(RepositorioUnidadeEmMemoria())


@pytest.fixture
def executor() -> ExecutorDeComandos:
    return ExecutorDeComandos()


def test_comando_remover_unidade_logicamente(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    unidade = executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS Sul",
            cnpj="12345678000199",
            endereco="Rua Sul, 100",
            telefone="84999990000",
        )
    )

    comando_remover = ComandoRemoverUnidade(
        gerenciador_unidades,
        unidade_id=unidade.id,
    )
    assert comando_remover.unidade_id == unidade.id

    removida = executor.executar(comando_remover)
    assert removida.id == unidade.id
    assert removida.ativa is False

    # Verifica que foi desativada no repositório
    consultada = executor.executar(
        ComandoBuscarUnidadePorId(gerenciador_unidades, unidade.id)
    )
    assert consultada.ativa is False

    # Listar apenas ativas não deve retornar a unidade removida
    ativas = executor.executar(
        ComandoListarUnidades(gerenciador_unidades, apenas_ativas=True)
    )
    assert ativas == []

    # Listar todas deve retornar a unidade
    todas = executor.executar(
        ComandoListarUnidades(gerenciador_unidades, apenas_ativas=False)
    )
    assert len(todas) == 1


def test_comando_remover_unidade_inexistente(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    comando = ComandoRemoverUnidade(
        gerenciador_unidades,
        unidade_id=999,
    )

    with pytest.raises(UnidadeNaoEncontrada):
        executor.executar(comando)


def test_comando_listar_unidades_vazio_e_com_elementos(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    comando_listar = ComandoListarUnidades(gerenciador_unidades)
    assert executor.executar(comando_listar) == []

    executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS 1",
            cnpj="11111111000111",
            endereco="Rua 1",
            telefone="84911111111",
        )
    )
    executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS 2",
            cnpj="22222222000122",
            endereco="Rua 2",
            telefone="84922222222",
        )
    )

    unidades = executor.executar(comando_listar)
    assert len(unidades) == 2

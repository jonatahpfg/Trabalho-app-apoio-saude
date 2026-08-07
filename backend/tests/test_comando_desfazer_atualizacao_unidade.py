"""Testes do comando para desfazer a última atualização de uma UBS."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    ComandoAdicionarUnidade,
    ComandoAtualizarUnidade,
    ComandoDesfazerAtualizacaoDeUnidade,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import (
    GerenciadorDeUnidades,
)
from gestao_usuarios.dominio.erros import (
    NenhumaAtualizacaoParaDesfazer,
)


@pytest.fixture
def gerenciador_unidades() -> GerenciadorDeUnidades:
    return GerenciadorDeUnidades(
        RepositorioUnidadeEmMemoria()
    )


@pytest.fixture
def executor() -> ExecutorDeComandos:
    return ExecutorDeComandos()


def test_comando_desfazer_restaura_estado_anterior(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    unidade = executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS Centro",
            cnpj="12345678000199",
            endereco="Rua Principal, 100",
            telefone="84999990000",
        )
    )

    executor.executar(
        ComandoAtualizarUnidade(
            gerenciador_unidades,
            unidade_id=unidade.id,
            nome="UBS Centro Atualizada",
            cnpj="98765432000110",
            endereco="Rua Nova, 200",
            telefone="84988887777",
        )
    )

    comando = ComandoDesfazerAtualizacaoDeUnidade(
        gerenciador_unidades
    )

    restaurada = executor.executar(comando)

    assert restaurada.id == unidade.id
    assert restaurada.nome == "UBS Centro"
    assert restaurada.cnpj == "12345678000199"
    assert restaurada.endereco == "Rua Principal, 100"
    assert restaurada.telefone == "84999990000"
    assert restaurada.ativa is True

    persistida = gerenciador_unidades.buscar_unidade_por_id(
        unidade.id
    )

    assert persistida == restaurada


def test_executor_registra_comando_desfazer_quando_tem_sucesso(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    unidade = gerenciador_unidades.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    gerenciador_unidades.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Atualizada",
        cnpj="98765432000110",
        endereco="Rua Nova, 200",
        telefone="84988887777",
    )

    comando = ComandoDesfazerAtualizacaoDeUnidade(
        gerenciador_unidades
    )

    executor.executar(comando)

    assert executor.ultimo_comando is comando
    assert executor.historico == [comando]


def test_executor_nao_registra_comando_desfazer_quando_falha(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    comando = ComandoDesfazerAtualizacaoDeUnidade(
        gerenciador_unidades
    )

    with pytest.raises(NenhumaAtualizacaoParaDesfazer):
        executor.executar(comando)

    assert executor.ultimo_comando is None
    assert executor.historico == []
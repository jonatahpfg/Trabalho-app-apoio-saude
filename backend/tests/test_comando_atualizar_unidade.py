"""Testes unitários do comando atualizar unidade e busca (Padrão Command)."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    ComandoAdicionarUnidade,
    ComandoAtualizarUnidade,
    ComandoBuscarUnidadePorId,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from gestao_usuarios.dominio.erros import (
    CnpjDuplicado,
    ErroDeValidacao,
    UnidadeNaoEncontrada,
)


@pytest.fixture
def gerenciador_unidades() -> GerenciadorDeUnidades:
    return GerenciadorDeUnidades(RepositorioUnidadeEmMemoria())


@pytest.fixture
def executor() -> ExecutorDeComandos:
    return ExecutorDeComandos()


def test_comando_atualizar_unidade_com_sucesso(
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

    comando_atualizar = ComandoAtualizarUnidade(
        gerenciador_unidades,
        unidade_id=unidade.id,
        nome="UBS Centro Renovada",
        cnpj="12345678000199",
        endereco="Rua Nova, 500",
        telefone="84988887777",
    )

    assert comando_atualizar.unidade_id == unidade.id
    assert comando_atualizar.nome == "UBS Centro Renovada"
    assert comando_atualizar.cnpj == "12345678000199"
    assert comando_atualizar.endereco == "Rua Nova, 500"
    assert comando_atualizar.telefone == "84988887777"

    atualizada = executor.executar(comando_atualizar)

    assert atualizada.id == unidade.id
    assert atualizada.nome == "UBS Centro Renovada"
    assert atualizada.endereco == "Rua Nova, 500"
    assert atualizada.telefone == "84988887777"


def test_comando_atualizar_unidade_inexistente(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    comando = ComandoAtualizarUnidade(
        gerenciador_unidades,
        unidade_id=999,
        nome="UBS Fantasma",
        cnpj="12345678000199",
        endereco="Rua Fantasma, 0",
        telefone="84999990000",
    )

    with pytest.raises(UnidadeNaoEncontrada):
        executor.executar(comando)


def test_comando_atualizar_unidade_rejeita_cnpj_duplicado_de_outra_unidade(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    u1 = executor.executar(
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

    # Tenta atualizar a UBS 1 usando o CNPJ da UBS 2
    comando = ComandoAtualizarUnidade(
        gerenciador_unidades,
        unidade_id=u1.id,
        nome="UBS 1 Alterada",
        cnpj="22222222000122",
        endereco="Rua 1",
        telefone="84911111111",
    )

    with pytest.raises(CnpjDuplicado):
        executor.executar(comando)


def test_comando_atualizar_unidade_rejeita_dados_invalidos(
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

    comando = ComandoAtualizarUnidade(
        gerenciador_unidades,
        unidade_id=unidade.id,
        nome="",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    with pytest.raises(ErroDeValidacao):
        executor.executar(comando)


def test_comando_buscar_unidade_por_id(
    gerenciador_unidades: GerenciadorDeUnidades,
    executor: ExecutorDeComandos,
):
    unidade = executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS Norte",
            cnpj="98765432000110",
            endereco="Rua Norte, 200",
            telefone="84988887777",
        )
    )

    comando_busca = ComandoBuscarUnidadePorId(
        gerenciador_unidades,
        unidade_id=unidade.id,
    )
    assert comando_busca.unidade_id == unidade.id

    encontrada = executor.executar(comando_busca)
    assert encontrada.id == unidade.id
    assert encontrada.nome == "UBS Norte"

    comando_busca_inexistente = ComandoBuscarUnidadePorId(
        gerenciador_unidades,
        unidade_id=999,
    )
    with pytest.raises(UnidadeNaoEncontrada):
        executor.executar(comando_busca_inexistente)

"""Testes do CRUD de Unidade Básica de Saúde."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from gestao_usuarios.dominio.erros import (
    CnpjDuplicado,
    ErroDeValidacao,
    UnidadeNaoEncontrada,
)


def _criar_gerenciador() -> GerenciadorDeUnidades:
    return GerenciadorDeUnidades(RepositorioUnidadeEmMemoria())


# ------------------------------------------------------------------ #
# Testes — Adicionar (Create)                                         #
# ------------------------------------------------------------------ #


def test_deve_adicionar_unidade_valida():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    assert unidade.id == 1
    assert unidade.nome == "UBS Centro"
    assert unidade.cnpj == "12345678000199"
    assert unidade.ativa is True


def test_deve_rejeitar_cnpj_duplicado():
    gerenciador = _criar_gerenciador()

    gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    with pytest.raises(CnpjDuplicado):
        gerenciador.adicionar_unidade(
            nome="UBS Sul",
            cnpj="12345678000199",
            endereco="Rua Sul, 300",
            telefone="84977776666",
        )


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("cnpj", ""),
        ("endereco", ""),
        ("telefone", ""),
    ],
)
def test_deve_rejeitar_campos_obrigatorios_vazios(campo, valor):
    gerenciador = _criar_gerenciador()

    dados = {
        "nome": "UBS Centro",
        "cnpj": "12345678000199",
        "endereco": "Rua Principal, 100",
        "telefone": "84999990000",
    }
    dados[campo] = valor

    with pytest.raises(ErroDeValidacao):
        gerenciador.adicionar_unidade(**dados)


def test_deve_rejeitar_cnpj_com_tamanho_invalido():
    gerenciador = _criar_gerenciador()

    with pytest.raises(ErroDeValidacao):
        gerenciador.adicionar_unidade(
            nome="UBS Centro",
            cnpj="123",
            endereco="Rua Principal, 100",
            telefone="84999990000",
        )


# ------------------------------------------------------------------ #
# Testes — Listar e Buscar (Read)                                     #
# ------------------------------------------------------------------ #


def test_deve_listar_unidades():
    gerenciador = _criar_gerenciador()

    gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )
    gerenciador.adicionar_unidade(
        nome="UBS Norte",
        cnpj="98765432000110",
        endereco="Rua Norte, 200",
        telefone="84988887777",
    )

    unidades = gerenciador.listar_unidades()

    assert len(unidades) == 2


def test_deve_buscar_unidade_por_id():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    encontrada = gerenciador.buscar_unidade_por_id(unidade.id)

    assert encontrada.nome == "UBS Centro"
    assert encontrada.cnpj == "12345678000199"


def test_deve_rejeitar_busca_de_unidade_inexistente():
    gerenciador = _criar_gerenciador()

    with pytest.raises(UnidadeNaoEncontrada):
        gerenciador.buscar_unidade_por_id(999)


# ------------------------------------------------------------------ #
# Testes — Atualizar (Update)                                         #
# ------------------------------------------------------------------ #


def test_deve_atualizar_unidade():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    atualizada = gerenciador.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Centro Atualizada",
        cnpj="12345678000199",
        endereco="Rua Nova, 200",
        telefone="84988887777",
    )

    assert atualizada.id == unidade.id
    assert atualizada.nome == "UBS Centro Atualizada"
    assert atualizada.endereco == "Rua Nova, 200"
    assert atualizada.telefone == "84988887777"


# ------------------------------------------------------------------ #
# Testes — Remover / Desativar (Delete lógico)                        #
# ------------------------------------------------------------------ #


def test_deve_remover_unidade_logicamente():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    removida = gerenciador.remover_unidade(unidade.id)

    assert removida.ativa is False

    encontrada = gerenciador.buscar_unidade_por_id(unidade.id)

    assert encontrada.ativa is False
    assert gerenciador.listar_unidades(apenas_ativas=True) == []


def test_deve_rejeitar_remocao_de_unidade_inexistente():
    gerenciador = _criar_gerenciador()

    with pytest.raises(UnidadeNaoEncontrada):
        gerenciador.remover_unidade(999)

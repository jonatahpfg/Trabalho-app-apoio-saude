"""Testes do padrão Memento aplicado à UnidadeBasicaSaude."""

from dataclasses import FrozenInstanceError

import pytest

from gestao_usuarios.dominio.unidade_basica_saude import (
    UnidadeBasicaSaude,
)


def _criar_unidade() -> UnidadeBasicaSaude:
    """Cria uma UBS válida para uso nos testes."""
    unidade = UnidadeBasicaSaude.criar(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )
    unidade.id = 1

    return unidade


def test_criar_memento_copia_todo_estado_da_unidade():
    unidade = _criar_unidade()

    memento = unidade.criar_memento()

    assert memento.id == 1
    assert memento.nome == "UBS Centro"
    assert memento.cnpj == "12345678000199"
    assert memento.endereco == "Rua Principal, 100"
    assert memento.telefone == "84999990000"
    assert memento.ativa is True


def test_memento_nao_e_a_mesma_instancia_da_unidade():
    unidade = _criar_unidade()

    memento = unidade.criar_memento()

    assert memento is not unidade


def test_memento_preserva_estado_mesmo_apos_alterar_unidade():
    unidade = _criar_unidade()

    memento = unidade.criar_memento()

    unidade.nome = "UBS Alterada"
    unidade.endereco = "Rua Alterada"
    unidade.telefone = "84988887777"
    unidade.ativa = False

    assert memento.nome == "UBS Centro"
    assert memento.endereco == "Rua Principal, 100"
    assert memento.telefone == "84999990000"
    assert memento.ativa is True


def test_memento_e_imutavel():
    unidade = _criar_unidade()

    memento = unidade.criar_memento()

    with pytest.raises(FrozenInstanceError):
        memento.nome = "Tentativa de alteração"


def test_restaurar_recupera_estado_anterior():
    unidade = _criar_unidade()

    memento = unidade.criar_memento()

    unidade.nome = "UBS Alterada"
    unidade.cnpj = "98765432000110"
    unidade.endereco = "Rua Nova, 500"
    unidade.telefone = "84988887777"
    unidade.ativa = False
    unidade.id = 99

    unidade.restaurar(memento)

    assert unidade.id == 1
    assert unidade.nome == "UBS Centro"
    assert unidade.cnpj == "12345678000199"
    assert unidade.endereco == "Rua Principal, 100"
    assert unidade.telefone == "84999990000"
    assert unidade.ativa is True


def test_memento_preserva_unidade_inativa():
    unidade = _criar_unidade()
    unidade.ativa = False

    memento = unidade.criar_memento()

    unidade.ativa = True

    unidade.restaurar(memento)

    assert unidade.ativa is False
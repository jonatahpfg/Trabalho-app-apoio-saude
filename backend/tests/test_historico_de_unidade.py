"""Testes do Caretaker HistoricoDeUnidade."""

import pytest

from gestao_usuarios.aplicacao.historico_de_unidade import (
    HistoricoDeUnidade,
)
from gestao_usuarios.dominio.erros import (
    NenhumaAtualizacaoParaDesfazer,
)
from gestao_usuarios.dominio.memento_unidade_basica_saude import (
    MementoUnidadeBasicaSaude,
)


def _criar_memento(
    *,
    nome: str = "UBS Centro",
    id_unidade: int = 1,
) -> MementoUnidadeBasicaSaude:
    """Cria um Memento válido para uso nos testes."""
    return MementoUnidadeBasicaSaude(
        nome=nome,
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
        ativa=True,
        id=id_unidade,
    )


def test_historico_inicia_sem_estado():
    historico = HistoricoDeUnidade()

    assert historico.possui_estado is False


def test_obter_ultimo_sem_estado_lanca_excecao():
    historico = HistoricoDeUnidade()

    with pytest.raises(NenhumaAtualizacaoParaDesfazer):
        historico.obter_ultimo()


def test_salvar_memento_permite_recuperar_estado():
    historico = HistoricoDeUnidade()
    memento = _criar_memento()

    historico.salvar(memento)

    assert historico.possui_estado is True
    assert historico.obter_ultimo() == memento


def test_historico_retorna_o_mesmo_memento_salvo():
    historico = HistoricoDeUnidade()
    memento = _criar_memento()

    historico.salvar(memento)

    recuperado = historico.obter_ultimo()

    assert recuperado is memento


def test_novo_memento_substitui_o_anterior():
    historico = HistoricoDeUnidade()

    primeiro = _criar_memento(
        nome="UBS Estado 1",
        id_unidade=1,
    )
    segundo = _criar_memento(
        nome="UBS Estado 2",
        id_unidade=2,
    )

    historico.salvar(primeiro)
    historico.salvar(segundo)

    recuperado = historico.obter_ultimo()

    assert recuperado == segundo
    assert recuperado != primeiro
    assert recuperado.nome == "UBS Estado 2"


def test_descartar_ultimo_remove_estado():
    historico = HistoricoDeUnidade()
    historico.salvar(_criar_memento())

    historico.descartar_ultimo()

    assert historico.possui_estado is False


def test_obter_depois_de_descartar_lanca_excecao():
    historico = HistoricoDeUnidade()
    historico.salvar(_criar_memento())

    historico.descartar_ultimo()

    with pytest.raises(NenhumaAtualizacaoParaDesfazer):
        historico.obter_ultimo()


def test_historico_pode_receber_novo_estado_depois_de_descartar():
    historico = HistoricoDeUnidade()

    primeiro = _criar_memento(nome="Primeiro")
    segundo = _criar_memento(nome="Segundo")

    historico.salvar(primeiro)
    historico.descartar_ultimo()
    historico.salvar(segundo)

    assert historico.possui_estado is True
    assert historico.obter_ultimo() == segundo
"""Testes do CRUD de Unidade Básica de Saúde."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import (
    GerenciadorDeUnidades,
)
from gestao_usuarios.dominio.erros import (
    CnpjDuplicado,
    ErroDeValidacao,
    NenhumaAtualizacaoParaDesfazer,
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
# Testes — Memento / Desfazer atualização                             #
# ------------------------------------------------------------------ #


def test_deve_desfazer_ultima_atualizacao_e_restaurar_estado_anterior():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    gerenciador.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Centro Atualizada",
        cnpj="98765432000110",
        endereco="Rua Nova, 200",
        telefone="84988887777",
    )

    restaurada = (
        gerenciador.desfazer_ultima_atualizacao_de_unidade()
    )

    assert restaurada.id == unidade.id
    assert restaurada.nome == "UBS Centro"
    assert restaurada.cnpj == "12345678000199"
    assert restaurada.endereco == "Rua Principal, 100"
    assert restaurada.telefone == "84999990000"
    assert restaurada.ativa is True

    persistida = gerenciador.buscar_unidade_por_id(unidade.id)

    assert persistida == restaurada


def test_duas_atualizacoes_e_um_desfazer_restaura_penultimo_estado():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Original",
        cnpj="12345678000199",
        endereco="Rua Original, 100",
        telefone="84999990000",
    )

    gerenciador.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Primeira Atualização",
        cnpj="23456789000188",
        endereco="Rua Primeira, 200",
        telefone="84988887777",
    )

    gerenciador.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Segunda Atualização",
        cnpj="34567890000177",
        endereco="Rua Segunda, 300",
        telefone="84977776666",
    )

    restaurada = (
        gerenciador.desfazer_ultima_atualizacao_de_unidade()
    )

    assert restaurada.id == unidade.id
    assert restaurada.nome == "UBS Primeira Atualização"
    assert restaurada.cnpj == "23456789000188"
    assert restaurada.endereco == "Rua Primeira, 200"
    assert restaurada.telefone == "84988887777"


def test_segundo_desfazer_sem_nova_atualizacao_lanca_excecao():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    gerenciador.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Atualizada",
        cnpj="98765432000110",
        endereco="Rua Nova, 200",
        telefone="84988887777",
    )

    gerenciador.desfazer_ultima_atualizacao_de_unidade()

    with pytest.raises(NenhumaAtualizacaoParaDesfazer):
        gerenciador.desfazer_ultima_atualizacao_de_unidade()


def test_atualizacao_invalida_nao_deve_criar_memento():
    gerenciador = _criar_gerenciador()

    unidade = gerenciador.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    with pytest.raises(ErroDeValidacao):
        gerenciador.atualizar_unidade(
            unidade_id=unidade.id,
            nome="",
            cnpj="98765432000110",
            endereco="Rua Nova, 200",
            telefone="84988887777",
        )

    with pytest.raises(NenhumaAtualizacaoParaDesfazer):
        gerenciador.desfazer_ultima_atualizacao_de_unidade()

    persistida = gerenciador.buscar_unidade_por_id(unidade.id)

    assert persistida.nome == "UBS Centro"
    assert persistida.cnpj == "12345678000199"
    assert persistida.endereco == "Rua Principal, 100"
    assert persistida.telefone == "84999990000"


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
from datetime import datetime

import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.registro_de_acesso import RegistroDeAcesso


def test_cria_registro_quando_dados_validos():
    momento = datetime(2026, 7, 15, 10, 30)

    registro = RegistroDeAcesso.criar(
        login="ana",
        sucesso=True,
        data_hora=momento,
    )

    assert registro.login == "ana"
    assert registro.sucesso is True
    assert registro.data_hora == momento
    assert registro.id is None


def test_preenche_data_hora_quando_nao_informada():
    registro = RegistroDeAcesso.criar(
        login="ana",
        sucesso=False,
    )

    assert isinstance(
        registro.data_hora,
        datetime,
    )


def test_normaliza_login_removendo_espacos():
    registro = RegistroDeAcesso.criar(
        login="  ana  ",
        sucesso=True,
    )

    assert registro.login == "ana"


def test_rejeita_registro_quando_login_vazio():
    with pytest.raises(ErroDeValidacao):
        RegistroDeAcesso.criar(
            login="   ",
            sucesso=True,
        )


def test_rejeita_registro_quando_sucesso_nao_e_booleano():
    with pytest.raises(ErroDeValidacao):
        RegistroDeAcesso.criar(
            login="ana",
            sucesso="sim",
        )
from datetime import datetime

import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.registro_de_acesso import RegistroDeAcesso


def test_cria_registro_quando_dados_validos():
    momento = datetime(2026, 7, 15, 10, 30)

    registro = RegistroDeAcesso.criar(
        email="ana@ubs.gov.br", sucesso=True, data_hora=momento
    )

    assert registro.email == "ana@ubs.gov.br"
    assert registro.sucesso is True
    assert registro.data_hora == momento
    assert registro.id is None


def test_preenche_data_hora_quando_nao_informada():
    registro = RegistroDeAcesso.criar(email="ana@ubs.gov.br", sucesso=False)

    assert isinstance(registro.data_hora, datetime)


def test_normaliza_email_removendo_espacos():
    registro = RegistroDeAcesso.criar(email="  ana@ubs.gov.br  ", sucesso=True)

    assert registro.email == "ana@ubs.gov.br"


def test_rejeita_registro_quando_email_vazio():
    with pytest.raises(ErroDeValidacao):
        RegistroDeAcesso.criar(email="   ", sucesso=True)


def test_rejeita_registro_quando_sucesso_nao_e_booleano():
    with pytest.raises(ErroDeValidacao):
        RegistroDeAcesso.criar(email="ana@ubs.gov.br", sucesso="sim")

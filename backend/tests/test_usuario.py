import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.usuario import Perfil, Usuario


def test_cria_usuario_quando_dados_validos():
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        perfil=Perfil.MEDICO,
    )

    assert usuario.nome == "Ana"
    assert usuario.perfil is Perfil.MEDICO
    assert usuario.ativo is True
    assert usuario.id is None


def test_aceita_perfil_informado_como_texto():
    usuario = Usuario.criar(
        nome="Bia",
        cpf="98765432100",
        email="bia@ubs.gov.br",
        telefone="84988887777",
        perfil="GESTOR",
    )

    assert usuario.perfil is Perfil.GESTOR


def test_rejeita_usuario_quando_nome_vazio():
    with pytest.raises(ErroDeValidacao):
        Usuario.criar(
            nome="   ",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_email_invalido():
    with pytest.raises(ErroDeValidacao):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana-sem-arroba",
            telefone="84999990000",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_perfil_invalido():
    with pytest.raises(ErroDeValidacao):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            perfil="DIRETOR",
        )

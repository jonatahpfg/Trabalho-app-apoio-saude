import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.usuario import Perfil, Usuario


def test_cria_usuario_quando_dados_validos():
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
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
        senha="OutraSenha1!",
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
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_email_invalido():
    with pytest.raises(ErroDeValidacao):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana-sem-arroba",
            telefone="84999990000",
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_perfil_invalido():
    with pytest.raises(ErroDeValidacao):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="Senha123!",
            perfil="DIRETOR",
        )


def test_rejeita_usuario_quando_senha_muito_curta():
    with pytest.raises(ErroDeValidacao, match="entre 8 e 128"):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="A1!a",  # 4 chars, 4 types
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_muito_longa():
    senha_longa = "A1!a" * 35  # 140 chars
    with pytest.raises(ErroDeValidacao, match="entre 8 e 128"):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha=senha_longa,
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_igual_ao_nome():
    with pytest.raises(ErroDeValidacao, match="igual ao nome ou e-mail"):
        Usuario.criar(
            nome="AnaMaria123!",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="AnaMaria123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_igual_ao_email():
    with pytest.raises(ErroDeValidacao, match="igual ao nome ou e-mail"):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="Ana123!@ubs.gov.br",
            telefone="84999990000",
            senha="Ana123!@ubs.gov.br",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_nao_atinge_tres_tipos_de_caracteres():
    # Only lowercase and numbers (2 types)
    with pytest.raises(ErroDeValidacao, match="no mínimo 3 dos 4 tipos"):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="apenasminusculas123",
            perfil=Perfil.MEDICO,
        )


def test_cria_usuario_quando_senha_atende_tres_de_quatro_requisitos():
    # Only uppercase, lowercase and numbers (3 types)
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="SenhaApenasLetrasENumeros123",
        perfil=Perfil.MEDICO,
    )
    assert usuario.nome == "Ana"

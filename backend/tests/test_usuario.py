import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.usuario import Perfil, Usuario


def test_cria_usuario_quando_dados_validos():
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )

    assert usuario.nome == "Ana"
    assert usuario.login == "ana"
    assert usuario.perfil is Perfil.MEDICO
    assert usuario.ativo is True
    assert usuario.id is None


def test_aceita_perfil_informado_como_texto():
    usuario = Usuario.criar(
        nome="Bia",
        cpf="98765432100",
        email="bia@ubs.gov.br",
        telefone="84988887777",
        login="bia",
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
            login="ana",
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
            login="ana",
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
            login="ana",
            senha="Senha123!",
            perfil="DIRETOR",
        )


# ---------------------------------------------------------------------------
# Validação do login
# ---------------------------------------------------------------------------


def test_rejeita_usuario_quando_login_vazio():
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="",
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_login_apenas_espacos():
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="   ",
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_aceita_login_com_12_caracteres():
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="abcdefghijkl",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )

    assert usuario.login == "abcdefghijkl"


def test_rejeita_login_com_mais_de_12_caracteres():
    with pytest.raises(
        ErroDeValidacao,
        match="no máximo 12",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="abcdefghijklm",
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_normaliza_login_removendo_espacos_nas_extremidades():
    usuario = Usuario.criar(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="  ana  ",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )

    assert usuario.login == "ana"


# ---------------------------------------------------------------------------
# Validação da senha
# ---------------------------------------------------------------------------


def test_rejeita_usuario_quando_senha_muito_curta():
    with pytest.raises(
        ErroDeValidacao,
        match="entre 8 e 128",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="A1!a",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_muito_longa():
    senha_longa = "A1!a" * 35

    with pytest.raises(
        ErroDeValidacao,
        match="entre 8 e 128",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha=senha_longa,
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_igual_ao_nome():
    with pytest.raises(
        ErroDeValidacao,
        match="igual ao nome ou e-mail",
    ):
        Usuario.criar(
            nome="AnaMaria123!",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="AnaMaria123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_igual_ao_email():
    with pytest.raises(
        ErroDeValidacao,
        match="igual ao nome ou e-mail",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="Ana123!@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="Ana123!@ubs.gov.br",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_senha_nao_atinge_tres_tipos_de_caracteres():
    # Only lowercase and numbers (2 types)
    with pytest.raises(
        ErroDeValidacao,
        match="no mínimo 3 dos 4 tipos",
    ):
        Usuario.criar(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
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
        login="ana",
        senha="SenhaApenasLetrasENumeros123",
        perfil=Perfil.MEDICO,
    )

    assert usuario.nome == "Ana"
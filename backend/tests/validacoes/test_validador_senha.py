import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.validacoes.validador_senha import (
    TAMANHO_MAXIMO_SENHA,
    TAMANHO_MINIMO_SENHA,
    ValidadorSenha,
)


def test_aceita_senha_valida():
    senha = "Senha123!"

    resultado = ValidadorSenha.validar(
        senha,
        nome="Ana",
        email="ana@ubs.gov.br",
    )

    assert resultado == senha


def test_aceita_senha_com_tres_tipos_de_caracteres():
    senha = "SenhaComNumeros123"

    resultado = ValidadorSenha.validar(
        senha,
        nome="Ana",
        email="ana@ubs.gov.br",
    )

    assert resultado == senha


def test_rejeita_senha_vazia():
    with pytest.raises(
        ErroDeValidacao,
        match="senha",
    ):
        ValidadorSenha.validar(
            "",
            nome="Ana",
            email="ana@ubs.gov.br",
        )


def test_rejeita_senha_apenas_com_espacos():
    with pytest.raises(
        ErroDeValidacao,
        match="senha",
    ):
        ValidadorSenha.validar(
            "   ",
            nome="Ana",
            email="ana@ubs.gov.br",
        )


def test_rejeita_senha_menor_que_o_minimo():
    senha = "A1!a"

    assert len(senha) < TAMANHO_MINIMO_SENHA

    with pytest.raises(
        ErroDeValidacao,
        match="entre 8 e 128",
    ):
        ValidadorSenha.validar(
            senha,
            nome="Ana",
            email="ana@ubs.gov.br",
        )


def test_rejeita_senha_maior_que_o_maximo():
    senha = "A1!a" * 33

    assert len(senha) > TAMANHO_MAXIMO_SENHA

    with pytest.raises(
        ErroDeValidacao,
        match="entre 8 e 128",
    ):
        ValidadorSenha.validar(
            senha,
            nome="Ana",
            email="ana@ubs.gov.br",
        )


def test_rejeita_senha_igual_ao_nome():
    senha = "AnaMaria123!"

    with pytest.raises(
        ErroDeValidacao,
        match="igual ao nome ou e-mail",
    ):
        ValidadorSenha.validar(
            senha,
            nome=senha,
            email="ana@ubs.gov.br",
        )


def test_rejeita_senha_igual_ao_email():
    senha = "Ana123!@ubs.gov.br"

    with pytest.raises(
        ErroDeValidacao,
        match="igual ao nome ou e-mail",
    ):
        ValidadorSenha.validar(
            senha,
            nome="Ana",
            email=senha,
        )


def test_rejeita_senha_com_apenas_dois_tipos_de_caracteres():
    senha = "apenasminusculas123"

    with pytest.raises(
        ErroDeValidacao,
        match="no mínimo 3 dos 4 tipos",
    ):
        ValidadorSenha.validar(
            senha,
            nome="Ana",
            email="ana@ubs.gov.br",
        )


def test_aceita_senha_com_quatro_tipos_de_caracteres():
    senha = "Senha123!"

    resultado = ValidadorSenha.validar(
        senha,
        nome="Ana",
        email="ana@ubs.gov.br",
    )

    assert resultado == senha
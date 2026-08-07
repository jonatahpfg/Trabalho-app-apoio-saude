import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.validacoes.validador_login import (
    TAMANHO_MAXIMO_LOGIN,
    ValidadorLogin,
)


def test_aceita_login_valido():
    resultado = ValidadorLogin.validar(
        "ana"
    )

    assert resultado == "ana"


def test_remove_espacos_nas_extremidades():
    resultado = ValidadorLogin.validar(
        "  ana  "
    )

    assert resultado == "ana"


def test_aceita_login_com_tamanho_maximo():
    login = "a" * TAMANHO_MAXIMO_LOGIN

    resultado = ValidadorLogin.validar(
        login
    )

    assert resultado == login


def test_rejeita_login_com_mais_de_12_caracteres():
    login = "a" * (
        TAMANHO_MAXIMO_LOGIN + 1
    )

    with pytest.raises(
        ErroDeValidacao,
        match="no máximo 12",
    ):
        ValidadorLogin.validar(
            login
        )


def test_rejeita_login_vazio():
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        ValidadorLogin.validar(
            ""
        )


def test_rejeita_login_apenas_com_espacos():
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        ValidadorLogin.validar(
            "   "
        )


def test_rejeita_login_none():
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        ValidadorLogin.validar(
            None
        )


def test_rejeita_login_com_numeros():
    with pytest.raises(
        ErroDeValidacao,
        match="não pode conter números",
    ):
        ValidadorLogin.validar(
            "ana2"
        )


def test_rejeita_login_formado_apenas_por_numeros():
    with pytest.raises(
        ErroDeValidacao,
        match="não pode conter números",
    ):
        ValidadorLogin.validar(
            "12345"
        )


def test_aceita_login_com_letras_acentuadas():
    resultado = ValidadorLogin.validar(
        "joão"
    )

    assert resultado == "joão"


def test_valida_o_tamanho_antes_de_verificar_os_numeros():
    login = "a" * (
        TAMANHO_MAXIMO_LOGIN + 1
    ) + "1"

    with pytest.raises(
        ErroDeValidacao,
        match="no máximo 12",
    ):
        ValidadorLogin.validar(
            login
        )
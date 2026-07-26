import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.validacoes.validador_email import (
    ValidadorEmail,
)


def test_aceita_email_valido():
    resultado = ValidadorEmail.validar(
        "ana@ubs.gov.br"
    )

    assert resultado == "ana@ubs.gov.br"


def test_remove_espacos_nas_extremidades():
    resultado = ValidadorEmail.validar(
        "  ana@ubs.gov.br  "
    )

    assert resultado == "ana@ubs.gov.br"


def test_rejeita_email_sem_arroba():
    with pytest.raises(
        ErroDeValidacao,
        match="E-mail inválido",
    ):
        ValidadorEmail.validar(
            "ana.ubs.gov.br"
        )


def test_rejeita_email_sem_dominio():
    with pytest.raises(
        ErroDeValidacao,
        match="E-mail inválido",
    ):
        ValidadorEmail.validar(
            "ana@"
        )


def test_rejeita_email_sem_extensao():
    with pytest.raises(
        ErroDeValidacao,
        match="E-mail inválido",
    ):
        ValidadorEmail.validar(
            "ana@ubs"
        )


def test_rejeita_email_vazio():
    with pytest.raises(
        ErroDeValidacao,
        match="email",
    ):
        ValidadorEmail.validar(
            ""
        )


def test_rejeita_email_apenas_com_espacos():
    with pytest.raises(
        ErroDeValidacao,
        match="email",
    ):
        ValidadorEmail.validar(
            "   "
        )


def test_rejeita_email_none():
    with pytest.raises(
        ErroDeValidacao,
        match="email",
    ):
        ValidadorEmail.validar(
            None
        )
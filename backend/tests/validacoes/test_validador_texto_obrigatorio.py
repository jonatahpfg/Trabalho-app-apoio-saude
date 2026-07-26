import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.validacoes.validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)


def test_aceita_texto_valido():
    resultado = ValidadorTextoObrigatorio.validar(
        "Ana",
        "nome",
    )

    assert resultado == "Ana"


def test_remove_espacos_nas_extremidades():
    resultado = ValidadorTextoObrigatorio.validar(
        "  Ana  ",
        "nome",
    )

    assert resultado == "Ana"


def test_rejeita_texto_vazio():
    with pytest.raises(
        ErroDeValidacao,
        match="nome",
    ):
        ValidadorTextoObrigatorio.validar(
            "",
            "nome",
        )


def test_rejeita_texto_apenas_com_espacos():
    with pytest.raises(
        ErroDeValidacao,
        match="nome",
    ):
        ValidadorTextoObrigatorio.validar(
            "   ",
            "nome",
        )


def test_rejeita_none():
    with pytest.raises(
        ErroDeValidacao,
        match="nome",
    ):
        ValidadorTextoObrigatorio.validar(
            None,
            "nome",
        )
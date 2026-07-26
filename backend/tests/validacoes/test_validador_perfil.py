from enum import Enum

import pytest

from gestao_usuarios.dominio.erros import ErroDeValidacao
from gestao_usuarios.dominio.validacoes.validador_perfil import (
    ValidadorPerfil,
)


class PerfilFake(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    GESTOR = "GESTOR"
    MEDICO = "MEDICO"


def test_aceita_perfil_que_ja_e_enum():
    resultado = ValidadorPerfil.validar(
        PerfilFake.MEDICO,
        PerfilFake,
    )

    assert resultado is PerfilFake.MEDICO


def test_converte_texto_para_perfil():
    resultado = ValidadorPerfil.validar(
        "GESTOR",
        PerfilFake,
    )

    assert resultado is PerfilFake.GESTOR


def test_rejeita_perfil_inexistente():
    with pytest.raises(
        ErroDeValidacao,
        match="Perfil inválido",
    ):
        ValidadorPerfil.validar(
            "DIRETOR",
            PerfilFake,
        )


def test_rejeita_valor_none():
    with pytest.raises(
        ErroDeValidacao,
        match="Perfil inválido",
    ):
        ValidadorPerfil.validar(
            None,
            PerfilFake,
        )
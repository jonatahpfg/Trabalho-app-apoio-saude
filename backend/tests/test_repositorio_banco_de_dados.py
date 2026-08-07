from dataclasses import replace
import sqlite3

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_banco_de_dados import (
    RepositorioUsuarioBancoDeDados,
)
from gestao_usuarios.dominio.erros import ErroDeAcessoAoBanco
from gestao_usuarios.dominio.usuario import Perfil, Usuario

# O login não pode conter números (RN02), então o CPF é convertido
# em letras para gerar um login único e válido em cada cenário.
_DIGITO_PARA_LETRA = str.maketrans(
    "0123456789",
    "abcdefghij",
)


def _login_sem_numeros(cpf: str) -> str:
    return f"u{cpf[-6:].translate(_DIGITO_PARA_LETRA)}"


def _usuario(
    cpf: str = "12345678901",
    login: str | None = None,
) -> Usuario:
    return Usuario.criar(
        nome="Ana",
        cpf=cpf,
        email=f"{cpf}@ubs.gov.br",
        telefone="84999990000",
        login=login or _login_sem_numeros(cpf),
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )


def test_salvar_no_banco_atribui_id_e_insere(tmp_path):
    db_path = str(tmp_path / "usuarios.db")
    repositorio = RepositorioUsuarioBancoDeDados(db_path)

    usuario = _usuario("11111111111", login="ana")
    salvo = repositorio.salvar(usuario)

    assert salvo.id is not None
    assert salvo.nome == "Ana"
    assert salvo.login == "ana"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT id, nome, cpf, email, login, perfil
            FROM usuarios
            WHERE id = ?
            """,
            (salvo.id,),
        )
        linha = cursor.fetchone()

    assert linha is not None
    assert linha["nome"] == "Ana"
    assert linha["cpf"] == "11111111111"
    assert linha["email"] == "11111111111@ubs.gov.br"
    assert linha["login"] == "ana"
    assert linha["perfil"] == "MEDICO"


def test_salvar_violacao_de_constraint_lanca_erro_de_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    # Salvar primeiro usuário.
    repositorio.salvar(
        _usuario(
            "11111111111",
            login="usuarioum",
        )
    )

    # Salvar segundo com mesmo CPF deve violar a UNIQUE constraint no banco
    # e lançar ErroDeAcessoAoBanco.
    u_duplicado = _usuario(
        "11111111111",
        login="usuariodois",
    )

    with pytest.raises(ErroDeAcessoAoBanco):
        repositorio.salvar(u_duplicado)


def test_salvar_login_duplicado_lanca_erro_de_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    usuario_com_login_duplicado = _usuario(
        "22222222222",
        login="ana",
    )

    with pytest.raises(ErroDeAcessoAoBanco):
        repositorio.salvar(usuario_com_login_duplicado)


def test_buscar_todos_devolve_usuarios_salvos():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    repositorio.salvar(
        _usuario(
            "11111111111",
            login="usuarioum",
        )
    )
    repositorio.salvar(
        _usuario(
            "22222222222",
            login="usuariodois",
        )
    )

    usuarios = repositorio.buscar_todos()

    assert len(usuarios) == 2
    assert {u.cpf for u in usuarios} == {
        "11111111111",
        "22222222222",
    }


def test_buscar_por_cpf_devolve_usuario_ou_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    encontrado = repositorio.buscar_por_cpf(
        "11111111111"
    )

    assert encontrado is not None
    assert encontrado.id == salvo.id
    assert encontrado.perfil is Perfil.MEDICO
    assert repositorio.buscar_por_cpf("99999999999") is None


def test_buscar_por_email_devolve_usuario_ou_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    encontrado = repositorio.buscar_por_email(
        "11111111111@ubs.gov.br"
    )

    assert encontrado is not None
    assert encontrado.cpf == "11111111111"
    assert repositorio.buscar_por_email("nao@existe.br") is None


def test_buscar_por_login_devolve_usuario_ou_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    encontrado = repositorio.buscar_por_login("ana")

    assert encontrado is not None
    assert encontrado.id == salvo.id
    assert encontrado.login == "ana"
    assert encontrado.cpf == "11111111111"

    assert repositorio.buscar_por_login("naoexiste") is None


def test_atualizar_usuario_existente_persiste_mudanca():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    repositorio.salvar(
        replace(
            salvo,
            ativo=False,
        )
    )

    atualizado = repositorio.buscar_por_cpf(
        "11111111111"
    )

    assert atualizado is not None
    assert atualizado.ativo is False
    assert atualizado.login == "ana"


def test_buscar_por_id_encontra_ou_devolve_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    encontrado = repositorio.buscar_por_id(
        salvo.id
    )

    assert encontrado is not None
    assert encontrado.id == salvo.id
    assert encontrado.login == "ana"
    assert repositorio.buscar_por_id(999) is None


def test_salvar_usuario_existente_atualiza_o_registro_no_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    repositorio.salvar(
        salvo.atualizar_dados(
            nome="Ana Souza",
            cpf=salvo.cpf,
            email=salvo.email,
            telefone=salvo.telefone,
            login="anasouza",
            perfil=salvo.perfil,
        )
    )

    atualizado = repositorio.buscar_por_id(salvo.id)

    assert len(repositorio.buscar_todos()) == 1
    assert atualizado.nome == "Ana Souza"
    assert atualizado.login == "anasouza"


def test_salvar_usuario_desativado_persiste_a_situacao_no_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    salvo = repositorio.salvar(
        _usuario(
            "11111111111",
            login="ana",
        )
    )

    repositorio.salvar(salvo.desativar())

    assert repositorio.buscar_por_id(salvo.id).ativo is False

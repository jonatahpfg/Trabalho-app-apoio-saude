import pytest
import sqlite3
from gestao_usuarios.adaptadores.repositorio_usuario_banco_de_dados import (
    RepositorioUsuarioBancoDeDados,
)
from gestao_usuarios.dominio.usuario import Perfil, Usuario
from gestao_usuarios.dominio.erros import ErroDeAcessoAoBanco


def _usuario(cpf: str = "12345678901") -> Usuario:
    return Usuario.criar(
        nome="Ana",
        cpf=cpf,
        email=f"{cpf}@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )

def test_salvar_no_banco_atribui_id_e_insere(tmp_path):
    db_path = str(tmp_path / "usuarios.db")
    repositorio = RepositorioUsuarioBancoDeDados(db_path)

    usuario = _usuario("11111111111")
    salvo = repositorio.salvar(usuario)

    assert salvo.id is not None
    assert salvo.nome == "Ana"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, nome, cpf, email, perfil FROM usuarios WHERE id = ?",
            (salvo.id,),
        )
        linha = cursor.fetchone()

    assert linha is not None
    assert linha["nome"] == "Ana"
    assert linha["cpf"] == "11111111111"
    assert linha["email"] == "11111111111@ubs.gov.br"
    assert linha["perfil"] == "MEDICO"

def test_salvar_violacao_de_constraint_lanca_erro_de_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")

    # Salvar primeiro usuário
    repositorio.salvar(_usuario("11111111111"))

    # Salvar segundo com mesmo CPF deve violar a UNIQUE constraint no banco
    # e lançar ErroDeAcessoAoBanco
    u_duplicado = _usuario("11111111111")
    with pytest.raises(ErroDeAcessoAoBanco):
        repositorio.salvar(u_duplicado)


def test_buscar_todos_devolve_usuarios_salvos():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")
    repositorio.salvar(_usuario("11111111111"))
    repositorio.salvar(_usuario("22222222222"))

    usuarios = repositorio.buscar_todos()

    assert len(usuarios) == 2
    assert {u.cpf for u in usuarios} == {"11111111111", "22222222222"}


def test_buscar_por_cpf_devolve_usuario_ou_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")
    salvo = repositorio.salvar(_usuario("11111111111"))

    encontrado = repositorio.buscar_por_cpf("11111111111")

    assert encontrado is not None
    assert encontrado.id == salvo.id
    assert encontrado.perfil is Perfil.MEDICO
    assert repositorio.buscar_por_cpf("99999999999") is None


def test_buscar_por_email_devolve_usuario_ou_none():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")
    repositorio.salvar(_usuario("11111111111"))

    encontrado = repositorio.buscar_por_email("11111111111@ubs.gov.br")

    assert encontrado is not None
    assert encontrado.cpf == "11111111111"
    assert repositorio.buscar_por_email("nao@existe.br") is None


def test_atualizar_usuario_existente_persiste_mudanca():
    from dataclasses import replace

    repositorio = RepositorioUsuarioBancoDeDados(":memory:")
    salvo = repositorio.salvar(_usuario("11111111111"))

    repositorio.salvar(replace(salvo, ativo=False))

    atualizado = repositorio.buscar_por_cpf("11111111111")
    assert atualizado is not None
    assert atualizado.ativo is False

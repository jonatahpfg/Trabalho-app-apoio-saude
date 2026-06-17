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


def test_salvar_no_banco_atribui_id_e_insere():
    # Usando banco em memória ":memory:" para testar isoladamente
    db_path = ":memory:"
    repositorio = RepositorioUsuarioBancoDeDados(db_path)

    usuario = _usuario("11111111111")
    salvo = repositorio.salvar(usuario)

    assert salvo.id is not None
    assert salvo.nome == "Ana"

    # Verificar se está no banco consultando diretamente via conexão SQLite
    # Já que o repositório agora não tem mais os métodos de busca.
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT id, nome, cpf, email, perfil FROM usuarios WHERE id = ?", (salvo.id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row["id"] == salvo.id
        assert row["cpf"] == "11111111111"
        assert row["nome"] == "Ana"
        assert row["perfil"] == "MEDICO"


def test_salvar_violacao_de_constraint_lanca_erro_de_banco():
    repositorio = RepositorioUsuarioBancoDeDados(":memory:")
    
    # Salvar primeiro usuário
    repositorio.salvar(_usuario("11111111111"))

    # Salvar segundo com mesmo CPF deve violar a UNIQUE constraint no banco
    # e lançar ErroDeAcessoAoBanco
    u_duplicado = _usuario("11111111111")
    with pytest.raises(ErroDeAcessoAoBanco):
        repositorio.salvar(u_duplicado)

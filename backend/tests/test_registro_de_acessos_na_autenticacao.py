"""Testes do registro de acessos no fluxo de autenticação (Tarefa 5).

Usa um dublê simples da porta RepositorioRegistroDeAcesso: o adaptador
real é responsabilidade de outro teste — aqui interessa apenas o contrato.
"""
from dataclasses import replace

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.dominio.erros import (
    CredenciaisInvalidas,
    ErroDeValidacao,
    UsuarioInativo,
)
from gestao_usuarios.dominio.registro_de_acesso import RegistroDeAcesso
from gestao_usuarios.dominio.usuario import Perfil


class RepositorioRegistroDeAcessoFake:
    """Dublê em memória da porta, apenas para os testes deste módulo."""

    def __init__(self) -> None:
        self.registros: list[RegistroDeAcesso] = []

    def salvar(self, registro: RegistroDeAcesso) -> RegistroDeAcesso:
        registro = replace(registro, id=len(self.registros) + 1)
        self.registros.append(registro)
        return registro

    def buscar_todos(self) -> list[RegistroDeAcesso]:
        return list(self.registros)


@pytest.fixture
def repositorio_acessos() -> RepositorioRegistroDeAcessoFake:
    return RepositorioRegistroDeAcessoFake()


@pytest.fixture
def gerenciador(repositorio_acessos) -> GerenciadorDeUsuarios:
    gerenciador = GerenciadorDeUsuarios(
        RepositorioUsuarioEmMemoria(), repositorio_acessos
    )
    gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!!",
        perfil=Perfil.MEDICO,
    )
    return gerenciador


def test_registra_acesso_com_sucesso_quando_login_valido(gerenciador, repositorio_acessos):
    gerenciador.autenticar(email="ana@ubs.gov.br", senha="Senha123!!")

    registros = repositorio_acessos.buscar_todos()
    assert len(registros) == 1
    assert registros[0].email == "ana@ubs.gov.br"
    assert registros[0].sucesso is True


def test_registra_falha_quando_senha_incorreta(gerenciador, repositorio_acessos):
    with pytest.raises(CredenciaisInvalidas):
        gerenciador.autenticar(email="ana@ubs.gov.br", senha="senha_errada")

    registros = repositorio_acessos.buscar_todos()
    assert len(registros) == 1
    assert registros[0].sucesso is False


def test_registra_falha_quando_email_nao_cadastrado(gerenciador, repositorio_acessos):
    with pytest.raises(CredenciaisInvalidas):
        gerenciador.autenticar(email="inexistente@ubs.gov.br", senha="Senha123!!")

    registros = repositorio_acessos.buscar_todos()
    assert len(registros) == 1
    assert registros[0].email == "inexistente@ubs.gov.br"
    assert registros[0].sucesso is False


def test_registra_falha_quando_usuario_inativo(gerenciador, repositorio_acessos):
    repositorio = gerenciador._repositorio
    usuario = repositorio.buscar_por_email("ana@ubs.gov.br")
    repositorio.salvar(replace(usuario, ativo=False))

    with pytest.raises(UsuarioInativo):
        gerenciador.autenticar(email="ana@ubs.gov.br", senha="Senha123!!")

    registros = repositorio_acessos.buscar_todos()
    assert len(registros) == 1
    assert registros[0].sucesso is False


def test_nao_registra_acesso_quando_campos_em_branco(gerenciador, repositorio_acessos):
    """Erros de validação não são tentativas reais de login."""
    with pytest.raises(ErroDeValidacao):
        gerenciador.autenticar(email="", senha="Senha123!!")

    assert repositorio_acessos.buscar_todos() == []


def test_acumula_registros_de_varias_tentativas(gerenciador, repositorio_acessos):
    gerenciador.autenticar(email="ana@ubs.gov.br", senha="Senha123!!")
    with pytest.raises(CredenciaisInvalidas):
        gerenciador.autenticar(email="ana@ubs.gov.br", senha="senha_errada")
    gerenciador.autenticar(email="ana@ubs.gov.br", senha="Senha123!!")

    registros = repositorio_acessos.buscar_todos()
    assert [r.sucesso for r in registros] == [True, False, True]


def test_autentica_normalmente_sem_porta_de_acessos():
    """A porta é opcional: sem ela o fluxo de login não muda (retrocompatível)."""
    gerenciador = GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())
    gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!!",
        perfil=Perfil.MEDICO,
    )

    usuario = gerenciador.autenticar(email="ana@ubs.gov.br", senha="Senha123!!")

    assert usuario.nome == "Ana Souza"

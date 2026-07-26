"""Testes de validação de login (autenticar).

Cada teste verifica um cenário distinto de exceção, aplicando os princípios
dos artigos indicados pelo professor:

- Taborda: exceções específicas e hierárquicas (CredenciaisInvalidas,
  UsuarioInativo) — o chamador captura a subclasse correta.
- PLoP 2018 (Coelho et al.): sem Empty Catch, sem Catch Generic —
  cada assert verifica o tipo exato da exceção lançada.
"""

from dataclasses import replace

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.dominio.erros import (
    CredenciaisInvalidas,
    ErroDeAutenticacao,
    ErroDeValidacao,
    UsuarioInativo,
)
from gestao_usuarios.dominio.usuario import Perfil


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def gerenciador() -> GerenciadorDeUsuarios:
    return GerenciadorDeUsuarios(
        RepositorioUsuarioEmMemoria()
    )


@pytest.fixture
def gerenciador_com_usuario(
    gerenciador: GerenciadorDeUsuarios,
) -> GerenciadorDeUsuarios:
    """Gerenciador já populado com um usuário ativo para os testes de login."""
    gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="Senha123!!",
        perfil=Perfil.MEDICO,
    )

    return gerenciador


# ---------------------------------------------------------------------------
# Cenários de sucesso
# ---------------------------------------------------------------------------


def test_autentica_usuario_com_credenciais_validas(
    gerenciador_com_usuario,
):
    """Caminho feliz: credenciais corretas devolvem o usuário autenticado."""
    usuario = gerenciador_com_usuario.autenticar(
        login="ana",
        senha="Senha123!!",
    )

    assert usuario.nome == "Ana Souza"
    assert usuario.login == "ana"
    assert usuario.perfil is Perfil.MEDICO
    assert usuario.ativo is True


# ---------------------------------------------------------------------------
# Pré-condições: ErroDeValidacao (campos obrigatórios)
#
# Taborda: "Seja específico e lance o quanto antes."
# ---------------------------------------------------------------------------


def test_rejeita_login_quando_login_vazio(
    gerenciador_com_usuario,
):
    with pytest.raises(ErroDeValidacao):
        gerenciador_com_usuario.autenticar(
            login="",
            senha="SenhaSecreta1!",
        )


def test_rejeita_login_quando_senha_vazia(
    gerenciador_com_usuario,
):
    with pytest.raises(ErroDeValidacao):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="",
        )


def test_rejeita_login_quando_login_apenas_espacos(
    gerenciador_com_usuario,
):
    with pytest.raises(ErroDeValidacao):
        gerenciador_com_usuario.autenticar(
            login="   ",
            senha="SenhaSecreta1!",
        )


# ---------------------------------------------------------------------------
# Credenciais inválidas: CredenciaisInvalidas
#
# Taborda: exceção específica que revela o problema sem vazar detalhes
# técnicos (não diferenciamos "login errado" de "senha errada").
# PLoP 2018: não usamos Catch Generic — capturamos CredenciaisInvalidas.
# ---------------------------------------------------------------------------


def test_rejeita_login_quando_login_nao_cadastrado(
    gerenciador_com_usuario,
):
    with pytest.raises(CredenciaisInvalidas):
        gerenciador_com_usuario.autenticar(
            login="inexistente",
            senha="Senha123!!",
        )


def test_rejeita_login_quando_senha_incorreta(
    gerenciador_com_usuario,
):
    with pytest.raises(CredenciaisInvalidas):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="senha_errada",
        )


def test_credenciais_invalidas_e_subtipo_de_erro_de_autenticacao(
    gerenciador_com_usuario,
):
    """Verifica a hierarquia: CredenciaisInvalidas IS-A ErroDeAutenticacao.

    Isso valida o princípio de Taborda sobre 'Camadas e exceções': o chamador
    pode capturar ErroDeAutenticacao para tratar qualquer falha de login sem
    precisar conhecer as subclasses.
    """
    with pytest.raises(ErroDeAutenticacao):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="senha_errada",
        )


# ---------------------------------------------------------------------------
# Usuário inativo: UsuarioInativo
#
# Taborda: exceção separada de CredenciaisInvalidas porque a ação corretiva
# é diferente — o admin reativa a conta, não redefine a senha.
# ---------------------------------------------------------------------------


def test_rejeita_login_quando_usuario_inativo(
    gerenciador_com_usuario,
):
    """Usuário inativo com senha correta deve lançar UsuarioInativo."""
    # Obter o usuário e desativá-lo manualmente no repositório (acesso interno)
    repositorio = gerenciador_com_usuario._repositorio

    usuario_ativo = repositorio.buscar_por_login(
        "ana"
    )

    repositorio.salvar(
        replace(
            usuario_ativo,
            ativo=False,
        )
    )

    with pytest.raises(UsuarioInativo):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="Senha123!!",
        )


def test_usuario_inativo_e_subtipo_de_erro_de_autenticacao(
    gerenciador_com_usuario,
):
    """Verifica a hierarquia: UsuarioInativo IS-A ErroDeAutenticacao."""
    repositorio = gerenciador_com_usuario._repositorio

    usuario_ativo = repositorio.buscar_por_login(
        "ana"
    )

    repositorio.salvar(
        replace(
            usuario_ativo,
            ativo=False,
        )
    )

    with pytest.raises(ErroDeAutenticacao):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="Senha123!!",
        )


def test_usuario_inativo_nao_lanca_credenciais_invalidas(
    gerenciador_com_usuario,
):
    """UsuarioInativo e CredenciaisInvalidas são exceções distintas.

    PLoP 2018 — evitar 'isinstance no catch': a distinção é feita pela
    hierarquia de tipos, não por isinstance dentro do handler.
    """
    repositorio = gerenciador_com_usuario._repositorio

    usuario_ativo = repositorio.buscar_por_login(
        "ana"
    )

    repositorio.salvar(
        replace(
            usuario_ativo,
            ativo=False,
        )
    )

    with pytest.raises(UsuarioInativo):
        gerenciador_com_usuario.autenticar(
            login="ana",
            senha="Senha123!!",
        )
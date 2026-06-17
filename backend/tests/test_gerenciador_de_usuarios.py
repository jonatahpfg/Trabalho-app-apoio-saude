import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.dominio.erros import CpfDuplicado, ErroDeValidacao
from gestao_usuarios.dominio.usuario import Perfil


@pytest.fixture
def gerenciador() -> GerenciadorDeUsuarios:
    return GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())


def test_adiciona_usuario_quando_dados_validos(gerenciador):
    usuario = gerenciador.adicionar_usuario(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )

    assert usuario.id == 1
    assert gerenciador.listar_usuarios()[0].nome == "Ana"


def test_rejeita_usuario_quando_cpf_vazio(gerenciador):
    with pytest.raises(ErroDeValidacao):
        gerenciador.adicionar_usuario(
            nome="Ana",
            cpf="",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="Senha123!",
            perfil=Perfil.MEDICO,
        )


def test_rejeita_usuario_quando_cpf_duplicado(gerenciador):
    dados = dict(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )
    gerenciador.adicionar_usuario(**dados)

    with pytest.raises(CpfDuplicado):
        gerenciador.adicionar_usuario(**{**dados, "email": "outra@ubs.gov.br"})


def test_lista_todos_os_usuarios_cadastrados(gerenciador):
    gerenciador.adicionar_usuario(
        nome="Ana",
        cpf="11111111111",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )
    gerenciador.adicionar_usuario(
        nome="Bia",
        cpf="22222222222",
        email="bia@ubs.gov.br",
        telefone="84988887777",
        senha="OutraSenha1!",
        perfil=Perfil.GESTOR,
    )

    assert len(gerenciador.listar_usuarios()) == 2


def test_retorna_lista_vazia_quando_nao_ha_usuarios(gerenciador):
    assert gerenciador.listar_usuarios() == []

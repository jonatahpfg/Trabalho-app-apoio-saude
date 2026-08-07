"""Testes unitários dos comandos de Usuário (Padrão Command)."""

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    ComandoAdicionarUsuario,
    ComandoAutenticar,
    ComandoAutenticarUsuario,
    ComandoListarUsuarios,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
)
from gestao_usuarios.dominio.usuario import Perfil


@pytest.fixture
def gerenciador_usuarios() -> GerenciadorDeUsuarios:
    return GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())


@pytest.fixture
def executor() -> ExecutorDeComandos:
    return ExecutorDeComandos()


def test_comando_adicionar_usuario_com_sucesso(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    assert comando.nome == "Ana Souza"
    assert comando.cpf == "12345678901"
    assert comando.email == "ana@ubs.gov.br"
    assert comando.telefone == "84999990000"
    assert comando.login == "ana"
    assert comando.perfil is Perfil.ADMINISTRADOR

    usuario = executor.executar(comando)

    assert usuario.id is not None
    assert usuario.nome == "Ana Souza"
    assert usuario.login == "ana"
    assert usuario.perfil is Perfil.ADMINISTRADOR
    assert usuario.ativo is True


def test_comando_adicionar_usuario_rejeita_cpf_duplicado(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando1 = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )
    executor.executar(comando1)

    comando_duplicado = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Outra Ana",
        cpf="12345678901",
        email="outra@ubs.gov.br",
        telefone="84988887777",
        login="anasegunda",
        senha="OutraSenha2@",
        perfil=Perfil.GESTOR,
    )

    with pytest.raises(CpfDuplicado):
        executor.executar(comando_duplicado)


def test_comando_adicionar_usuario_rejeita_login_duplicado(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando1 = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )
    executor.executar(comando1)

    comando_duplicado = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Outro Usuario",
        cpf="98765432100",
        email="outro@ubs.gov.br",
        telefone="84988887777",
        login="ana",
        senha="OutraSenha2@",
        perfil=Perfil.GESTOR,
    )

    with pytest.raises(LoginDuplicado):
        executor.executar(comando_duplicado)


def test_comando_adicionar_usuario_rejeita_senha_invalida(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="123",
        perfil=Perfil.ADMINISTRADOR,
    )

    with pytest.raises(ErroDeValidacao):
        executor.executar(comando)


def test_comando_listar_usuarios(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando_listar = ComandoListarUsuarios(gerenciador_usuarios)
    assert executor.executar(comando_listar) == []

    comando_add = ComandoAdicionarUsuario(
        gerenciador_usuarios,
        nome="Bruno Lima",
        cpf="98765432100",
        email="bruno@ubs.gov.br",
        telefone="84988887777",
        login="bruno",
        senha="OutraSenha2@",
        perfil=Perfil.MEDICO,
    )
    executor.executar(comando_add)

    usuarios = executor.executar(comando_listar)
    assert len(usuarios) == 1
    assert usuarios[0].login == "bruno"


def test_comando_autenticar_usuario(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    executor.executar(
        ComandoAdicionarUsuario(
            gerenciador_usuarios,
            nome="Carlos",
            cpf="11122233344",
            email="carlos@ubs.gov.br",
            telefone="84911112222",
            login="carlos",
            senha="SenhaForte1!",
            perfil=Perfil.GESTOR,
        )
    )

    comando_auth = ComandoAutenticarUsuario(
        gerenciador_usuarios,
        login="carlos",
        senha="SenhaForte1!",
    )
    assert comando_auth.login == "carlos"

    autenticado = executor.executar(comando_auth)
    assert autenticado.nome == "Carlos"

    # Teste de alias
    comando_auth_alias = ComandoAutenticar(
        gerenciador_usuarios,
        login="carlos",
        senha="SenhaForte1!",
    )
    assert executor.executar(comando_auth_alias).nome == "Carlos"

    # Teste de falha na autenticação
    comando_invalido = ComandoAutenticarUsuario(
        gerenciador_usuarios,
        login="carlos",
        senha="SenhaErrada1!",
    )
    with pytest.raises(CredenciaisInvalidas):
        executor.executar(comando_invalido)

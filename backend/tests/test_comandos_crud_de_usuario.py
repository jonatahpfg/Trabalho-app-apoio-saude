"""Testes unitários dos comandos de CRUD de Usuário (Padrão Command)."""

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    Comando,
    ComandoAdicionarUsuario,
    ComandoAtualizarUsuario,
    ComandoBuscarUsuarioPorId,
    ComandoBuscarUsuarioPorLogin,
    ComandoDesativarUsuario,
    ComandoListarUsuarios,
    ComandoReativarUsuario,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.dominio.erros import (
    ErroDeValidacao,
    LoginDuplicado,
    UsuarioNaoEncontrado,
)
from gestao_usuarios.dominio.senha import verificar
from gestao_usuarios.dominio.usuario import Perfil


@pytest.fixture
def gerenciador_usuarios() -> GerenciadorDeUsuarios:
    return GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())


@pytest.fixture
def executor() -> ExecutorDeComandos:
    return ExecutorDeComandos()


@pytest.fixture
def usuario_cadastrado(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    return executor.executar(
        ComandoAdicionarUsuario(
            gerenciador_usuarios,
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )
    )


def test_comandos_de_usuario_implementam_a_interface_comando(
    gerenciador_usuarios: GerenciadorDeUsuarios,
):
    comandos = [
        ComandoBuscarUsuarioPorId(gerenciador_usuarios, 1),
        ComandoBuscarUsuarioPorLogin(gerenciador_usuarios, "ana"),
        ComandoDesativarUsuario(gerenciador_usuarios, 1),
        ComandoReativarUsuario(gerenciador_usuarios, 1),
    ]

    assert all(
        isinstance(comando, Comando)
        for comando in comandos
    )


def test_comando_buscar_usuario_por_id_devolve_o_usuario(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoBuscarUsuarioPorId(
        gerenciador_usuarios,
        usuario_cadastrado.id,
    )

    encontrado = executor.executar(comando)

    assert comando.usuario_id == usuario_cadastrado.id
    assert encontrado.nome == "Ana Souza"


def test_comando_buscar_usuario_por_id_inexistente_propaga_o_erro(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando = ComandoBuscarUsuarioPorId(
        gerenciador_usuarios,
        999,
    )

    with pytest.raises(UsuarioNaoEncontrado):
        executor.executar(comando)


def test_comando_buscar_usuario_por_login_devolve_o_usuario(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoBuscarUsuarioPorLogin(
        gerenciador_usuarios,
        "ana",
    )

    encontrado = executor.executar(comando)

    assert comando.login == "ana"
    assert encontrado.id == usuario_cadastrado.id


def test_comando_listar_usuarios_filtra_apenas_ativos(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    executor.executar(
        ComandoDesativarUsuario(
            gerenciador_usuarios,
            usuario_cadastrado.id,
        )
    )

    comando = ComandoListarUsuarios(
        gerenciador_usuarios,
        apenas_ativos=True,
    )

    assert comando.apenas_ativos is True
    assert executor.executar(comando) == []
    assert (
        len(
            executor.executar(
                ComandoListarUsuarios(gerenciador_usuarios)
            )
        )
        == 1
    )


def test_comando_atualizar_usuario_altera_os_dados_cadastrais(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoAtualizarUsuario(
        gerenciador_usuarios,
        usuario_id=usuario_cadastrado.id,
        nome="Ana Maria",
        cpf="98765432100",
        email="ana.maria@ubs.gov.br",
        telefone="84988887777",
        login="anamaria",
        perfil=Perfil.GESTOR,
    )

    atualizado = executor.executar(comando)

    assert comando.usuario_id == usuario_cadastrado.id
    assert comando.nome == "Ana Maria"
    assert comando.cpf == "98765432100"
    assert comando.email == "ana.maria@ubs.gov.br"
    assert comando.telefone == "84988887777"
    assert comando.login == "anamaria"
    assert comando.perfil is Perfil.GESTOR
    assert comando.altera_senha is False

    assert atualizado.nome == "Ana Maria"
    assert atualizado.perfil is Perfil.GESTOR
    assert atualizado.senha_hash == usuario_cadastrado.senha_hash


def test_comando_atualizar_usuario_pode_redefinir_a_senha(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoAtualizarUsuario(
        gerenciador_usuarios,
        usuario_id=usuario_cadastrado.id,
        nome=usuario_cadastrado.nome,
        cpf=usuario_cadastrado.cpf,
        email=usuario_cadastrado.email,
        telefone=usuario_cadastrado.telefone,
        login=usuario_cadastrado.login,
        perfil=usuario_cadastrado.perfil,
        senha="NovaSenha456@",
    )

    atualizado = executor.executar(comando)

    assert comando.altera_senha is True
    assert verificar("NovaSenha456@", atualizado.senha_hash)


def test_comando_atualizar_usuario_propaga_login_duplicado(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    outro = executor.executar(
        ComandoAdicionarUsuario(
            gerenciador_usuarios,
            nome="Bruno Lima",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            login="bruno",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )
    )

    comando = ComandoAtualizarUsuario(
        gerenciador_usuarios,
        usuario_id=outro.id,
        nome=outro.nome,
        cpf=outro.cpf,
        email=outro.email,
        telefone=outro.telefone,
        login="ana",
        perfil=outro.perfil,
    )

    with pytest.raises(LoginDuplicado):
        executor.executar(comando)


def test_comando_atualizar_usuario_propaga_erro_de_validacao(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoAtualizarUsuario(
        gerenciador_usuarios,
        usuario_id=usuario_cadastrado.id,
        nome=usuario_cadastrado.nome,
        cpf=usuario_cadastrado.cpf,
        email=usuario_cadastrado.email,
        telefone=usuario_cadastrado.telefone,
        login="ana2",
        perfil=usuario_cadastrado.perfil,
    )

    with pytest.raises(ErroDeValidacao):
        executor.executar(comando)


def test_comando_desativar_usuario_marca_como_inativo(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    comando = ComandoDesativarUsuario(
        gerenciador_usuarios,
        usuario_cadastrado.id,
    )

    desativado = executor.executar(comando)

    assert comando.usuario_id == usuario_cadastrado.id
    assert desativado.ativo is False


def test_comando_reativar_usuario_marca_como_ativo(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    executor.executar(
        ComandoDesativarUsuario(
            gerenciador_usuarios,
            usuario_cadastrado.id,
        )
    )

    reativado = executor.executar(
        ComandoReativarUsuario(
            gerenciador_usuarios,
            usuario_cadastrado.id,
        )
    )

    assert reativado.ativo is True


def test_executor_registra_os_comandos_de_crud_no_historico(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
    usuario_cadastrado,
):
    executor.executar(
        ComandoBuscarUsuarioPorId(
            gerenciador_usuarios,
            usuario_cadastrado.id,
        )
    )
    executor.executar(
        ComandoDesativarUsuario(
            gerenciador_usuarios,
            usuario_cadastrado.id,
        )
    )

    historico = executor.historico

    assert len(historico) == 3
    assert isinstance(historico[0], ComandoAdicionarUsuario)
    assert isinstance(historico[1], ComandoBuscarUsuarioPorId)
    assert isinstance(
        executor.ultimo_comando,
        ComandoDesativarUsuario,
    )


def test_comando_com_erro_nao_entra_no_historico(
    gerenciador_usuarios: GerenciadorDeUsuarios,
    executor: ExecutorDeComandos,
):
    comando = ComandoBuscarUsuarioPorId(
        gerenciador_usuarios,
        999,
    )

    with pytest.raises(UsuarioNaoEncontrado):
        executor.executar(comando)

    assert executor.historico == []

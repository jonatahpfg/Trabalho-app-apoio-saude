"""CRUD de usuários exercitado nos dois mecanismos de persistência.

Cada cenário roda duas vezes — uma com o repositório em memória (RAM) e
outra com o repositório SQLite — garantindo que os casos de uso se
comportam da mesma forma independentemente do adaptador escolhido.
"""

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_banco_de_dados import (
    RepositorioUsuarioBancoDeDados,
)
from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
    UsuarioInativo,
    UsuarioNaoEncontrado,
)
from gestao_usuarios.dominio.senha import verificar
from gestao_usuarios.dominio.usuario import Perfil


@pytest.fixture(
    params=[
        "memoria",
        "bd",
    ]
)
def gerenciador(request) -> GerenciadorDeUsuarios:
    repositorio = (
        RepositorioUsuarioEmMemoria()
        if request.param == "memoria"
        else RepositorioUsuarioBancoDeDados(":memory:")
    )

    return GerenciadorDeUsuarios(repositorio)


def _adicionar_ana(
    gerenciador: GerenciadorDeUsuarios,
):
    return gerenciador.adicionar_usuario(
        nome="Ana",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )


def _adicionar_bruno(
    gerenciador: GerenciadorDeUsuarios,
):
    return gerenciador.adicionar_usuario(
        nome="Bruno",
        cpf="98765432100",
        email="bruno@ubs.gov.br",
        telefone="84988887777",
        login="bruno",
        senha="OutraSenha2@",
        perfil=Perfil.GESTOR,
    )


# --- Read ---


def test_busca_usuario_por_id(gerenciador):
    salvo = _adicionar_ana(gerenciador)

    encontrado = gerenciador.buscar_usuario_por_id(
        salvo.id
    )

    assert encontrado.id == salvo.id
    assert encontrado.nome == "Ana"
    assert encontrado.login == "ana"


def test_busca_por_id_inexistente_lanca_usuario_nao_encontrado(
    gerenciador,
):
    with pytest.raises(
        UsuarioNaoEncontrado,
        match="999",
    ):
        gerenciador.buscar_usuario_por_id(999)


def test_busca_usuario_por_login(gerenciador):
    salvo = _adicionar_ana(gerenciador)

    encontrado = gerenciador.buscar_usuario_por_login(
        "ana"
    )

    assert encontrado.id == salvo.id


def test_busca_por_login_inexistente_lanca_usuario_nao_encontrado(
    gerenciador,
):
    with pytest.raises(UsuarioNaoEncontrado):
        gerenciador.buscar_usuario_por_login(
            "naoexiste"
        )


def test_busca_por_login_vazio_lanca_erro_de_validacao(
    gerenciador,
):
    with pytest.raises(
        ErroDeValidacao,
        match="login",
    ):
        gerenciador.buscar_usuario_por_login("   ")


def test_lista_apenas_usuarios_ativos_quando_solicitado(
    gerenciador,
):
    ana = _adicionar_ana(gerenciador)
    _adicionar_bruno(gerenciador)

    gerenciador.desativar_usuario(ana.id)

    assert len(gerenciador.listar_usuarios()) == 2

    ativos = gerenciador.listar_usuarios(
        apenas_ativos=True
    )

    assert [usuario.login for usuario in ativos] == [
        "bruno"
    ]


# --- Update ---


def test_atualiza_dados_cadastrais_do_usuario(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    atualizado = gerenciador.atualizar_usuario(
        usuario_id=salvo.id,
        nome="Ana Souza",
        cpf="11122233344",
        email="ana.souza@ubs.gov.br",
        telefone="84900001111",
        login="anasouza",
        perfil=Perfil.ADMINISTRADOR,
    )

    assert atualizado.id == salvo.id
    assert atualizado.nome == "Ana Souza"
    assert atualizado.cpf == "11122233344"
    assert atualizado.email == "ana.souza@ubs.gov.br"
    assert atualizado.telefone == "84900001111"
    assert atualizado.login == "anasouza"
    assert atualizado.perfil is Perfil.ADMINISTRADOR


def test_atualizacao_persiste_no_repositorio(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    gerenciador.atualizar_usuario(
        usuario_id=salvo.id,
        nome="Ana Souza",
        cpf=salvo.cpf,
        email=salvo.email,
        telefone=salvo.telefone,
        login="anasouza",
        perfil=salvo.perfil,
    )

    recarregado = gerenciador.buscar_usuario_por_id(
        salvo.id
    )

    assert recarregado.nome == "Ana Souza"
    assert recarregado.login == "anasouza"
    assert len(gerenciador.listar_usuarios()) == 1


def test_atualizacao_sem_senha_preserva_a_senha_atual(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    atualizado = gerenciador.atualizar_usuario(
        usuario_id=salvo.id,
        nome="Ana Souza",
        cpf=salvo.cpf,
        email=salvo.email,
        telefone=salvo.telefone,
        login=salvo.login,
        perfil=salvo.perfil,
    )

    assert atualizado.senha_hash == salvo.senha_hash
    assert gerenciador.autenticar(
        login="ana",
        senha="Senha123!",
    )


def test_atualizacao_com_senha_gera_novo_hash(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    atualizado = gerenciador.atualizar_usuario(
        usuario_id=salvo.id,
        nome=salvo.nome,
        cpf=salvo.cpf,
        email=salvo.email,
        telefone=salvo.telefone,
        login=salvo.login,
        perfil=salvo.perfil,
        senha="NovaSenha456@",
    )

    assert verificar(
        "NovaSenha456@",
        atualizado.senha_hash,
    )

    with pytest.raises(CredenciaisInvalidas):
        gerenciador.autenticar(
            login="ana",
            senha="Senha123!",
        )


def test_atualizacao_mantendo_os_proprios_dados_nao_acusa_duplicidade(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    atualizado = gerenciador.atualizar_usuario(
        usuario_id=salvo.id,
        nome="Ana Souza",
        cpf=salvo.cpf,
        email=salvo.email,
        telefone=salvo.telefone,
        login=salvo.login,
        perfil=salvo.perfil,
    )

    assert atualizado.cpf == salvo.cpf
    assert atualizado.login == salvo.login


def test_atualizacao_rejeita_cpf_de_outro_usuario(
    gerenciador,
):
    ana = _adicionar_ana(gerenciador)
    bruno = _adicionar_bruno(gerenciador)

    with pytest.raises(CpfDuplicado):
        gerenciador.atualizar_usuario(
            usuario_id=bruno.id,
            nome=bruno.nome,
            cpf=ana.cpf,
            email=bruno.email,
            telefone=bruno.telefone,
            login=bruno.login,
            perfil=bruno.perfil,
        )


def test_atualizacao_rejeita_login_de_outro_usuario(
    gerenciador,
):
    ana = _adicionar_ana(gerenciador)
    bruno = _adicionar_bruno(gerenciador)

    with pytest.raises(LoginDuplicado):
        gerenciador.atualizar_usuario(
            usuario_id=bruno.id,
            nome=bruno.nome,
            cpf=bruno.cpf,
            email=bruno.email,
            telefone=bruno.telefone,
            login=ana.login,
            perfil=bruno.perfil,
        )


def test_atualizacao_rejeita_login_com_numeros(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    with pytest.raises(
        ErroDeValidacao,
        match="não pode conter números",
    ):
        gerenciador.atualizar_usuario(
            usuario_id=salvo.id,
            nome=salvo.nome,
            cpf=salvo.cpf,
            email=salvo.email,
            telefone=salvo.telefone,
            login="ana2",
            perfil=salvo.perfil,
        )


def test_atualizacao_invalida_nao_altera_o_cadastro(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    with pytest.raises(ErroDeValidacao):
        gerenciador.atualizar_usuario(
            usuario_id=salvo.id,
            nome="Ana Souza",
            cpf=salvo.cpf,
            email="email-invalido",
            telefone=salvo.telefone,
            login=salvo.login,
            perfil=salvo.perfil,
        )

    inalterado = gerenciador.buscar_usuario_por_id(
        salvo.id
    )

    assert inalterado.nome == "Ana"
    assert inalterado.email == "ana@ubs.gov.br"


def test_atualizacao_de_usuario_inexistente_lanca_usuario_nao_encontrado(
    gerenciador,
):
    with pytest.raises(UsuarioNaoEncontrado):
        gerenciador.atualizar_usuario(
            usuario_id=999,
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            perfil=Perfil.MEDICO,
        )


# --- Delete lógico ---


def test_desativa_usuario_sem_apagar_o_registro(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    desativado = gerenciador.desativar_usuario(
        salvo.id
    )

    assert desativado.ativo is False
    assert len(gerenciador.listar_usuarios()) == 1
    assert (
        gerenciador.buscar_usuario_por_id(
            salvo.id
        ).ativo
        is False
    )


def test_usuario_desativado_nao_consegue_autenticar(
    gerenciador,
):
    salvo = _adicionar_ana(gerenciador)

    gerenciador.desativar_usuario(salvo.id)

    with pytest.raises(UsuarioInativo):
        gerenciador.autenticar(
            login="ana",
            senha="Senha123!",
        )


def test_desativacao_de_usuario_inexistente_lanca_usuario_nao_encontrado(
    gerenciador,
):
    with pytest.raises(UsuarioNaoEncontrado):
        gerenciador.desativar_usuario(999)


def test_reativa_usuario_desativado(gerenciador):
    salvo = _adicionar_ana(gerenciador)

    gerenciador.desativar_usuario(salvo.id)
    reativado = gerenciador.reativar_usuario(salvo.id)

    assert reativado.ativo is True
    assert gerenciador.autenticar(
        login="ana",
        senha="Senha123!",
    )

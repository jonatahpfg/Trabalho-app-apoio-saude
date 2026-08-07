"""Testes unitários para ProxyGerenciadorDeUsuarios — padrão Proxy (Sprint 6)."""

from __future__ import annotations

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.aplicacao.proxy.gerenciador_usuarios_proxy import (
    ProxyGerenciadorDeUsuarios,
)
from gestao_usuarios.dominio.erros import AcessoNegado
from gestao_usuarios.dominio.usuario import Perfil, Usuario


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _criar_usuario(perfil: Perfil, login: str = "user") -> Usuario:
    """Cria um usuário com o perfil informado para injetar no Proxy."""
    return Usuario(
        nome="Teste",
        cpf="00000000001",
        email="teste@ubs.gov.br",
        telefone="84900000000",
        login=login,
        senha_hash="hash",
        perfil=perfil,
        ativo=True,
        id=1,
    )


@pytest.fixture()
def repositorio():
    return RepositorioUsuarioEmMemoria()


@pytest.fixture()
def gerenciador(repositorio):
    return GerenciadorDeUsuarios(repositorio)


@pytest.fixture()
def proxy_admin(gerenciador):
    return ProxyGerenciadorDeUsuarios(
        gerenciador, _criar_usuario(Perfil.ADMINISTRADOR, "admin")
    )


@pytest.fixture()
def proxy_gestor(gerenciador):
    return ProxyGerenciadorDeUsuarios(
        gerenciador, _criar_usuario(Perfil.GESTOR, "gestor")
    )


@pytest.fixture()
def proxy_medico(gerenciador):
    return ProxyGerenciadorDeUsuarios(
        gerenciador, _criar_usuario(Perfil.MEDICO, "medico")
    )


# ---------------------------------------------------------------------------
# adicionar_usuario
# ---------------------------------------------------------------------------


class TestAdicionarUsuario:
    def test_administrador_pode_adicionar(self, proxy_admin):
        usuario = proxy_admin.adicionar_usuario(
            nome="João Silva",
            cpf="12345678901",
            email="joao@ubs.gov.br",
            telefone="84999990000",
            login="joao",
            senha="SenhaForte1!",
            perfil=Perfil.MEDICO,
        )
        assert usuario.login == "joao"

    def test_gestor_nao_pode_adicionar(self, proxy_gestor):
        with pytest.raises(AcessoNegado, match="adicionar_usuario"):
            proxy_gestor.adicionar_usuario(
                nome="X",
                cpf="00000000002",
                email="x@ubs.gov.br",
                telefone="84900000001",
                login="x",
                senha="SenhaForte1!",
                perfil=Perfil.MEDICO,
            )

    def test_medico_nao_pode_adicionar(self, proxy_medico):
        with pytest.raises(AcessoNegado, match="MEDICO"):
            proxy_medico.adicionar_usuario(
                nome="Y",
                cpf="00000000003",
                email="y@ubs.gov.br",
                telefone="84900000002",
                login="y",
                senha="SenhaForte1!",
                perfil=Perfil.MEDICO,
            )


# ---------------------------------------------------------------------------
# listar_usuarios
# ---------------------------------------------------------------------------


class TestListarUsuarios:
    def test_administrador_pode_listar(self, proxy_admin):
        resultado = proxy_admin.listar_usuarios()
        assert isinstance(resultado, list)

    def test_gestor_pode_listar(self, proxy_gestor):
        resultado = proxy_gestor.listar_usuarios()
        assert isinstance(resultado, list)

    def test_medico_nao_pode_listar(self, proxy_medico):
        with pytest.raises(AcessoNegado, match="listar_usuarios"):
            proxy_medico.listar_usuarios()


# ---------------------------------------------------------------------------
# CRUD de usuário — busca, atualização e desativação
# ---------------------------------------------------------------------------


def _cadastrar_usuario(proxy_admin) -> Usuario:
    """Cadastra um usuário pelo Proxy do ADMINISTRADOR."""
    return proxy_admin.adicionar_usuario(
        nome="João Silva",
        cpf="12345678901",
        email="joao@ubs.gov.br",
        telefone="84999990000",
        login="joao",
        senha="SenhaForte1!",
        perfil=Perfil.MEDICO,
    )


class TestBuscarUsuario:
    def test_administrador_pode_buscar_por_id(self, proxy_admin):
        cadastrado = _cadastrar_usuario(proxy_admin)

        assert (
            proxy_admin.buscar_usuario_por_id(cadastrado.id).login
            == "joao"
        )

    def test_gestor_pode_buscar_por_id(self, proxy_admin, proxy_gestor):
        cadastrado = _cadastrar_usuario(proxy_admin)

        assert (
            proxy_gestor.buscar_usuario_por_id(cadastrado.id).login
            == "joao"
        )

    def test_medico_nao_pode_buscar_por_id(self, proxy_admin, proxy_medico):
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="buscar_usuario_por_id"):
            proxy_medico.buscar_usuario_por_id(cadastrado.id)

    def test_administrador_pode_buscar_por_login(self, proxy_admin):
        _cadastrar_usuario(proxy_admin)

        assert (
            proxy_admin.buscar_usuario_por_login("joao").login == "joao"
        )

    def test_gestor_pode_buscar_por_login(self, proxy_admin, proxy_gestor):
        _cadastrar_usuario(proxy_admin)

        assert (
            proxy_gestor.buscar_usuario_por_login("joao").login == "joao"
        )

    def test_medico_nao_pode_buscar_por_login(self, proxy_admin, proxy_medico):
        _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="buscar_usuario_por_login"):
            proxy_medico.buscar_usuario_por_login("joao")


class TestAtualizarUsuario:
    def test_administrador_pode_atualizar(self, proxy_admin):
        cadastrado = _cadastrar_usuario(proxy_admin)

        atualizado = proxy_admin.atualizar_usuario(
            usuario_id=cadastrado.id,
            nome="João da Silva",
            cpf=cadastrado.cpf,
            email=cadastrado.email,
            telefone=cadastrado.telefone,
            login="joaosilva",
            perfil=Perfil.GESTOR,
        )

        assert atualizado.login == "joaosilva"
        assert atualizado.perfil is Perfil.GESTOR

    def test_gestor_nao_pode_atualizar(self, proxy_admin, proxy_gestor):
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="atualizar_usuario"):
            proxy_gestor.atualizar_usuario(
                usuario_id=cadastrado.id,
                nome="João da Silva",
                cpf=cadastrado.cpf,
                email=cadastrado.email,
                telefone=cadastrado.telefone,
                login="joaosilva",
                perfil=Perfil.GESTOR,
            )

    def test_medico_nao_pode_se_promover_a_administrador(
        self,
        proxy_admin,
        proxy_medico,
    ):
        """A escalada de privilégio é barrada antes de alcançar o gerenciador."""
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="MEDICO"):
            proxy_medico.atualizar_usuario(
                usuario_id=cadastrado.id,
                nome=cadastrado.nome,
                cpf=cadastrado.cpf,
                email=cadastrado.email,
                telefone=cadastrado.telefone,
                login=cadastrado.login,
                perfil=Perfil.ADMINISTRADOR,
            )

        assert (
            proxy_admin.buscar_usuario_por_id(cadastrado.id).perfil
            is Perfil.MEDICO
        )

    def test_perfil_nao_autorizado_nao_redefine_senha(
        self,
        proxy_admin,
        proxy_gestor,
    ):
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado):
            proxy_gestor.atualizar_usuario(
                usuario_id=cadastrado.id,
                nome=cadastrado.nome,
                cpf=cadastrado.cpf,
                email=cadastrado.email,
                telefone=cadastrado.telefone,
                login=cadastrado.login,
                perfil=cadastrado.perfil,
                senha="SenhaInvadida9$",
            )

        assert (
            proxy_admin.buscar_usuario_por_id(cadastrado.id).senha_hash
            == cadastrado.senha_hash
        )


class TestDesativarEReativarUsuario:
    def test_administrador_pode_desativar(self, proxy_admin):
        cadastrado = _cadastrar_usuario(proxy_admin)

        assert (
            proxy_admin.desativar_usuario(cadastrado.id).ativo is False
        )

    def test_administrador_pode_reativar(self, proxy_admin):
        cadastrado = _cadastrar_usuario(proxy_admin)

        proxy_admin.desativar_usuario(cadastrado.id)

        assert proxy_admin.reativar_usuario(cadastrado.id).ativo is True

    def test_gestor_nao_pode_desativar(self, proxy_admin, proxy_gestor):
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="desativar_usuario"):
            proxy_gestor.desativar_usuario(cadastrado.id)

        assert (
            proxy_admin.buscar_usuario_por_id(cadastrado.id).ativo is True
        )

    def test_medico_nao_pode_desativar(self, proxy_admin, proxy_medico):
        cadastrado = _cadastrar_usuario(proxy_admin)

        with pytest.raises(AcessoNegado, match="MEDICO"):
            proxy_medico.desativar_usuario(cadastrado.id)

    def test_gestor_nao_pode_reativar(self, proxy_admin, proxy_gestor):
        cadastrado = _cadastrar_usuario(proxy_admin)

        proxy_admin.desativar_usuario(cadastrado.id)

        with pytest.raises(AcessoNegado, match="reativar_usuario"):
            proxy_gestor.reativar_usuario(cadastrado.id)


class TestListagemFiltrada:
    def test_filtro_apenas_ativos_e_repassado_ao_gerenciador(
        self,
        proxy_admin,
    ):
        cadastrado = _cadastrar_usuario(proxy_admin)

        proxy_admin.desativar_usuario(cadastrado.id)

        assert len(proxy_admin.listar_usuarios()) == 1
        assert proxy_admin.listar_usuarios(apenas_ativos=True) == []


# ---------------------------------------------------------------------------
# autenticar (operação pública — sem restrição de perfil)
# ---------------------------------------------------------------------------


class TestAutenticarSemRestricao:
    """autenticar não exige perfil — qualquer usuário pode chamar."""

    def _popular_repo(self, gerenciador):
        gerenciador.adicionar_usuario(
            nome="Maria",
            cpf="99988877766",
            email="maria@ubs.gov.br",
            telefone="84911112222",
            login="maria",
            senha="SenhaForte9!",
            perfil=Perfil.MEDICO,
        )

    def test_medico_pode_autenticar(self, gerenciador, proxy_medico):
        self._popular_repo(gerenciador)
        usuario = proxy_medico.autenticar(login="maria", senha="SenhaForte9!")
        assert usuario.login == "maria"

    def test_gestor_pode_autenticar(self, gerenciador, proxy_gestor):
        self._popular_repo(gerenciador)
        usuario = proxy_gestor.autenticar(login="maria", senha="SenhaForte9!")
        assert usuario.login == "maria"

    def test_administrador_pode_autenticar(self, gerenciador, proxy_admin):
        self._popular_repo(gerenciador)
        usuario = proxy_admin.autenticar(login="maria", senha="SenhaForte9!")
        assert usuario.login == "maria"


# ---------------------------------------------------------------------------
# Mensagem de AcessoNegado
# ---------------------------------------------------------------------------


class TestMensagemAcessoNegado:
    def test_mensagem_contem_perfil_e_operacao(self, proxy_medico):
        with pytest.raises(AcessoNegado) as exc_info:
            proxy_medico.listar_usuarios()

        mensagem = str(exc_info.value)
        assert "MEDICO" in mensagem
        assert "listar_usuarios" in mensagem

    def test_mensagem_contem_perfis_autorizados(self, proxy_medico):
        with pytest.raises(AcessoNegado) as exc_info:
            proxy_medico.adicionar_usuario(
                nome="Z",
                cpf="00000000004",
                email="z@ubs.gov.br",
                telefone="84900000003",
                login="z",
                senha="SenhaForte1!",
                perfil=Perfil.MEDICO,
            )

        mensagem = str(exc_info.value)
        assert "ADMINISTRADOR" in mensagem

"""Testes unitários para ProxyGerenciadorDeUnidades — padrão Proxy (Sprint 6)."""

from __future__ import annotations

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from gestao_usuarios.aplicacao.proxy.gerenciador_unidades_proxy import (
    ProxyGerenciadorDeUnidades,
)
from gestao_usuarios.dominio.erros import AcessoNegado
from gestao_usuarios.dominio.usuario import Perfil, Usuario


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _criar_usuario(perfil: Perfil, login: str = "user") -> Usuario:
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
def gerenciador():
    return GerenciadorDeUnidades(RepositorioUnidadeEmMemoria())


@pytest.fixture()
def proxy_admin(gerenciador):
    return ProxyGerenciadorDeUnidades(
        gerenciador, _criar_usuario(Perfil.ADMINISTRADOR, "admin")
    )


@pytest.fixture()
def proxy_gestor(gerenciador):
    return ProxyGerenciadorDeUnidades(
        gerenciador, _criar_usuario(Perfil.GESTOR, "gestor")
    )


@pytest.fixture()
def proxy_medico(gerenciador):
    return ProxyGerenciadorDeUnidades(
        gerenciador, _criar_usuario(Perfil.MEDICO, "medico")
    )


def _dados_ubs(sufixo: str = "01") -> dict:
    return {
        "nome": f"UBS Teste {sufixo}",
        "cnpj": f"112223330001{sufixo}",
        "endereco": "Rua Teste, 1",
        "telefone": "84333334444",
    }


# ---------------------------------------------------------------------------
# adicionar_unidade
# ---------------------------------------------------------------------------


class TestAdicionarUnidade:
    def test_administrador_pode_adicionar(self, proxy_admin):
        ubs = proxy_admin.adicionar_unidade(**_dados_ubs("81"))
        assert ubs.nome == "UBS Teste 81"

    def test_gestor_pode_adicionar(self, proxy_gestor):
        ubs = proxy_gestor.adicionar_unidade(**_dados_ubs("82"))
        assert ubs.nome == "UBS Teste 82"

    def test_medico_nao_pode_adicionar(self, proxy_medico):
        with pytest.raises(AcessoNegado, match="adicionar_unidade"):
            proxy_medico.adicionar_unidade(**_dados_ubs("83"))


# ---------------------------------------------------------------------------
# listar_unidades
# ---------------------------------------------------------------------------


class TestListarUnidades:
    def test_administrador_pode_listar(self, proxy_admin):
        assert isinstance(proxy_admin.listar_unidades(), list)

    def test_gestor_pode_listar(self, proxy_gestor):
        assert isinstance(proxy_gestor.listar_unidades(), list)

    def test_medico_pode_listar(self, proxy_medico):
        assert isinstance(proxy_medico.listar_unidades(), list)


# ---------------------------------------------------------------------------
# buscar_unidade_por_id
# ---------------------------------------------------------------------------


class TestBuscarUnidadePorId:
    def _criar_ubs(self, proxy_admin):
        return proxy_admin.adicionar_unidade(**_dados_ubs("91"))

    def test_administrador_pode_buscar(self, proxy_admin):
        ubs = self._criar_ubs(proxy_admin)
        resultado = proxy_admin.buscar_unidade_por_id(ubs.id)
        assert resultado.id == ubs.id

    def test_gestor_pode_buscar(self, proxy_admin, proxy_gestor):
        ubs = self._criar_ubs(proxy_admin)
        resultado = proxy_gestor.buscar_unidade_por_id(ubs.id)
        assert resultado.id == ubs.id

    def test_medico_pode_buscar(self, proxy_admin, proxy_medico):
        ubs = self._criar_ubs(proxy_admin)
        resultado = proxy_medico.buscar_unidade_por_id(ubs.id)
        assert resultado.id == ubs.id


# ---------------------------------------------------------------------------
# atualizar_unidade
# ---------------------------------------------------------------------------


class TestAtualizarUnidade:
    def _criar_ubs(self, proxy_admin):
        return proxy_admin.adicionar_unidade(**_dados_ubs("71"))

    def test_administrador_pode_atualizar(self, proxy_admin):
        ubs = self._criar_ubs(proxy_admin)
        atualizada = proxy_admin.atualizar_unidade(
            unidade_id=ubs.id,
            nome="UBS Atualizada",
            cnpj=ubs.cnpj,
            endereco="Rua Nova, 2",
            telefone="84300000001",
        )
        assert atualizada.nome == "UBS Atualizada"

    def test_gestor_pode_atualizar(self, proxy_admin, proxy_gestor):
        ubs = self._criar_ubs(proxy_admin)
        atualizada = proxy_gestor.atualizar_unidade(
            unidade_id=ubs.id,
            nome="UBS Gestor Update",
            cnpj=ubs.cnpj,
            endereco="Av. Central, 3",
            telefone="84300000002",
        )
        assert atualizada.nome == "UBS Gestor Update"

    def test_medico_nao_pode_atualizar(self, proxy_admin, proxy_medico):
        ubs = self._criar_ubs(proxy_admin)
        with pytest.raises(AcessoNegado, match="atualizar_unidade"):
            proxy_medico.atualizar_unidade(
                unidade_id=ubs.id,
                nome="UBS Alterada",
                cnpj=ubs.cnpj,
                endereco="Rua X, 1",
                telefone="84300000003",
            )


# ---------------------------------------------------------------------------
# remover_unidade
# ---------------------------------------------------------------------------


class TestRemoverUnidade:
    def _criar_ubs(self, proxy_admin):
        return proxy_admin.adicionar_unidade(**_dados_ubs("61"))

    def test_administrador_pode_remover(self, proxy_admin):
        ubs = self._criar_ubs(proxy_admin)
        removida = proxy_admin.remover_unidade(ubs.id)
        assert removida.ativa is False

    def test_gestor_nao_pode_remover(self, proxy_admin, proxy_gestor):
        ubs = self._criar_ubs(proxy_admin)
        with pytest.raises(AcessoNegado, match="remover_unidade"):
            proxy_gestor.remover_unidade(ubs.id)

    def test_medico_nao_pode_remover(self, proxy_admin, proxy_medico):
        ubs = self._criar_ubs(proxy_admin)
        with pytest.raises(AcessoNegado, match="remover_unidade"):
            proxy_medico.remover_unidade(ubs.id)


# ---------------------------------------------------------------------------
# Mensagem de AcessoNegado
# ---------------------------------------------------------------------------


class TestMensagemAcessoNegado:
    def test_mensagem_contem_perfil_e_operacao(self, proxy_medico):
        with pytest.raises(AcessoNegado) as exc_info:
            proxy_medico.adicionar_unidade(**_dados_ubs("51"))

        mensagem = str(exc_info.value)
        assert "MEDICO" in mensagem
        assert "adicionar_unidade" in mensagem

    def test_mensagem_remover_exige_so_admin(self, proxy_gestor, proxy_admin):
        ubs = proxy_admin.adicionar_unidade(**_dados_ubs("41"))
        with pytest.raises(AcessoNegado) as exc_info:
            proxy_gestor.remover_unidade(ubs.id)

        mensagem = str(exc_info.value)
        assert "ADMINISTRADOR" in mensagem

"""Testes unitários para o padrão Observer de autenticação (Sprint 6).

Testa:
- PublicadorDeEventosDeAutenticacao (Subject)
- ObservadorDeLogDeAutenticacao (Concrete Observer)
- ObservadorDeEstatisticasDeAutenticacao (Concrete Observer)
- Integração com GerenciadorDeUsuarios
"""

from __future__ import annotations

import pytest

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.aplicacao.observer.evento import EventoDeAutenticacao
from gestao_usuarios.aplicacao.observer.observador_de_estatisticas import (
    ObservadorDeEstatisticasDeAutenticacao,
)
from gestao_usuarios.aplicacao.observer.observador_de_log import (
    ObservadorDeLogDeAutenticacao,
)
from gestao_usuarios.aplicacao.observer.publicador import (
    PublicadorDeEventosDeAutenticacao,
)
from gestao_usuarios.dominio.erros import CredenciaisInvalidas
from gestao_usuarios.dominio.usuario import Perfil


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def publicador():
    return PublicadorDeEventosDeAutenticacao()


@pytest.fixture()
def obs_log():
    return ObservadorDeLogDeAutenticacao()


@pytest.fixture()
def obs_stats():
    return ObservadorDeEstatisticasDeAutenticacao()


@pytest.fixture()
def evento_sucesso():
    return EventoDeAutenticacao(login="ana", sucesso=True)


@pytest.fixture()
def evento_falha():
    return EventoDeAutenticacao(login="ana", sucesso=False)


# ---------------------------------------------------------------------------
# PublicadorDeEventosDeAutenticacao
# ---------------------------------------------------------------------------


class TestPublicador:
    def test_assinar_incrementa_total(self, publicador, obs_log):
        publicador.assinar(obs_log)
        assert publicador.total_observadores == 1

    def test_assinar_mesmo_duas_vezes_nao_duplica(self, publicador, obs_log):
        publicador.assinar(obs_log)
        publicador.assinar(obs_log)
        assert publicador.total_observadores == 1

    def test_cancelar_assinatura_remove(self, publicador, obs_log):
        publicador.assinar(obs_log)
        publicador.cancelar_assinatura(obs_log)
        assert publicador.total_observadores == 0

    def test_cancelar_nao_inscrito_nao_lanca(self, publicador, obs_log):
        publicador.cancelar_assinatura(obs_log)  # não deve lançar

    def test_notificar_aciona_observador(self, publicador, obs_log, evento_sucesso):
        publicador.assinar(obs_log)
        publicador.notificar(evento_sucesso)
        assert len(obs_log.historico) == 1
        assert obs_log.historico[0].login == "ana"

    def test_notificar_sem_observadores_nao_lanca(self, publicador, evento_sucesso):
        publicador.notificar(evento_sucesso)  # não deve lançar

    def test_notificar_multiplos_observadores(
        self, publicador, obs_log, obs_stats, evento_sucesso
    ):
        publicador.assinar(obs_log)
        publicador.assinar(obs_stats)
        publicador.notificar(evento_sucesso)
        assert len(obs_log.historico) == 1
        assert obs_stats.total_tentativas == 1

    def test_observador_removido_nao_recebe(
        self, publicador, obs_log, evento_sucesso
    ):
        publicador.assinar(obs_log)
        publicador.cancelar_assinatura(obs_log)
        publicador.notificar(evento_sucesso)
        assert len(obs_log.historico) == 0


# ---------------------------------------------------------------------------
# ObservadorDeLogDeAutenticacao
# ---------------------------------------------------------------------------


class TestObservadorDeLog:
    def test_registra_evento_sucesso(self, obs_log, evento_sucesso):
        obs_log.atualizar(evento_sucesso)
        assert len(obs_log.historico) == 1
        assert obs_log.historico[0].sucesso is True

    def test_registra_evento_falha(self, obs_log, evento_falha):
        obs_log.atualizar(evento_falha)
        assert obs_log.historico[0].sucesso is False

    def test_acumula_multiplos_eventos(self, obs_log, evento_sucesso, evento_falha):
        obs_log.atualizar(evento_sucesso)
        obs_log.atualizar(evento_falha)
        assert len(obs_log.historico) == 2

    def test_historico_e_copia(self, obs_log, evento_sucesso):
        obs_log.atualizar(evento_sucesso)
        copia = obs_log.historico
        copia.clear()
        assert len(obs_log.historico) == 1  # original intacto

    def test_limpar_esvazia_historico(self, obs_log, evento_sucesso):
        obs_log.atualizar(evento_sucesso)
        obs_log.limpar()
        assert len(obs_log.historico) == 0


# ---------------------------------------------------------------------------
# ObservadorDeEstatisticasDeAutenticacao
# ---------------------------------------------------------------------------


class TestObservadorDeEstatisticas:
    def test_inicia_zerado(self, obs_stats):
        assert obs_stats.total_tentativas == 0
        assert obs_stats.total_sucessos == 0
        assert obs_stats.total_falhas == 0

    def test_conta_sucesso(self, obs_stats, evento_sucesso):
        obs_stats.atualizar(evento_sucesso)
        assert obs_stats.total_tentativas == 1
        assert obs_stats.total_sucessos == 1
        assert obs_stats.total_falhas == 0

    def test_conta_falha(self, obs_stats, evento_falha):
        obs_stats.atualizar(evento_falha)
        assert obs_stats.total_tentativas == 1
        assert obs_stats.total_sucessos == 0
        assert obs_stats.total_falhas == 1

    def test_acumula_varios(self, obs_stats, evento_sucesso, evento_falha):
        obs_stats.atualizar(evento_sucesso)
        obs_stats.atualizar(evento_sucesso)
        obs_stats.atualizar(evento_falha)
        assert obs_stats.total_tentativas == 3
        assert obs_stats.total_sucessos == 2
        assert obs_stats.total_falhas == 1

    def test_resumo_retorna_dict(self, obs_stats, evento_sucesso, evento_falha):
        obs_stats.atualizar(evento_sucesso)
        obs_stats.atualizar(evento_falha)
        resumo = obs_stats.resumo()
        assert resumo == {"total": 2, "sucessos": 1, "falhas": 1}

    def test_zerar_reinicia_contadores(self, obs_stats, evento_sucesso):
        obs_stats.atualizar(evento_sucesso)
        obs_stats.zerar()
        assert obs_stats.total_tentativas == 0
        assert obs_stats.total_sucessos == 0
        assert obs_stats.total_falhas == 0


# ---------------------------------------------------------------------------
# Integração Observer + GerenciadorDeUsuarios
# ---------------------------------------------------------------------------


class TestIntegracaoObserverGerenciador:
    """Garante que o GerenciadorDeUsuarios notifica o publicador corretamente."""

    @pytest.fixture()
    def gerenciador_com_observer(self, publicador, obs_stats):
        publicador.assinar(obs_stats)
        repositorio = RepositorioUsuarioEmMemoria()
        ger = GerenciadorDeUsuarios(repositorio, publicador=publicador)
        ger.adicionar_usuario(
            nome="Maria",
            cpf="99988877766",
            email="maria@ubs.gov.br",
            telefone="84911112222",
            login="maria",
            senha="SenhaForte9!",
            perfil=Perfil.MEDICO,
        )
        return ger, obs_stats

    def test_login_correto_publica_sucesso(self, gerenciador_com_observer):
        ger, stats = gerenciador_com_observer
        ger.autenticar(login="maria", senha="SenhaForte9!")
        assert stats.total_sucessos == 1
        assert stats.total_falhas == 0

    def test_login_errado_publica_falha(self, gerenciador_com_observer):
        ger, stats = gerenciador_com_observer
        with pytest.raises(CredenciaisInvalidas):
            ger.autenticar(login="maria", senha="errada")
        assert stats.total_sucessos == 0
        assert stats.total_falhas == 1

    def test_multiplos_logins_acumula(self, gerenciador_com_observer):
        ger, stats = gerenciador_com_observer
        ger.autenticar(login="maria", senha="SenhaForte9!")
        with pytest.raises(CredenciaisInvalidas):
            ger.autenticar(login="maria", senha="errada")
        with pytest.raises(CredenciaisInvalidas):
            ger.autenticar(login="naoexiste", senha="qualquer")
        assert stats.total_tentativas == 3
        assert stats.total_sucessos == 1
        assert stats.total_falhas == 2

    def test_sem_publicador_funciona_normalmente(self):
        """GerenciadorDeUsuarios sem publicador não lança erro."""
        repositorio = RepositorioUsuarioEmMemoria()
        ger = GerenciadorDeUsuarios(repositorio)  # sem publicador
        ger.adicionar_usuario(
            nome="Pedro",
            cpf="11100022233",
            email="pedro@ubs.gov.br",
            telefone="84922223333",
            login="pedro",
            senha="SenhaForte9!",
            perfil=Perfil.MEDICO,
        )
        usuario = ger.autenticar(login="pedro", senha="SenhaForte9!")
        assert usuario.login == "pedro"

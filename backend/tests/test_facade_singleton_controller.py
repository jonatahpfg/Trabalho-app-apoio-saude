"""Testes do FacadeSingletonController.

Verificam:
  - Singleton: instancia() sempre devolve o mesmo objeto.
  - Facade:    os três casos de uso (adicionar, listar, autenticar)
               funcionam corretamente por meio da fachada.
"""

import pytest

from gestao_usuarios.aplicacao.facade_singleton_controller import (
    FacadeSingletonController,
)
from gestao_usuarios.dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    UsuarioInativo,
)
from gestao_usuarios.dominio.usuario import Perfil


# ------------------------------------------------------------------ #
# Fixture: garante estado limpo entre os testes                       #
# ------------------------------------------------------------------ #

@pytest.fixture(autouse=True)
def limpar_singleton():
    """Reseta a instância única antes (e depois) de cada teste."""
    FacadeSingletonController.resetar_instancia()
    yield
    FacadeSingletonController.resetar_instancia()


# ------------------------------------------------------------------ #
# Testes do padrão Singleton                                          #
# ------------------------------------------------------------------ #

class TestSingleton:
    def test_instancia_retorna_sempre_o_mesmo_objeto(self):
        """Duas chamadas a instancia() devem devolver o mesmo objeto."""
        a = FacadeSingletonController.instancia()
        b = FacadeSingletonController.instancia()
        assert a is b

    def test_resetar_permite_nova_instancia(self):
        """Após resetar_instancia(), uma nova instância deve ser criada."""
        primeira = FacadeSingletonController.instancia()
        FacadeSingletonController.resetar_instancia()
        segunda = FacadeSingletonController.instancia()
        assert primeira is not segunda

    def test_instancia_diferente_apos_reset_nao_compartilha_dados(self):
        """Após o reset, a nova instância começa com repositório vazio."""
        facade = FacadeSingletonController.instancia()
        facade.adicionar_usuario(
            nome="Carlos",
            cpf="11122233344",
            email="carlos@ubs.gov.br",
            telefone="84911112222",
            senha="SenhaForte1!",
            perfil=Perfil.MEDICO,
        )
        assert len(facade.listar_usuarios()) == 1

        FacadeSingletonController.resetar_instancia()
        nova_facade = FacadeSingletonController.instancia()
        assert len(nova_facade.listar_usuarios()) == 0


# ------------------------------------------------------------------ #
# Testes do padrão Facade — adicionar_usuario                         #
# ------------------------------------------------------------------ #

class TestFacadeAdicionarUsuario:
    def test_adiciona_usuario_valido(self):
        facade = FacadeSingletonController.instancia()
        usuario = facade.adicionar_usuario(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )
        assert usuario.nome == "Ana Souza"
        assert usuario.perfil is Perfil.ADMINISTRADOR
        assert usuario.ativo is True
        assert usuario.id is not None

    def test_adiciona_usuario_com_perfil_como_texto(self):
        facade = FacadeSingletonController.instancia()
        usuario = facade.adicionar_usuario(
            nome="Bruno Lima",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            senha="OutraSenha2@",
            perfil="GESTOR",
        )
        assert usuario.perfil is Perfil.GESTOR

    def test_rejeita_cpf_duplicado(self):
        facade = FacadeSingletonController.instancia()
        facade.adicionar_usuario(
            nome="Diana",
            cpf="55566677788",
            email="diana@ubs.gov.br",
            telefone="84977776666",
            senha="MinhaSenh@1",
            perfil=Perfil.MEDICO,
        )
        with pytest.raises(CpfDuplicado):
            facade.adicionar_usuario(
                nome="Outro",
                cpf="55566677788",
                email="outro@ubs.gov.br",
                telefone="84933334444",
                senha="OutraSenh@2",
                perfil=Perfil.GESTOR,
            )

    def test_rejeita_senha_fraca(self):
        facade = FacadeSingletonController.instancia()
        with pytest.raises(ErroDeValidacao):
            facade.adicionar_usuario(
                nome="Evandro",
                cpf="44455566677",
                email="evandro@ubs.gov.br",
                telefone="84955554444",
                senha="fraca",
                perfil=Perfil.MEDICO,
            )

    def test_rejeita_nome_vazio(self):
        facade = FacadeSingletonController.instancia()
        with pytest.raises(ErroDeValidacao):
            facade.adicionar_usuario(
                nome="",
                cpf="33344455566",
                email="fulano@ubs.gov.br",
                telefone="84922223333",
                senha="SenhaValida1!",
                perfil=Perfil.MEDICO,
            )


# ------------------------------------------------------------------ #
# Testes do padrão Facade — listar_usuarios                           #
# ------------------------------------------------------------------ #

class TestFacadeListarUsuarios:
    def test_lista_vazia_antes_de_adicionar(self):
        facade = FacadeSingletonController.instancia()
        assert facade.listar_usuarios() == []

    def test_lista_todos_os_usuarios_adicionados(self):
        facade = FacadeSingletonController.instancia()
        facade.adicionar_usuario(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )
        facade.adicionar_usuario(
            nome="Bruno",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )
        usuarios = facade.listar_usuarios()
        assert len(usuarios) == 2
        nomes = {u.nome for u in usuarios}
        assert nomes == {"Ana", "Bruno"}


# ------------------------------------------------------------------ #
# Testes do padrão Facade — autenticar                                #
# ------------------------------------------------------------------ #

class TestFacadeAutenticar:
    @pytest.fixture
    def facade_com_usuario(self):
        facade = FacadeSingletonController.instancia()
        facade.adicionar_usuario(
            nome="Carlos",
            cpf="11122233344",
            email="carlos@ubs.gov.br",
            telefone="84911112222",
            senha="SenhaForte1!",
            perfil=Perfil.GESTOR,
        )
        return facade

    def test_autentica_com_credenciais_corretas(self, facade_com_usuario):
        usuario = facade_com_usuario.autenticar(
            email="carlos@ubs.gov.br",
            senha="SenhaForte1!",
        )
        assert usuario.nome == "Carlos"

    def test_rejeita_senha_errada(self, facade_com_usuario):
        with pytest.raises(CredenciaisInvalidas):
            facade_com_usuario.autenticar(
                email="carlos@ubs.gov.br",
                senha="SenhaErrada9!",
            )

    def test_rejeita_email_inexistente(self, facade_com_usuario):
        with pytest.raises(CredenciaisInvalidas):
            facade_com_usuario.autenticar(
                email="naoexiste@ubs.gov.br",
                senha="SenhaForte1!",
            )

    def test_rejeita_email_em_branco(self, facade_com_usuario):
        with pytest.raises(ErroDeValidacao):
            facade_com_usuario.autenticar(email="", senha="SenhaForte1!")

    def test_rejeita_senha_em_branco(self, facade_com_usuario):
        with pytest.raises(ErroDeValidacao):
            facade_com_usuario.autenticar(
                email="carlos@ubs.gov.br",
                senha="",
            )

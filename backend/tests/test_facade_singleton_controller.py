"""Testes do FacadeSingletonController.

Verificam:
  - Singleton: instancia() sempre devolve o mesmo objeto.
  - Facade:    os três casos de uso (adicionar, listar, autenticar)
               funcionam corretamente por meio da fachada.
"""

import pytest

from gestao_usuarios.aplicacao.comandos import (
    ComandoBuscarUsuarioPorId,
    ComandoDesativarUsuario,
)
from gestao_usuarios.aplicacao.facade_singleton_controller import (
    FacadeSingletonController,
)
from gestao_usuarios.dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
    NenhumaAtualizacaoParaDesfazer,
    UsuarioInativo,
    UsuarioNaoEncontrado,
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
            login="carlos",
            senha="SenhaForte1!",
            perfil=Perfil.MEDICO,
        )

        assert len(
            facade.listar_usuarios()
        ) == 1

        FacadeSingletonController.resetar_instancia()

        nova_facade = FacadeSingletonController.instancia()

        assert len(
            nova_facade.listar_usuarios()
        ) == 0


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
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )

        assert usuario.nome == "Ana Souza"
        assert usuario.login == "ana"
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
            login="bruno",
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
            login="diana",
            senha="MinhaSenh@1",
            perfil=Perfil.MEDICO,
        )

        with pytest.raises(CpfDuplicado):
            facade.adicionar_usuario(
                nome="Outro",
                cpf="55566677788",
                email="outro@ubs.gov.br",
                telefone="84933334444",
                login="outro",
                senha="OutraSenh@2",
                perfil=Perfil.GESTOR,
            )

    def test_rejeita_login_duplicado(self):
        facade = FacadeSingletonController.instancia()

        facade.adicionar_usuario(
            nome="Diana",
            cpf="55566677788",
            email="diana@ubs.gov.br",
            telefone="84977776666",
            login="diana",
            senha="MinhaSenh@1",
            perfil=Perfil.MEDICO,
        )

        with pytest.raises(LoginDuplicado):
            facade.adicionar_usuario(
                nome="Outra Diana",
                cpf="11122233344",
                email="outra@ubs.gov.br",
                telefone="84933334444",
                login="diana",
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
                login="evandro",
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
                login="fulano",
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
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )

        facade.adicionar_usuario(
            nome="Bruno",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            login="bruno",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )

        usuarios = facade.listar_usuarios()

        assert len(usuarios) == 2

        nomes = {
            usuario.nome
            for usuario in usuarios
        }

        assert nomes == {
            "Ana",
            "Bruno",
        }


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
            login="carlos",
            senha="SenhaForte1!",
            perfil=Perfil.GESTOR,
        )

        return facade

    def test_autentica_com_credenciais_corretas(
        self,
        facade_com_usuario,
    ):
        usuario = facade_com_usuario.autenticar(
            login="carlos",
            senha="SenhaForte1!",
        )

        assert usuario.nome == "Carlos"
        assert usuario.login == "carlos"

    def test_rejeita_senha_errada(
        self,
        facade_com_usuario,
    ):
        with pytest.raises(CredenciaisInvalidas):
            facade_com_usuario.autenticar(
                login="carlos",
                senha="SenhaErrada9!",
            )

    def test_rejeita_login_inexistente(
        self,
        facade_com_usuario,
    ):
        with pytest.raises(CredenciaisInvalidas):
            facade_com_usuario.autenticar(
                login="naoexiste",
                senha="SenhaForte1!",
            )

    def test_rejeita_login_em_branco(
        self,
        facade_com_usuario,
    ):
        with pytest.raises(ErroDeValidacao):
            facade_com_usuario.autenticar(
                login="",
                senha="SenhaForte1!",
            )

    def test_rejeita_senha_em_branco(
        self,
        facade_com_usuario,
    ):
        with pytest.raises(ErroDeValidacao):
            facade_com_usuario.autenticar(
                login="carlos",
                senha="",
            )


# ------------------------------------------------------------------ #
# Testes do padrão Facade — Unidades Básicas de Saúde (UBS)           #
# ------------------------------------------------------------------ #


class TestFacadeUnidadeBasicaSaude:
    def test_crud_completo_ubs_via_facade(self):
        facade = FacadeSingletonController.instancia()

        # Adicionar
        unidade = facade.adicionar_unidade(
            nome="UBS Centro",
            cnpj="12345678000199",
            endereco="Rua Principal, 100",
            telefone="84999990000",
        )
        assert unidade.id == 1
        assert unidade.nome == "UBS Centro"
        assert unidade.ativa is True

        # Listar
        unidades = facade.listar_unidades()
        assert len(unidades) == 1

        # Buscar por ID
        buscada = facade.buscar_unidade_por_id(unidade.id)
        assert buscada.cnpj == "12345678000199"

        # Atualizar
        atualizada = facade.atualizar_unidade(
            unidade_id=unidade.id,
            nome="UBS Centro Atualizada",
            cnpj="12345678000199",
            endereco="Rua Nova, 200",
            telefone="84988887777",
        )
        assert atualizada.nome == "UBS Centro Atualizada"
        assert atualizada.endereco == "Rua Nova, 200"

        # Remover (lógico)
        removida = facade.remover_unidade(unidade.id)
        assert removida.ativa is False
        assert facade.listar_unidades(apenas_ativas=True) == []


# ------------------------------------------------------------------ #
# Testes do padrão Command na Facade                                 #
# ------------------------------------------------------------------ #


class TestFacadeIntegracaoCommand:
    def test_facade_possui_executor_de_comandos(self):
        facade = FacadeSingletonController.instancia()
        from gestao_usuarios.aplicacao.comandos import ExecutorDeComandos

        assert isinstance(facade.executor, ExecutorDeComandos)

    def test_operacoes_da_facade_registram_comandos_no_executor(self):
        facade = FacadeSingletonController.instancia()
        from gestao_usuarios.aplicacao.comandos import (
            ComandoAdicionarUnidade,
            ComandoAdicionarUsuario,
            ComandoContarTotalEntidades,
            ComandoListarUsuarios,
        )

        facade.adicionar_usuario(
            nome="Ana",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )
        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoAdicionarUsuario,
        )

        facade.listar_usuarios()
        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoListarUsuarios,
        )

        facade.adicionar_unidade(
            nome="UBS Central",
            cnpj="12345678000199",
            endereco="Rua Central, 1",
            telefone="84999991111",
        )
        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoAdicionarUnidade,
        )

        total = facade.obter_quantidade_total_entidades_cadastradas()

        assert total == 2
        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoContarTotalEntidades,
        )

    def test_executar_comando_diretamente_pela_facade(self):
        facade = FacadeSingletonController.instancia()
        from gestao_usuarios.aplicacao.comandos import (
            ComandoAdicionarUsuario,
            ComandoListarUsuarios,
        )

        cmd_add = ComandoAdicionarUsuario(
            facade._gerenciador_usuarios,
            nome="Bruno",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            login="bruno",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )

        usuario = facade.executar_comando(cmd_add)

        assert usuario.nome == "Bruno"

        cmd_list = ComandoListarUsuarios(
            facade._gerenciador_usuarios
        )

        usuarios = facade.executar_comando(cmd_list)

        assert len(usuarios) == 1

    def test_alias_facade_do_sistema(self):
        from gestao_usuarios.aplicacao.facade_singleton_controller import (
            FacadeDoSistema,
        )

        assert FacadeDoSistema is FacadeSingletonController


# ------------------------------------------------------------------ #
# Testes do padrão Memento na Facade                                 #
# ------------------------------------------------------------------ #


class TestFacadeMemento:
    def test_deve_desfazer_ultima_atualizacao_de_unidade(self):
        facade = FacadeSingletonController.instancia()

        unidade = facade.adicionar_unidade(
            nome="UBS Centro",
            cnpj="12345678000199",
            endereco="Rua Principal, 100",
            telefone="84999990000",
        )

        facade.atualizar_unidade(
            unidade_id=unidade.id,
            nome="UBS Centro Atualizada",
            cnpj="98765432000110",
            endereco="Rua Nova, 200",
            telefone="84988887777",
        )

        restaurada = (
            facade.desfazer_ultima_atualizacao_de_unidade()
        )

        assert restaurada.id == unidade.id
        assert restaurada.nome == "UBS Centro"
        assert restaurada.cnpj == "12345678000199"
        assert restaurada.endereco == "Rua Principal, 100"
        assert restaurada.telefone == "84999990000"
        assert restaurada.ativa is True

        persistida = facade.buscar_unidade_por_id(unidade.id)

        assert persistida == restaurada

    def test_deve_rejeitar_desfazer_sem_atualizacao_anterior(self):
        facade = FacadeSingletonController.instancia()

        with pytest.raises(NenhumaAtualizacaoParaDesfazer):
            facade.desfazer_ultima_atualizacao_de_unidade()

    def test_desfazer_deve_ser_registrado_no_executor(self):
        facade = FacadeSingletonController.instancia()

        from gestao_usuarios.aplicacao.comandos import (
            ComandoDesfazerAtualizacaoDeUnidade,
        )

        unidade = facade.adicionar_unidade(
            nome="UBS Centro",
            cnpj="12345678000199",
            endereco="Rua Principal, 100",
            telefone="84999990000",
        )

        facade.atualizar_unidade(
            unidade_id=unidade.id,
            nome="UBS Atualizada",
            cnpj="98765432000110",
            endereco="Rua Nova, 200",
            telefone="84988887777",
        )

        facade.desfazer_ultima_atualizacao_de_unidade()

        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoDesfazerAtualizacaoDeUnidade,
        )

# ------------------------------------------------------------------ #
# Testes do padrão Facade — CRUD de usuários                          #
# ------------------------------------------------------------------ #


class TestFacadeCrudDeUsuarios:
    @pytest.fixture
    def facade_com_usuario(self):
        facade = FacadeSingletonController.instancia()

        usuario = facade.adicionar_usuario(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )

        return facade, usuario

    def test_busca_usuario_por_id(self, facade_com_usuario):
        facade, usuario = facade_com_usuario

        encontrado = facade.buscar_usuario_por_id(usuario.id)

        assert encontrado.id == usuario.id
        assert encontrado.nome == "Ana Souza"

    def test_busca_usuario_por_login(self, facade_com_usuario):
        facade, usuario = facade_com_usuario

        encontrado = facade.buscar_usuario_por_login("ana")

        assert encontrado.id == usuario.id

    def test_rejeita_busca_de_usuario_inexistente(self):
        facade = FacadeSingletonController.instancia()

        with pytest.raises(UsuarioNaoEncontrado):
            facade.buscar_usuario_por_id(999)

    def test_atualiza_usuario(self, facade_com_usuario):
        facade, usuario = facade_com_usuario

        atualizado = facade.atualizar_usuario(
            usuario_id=usuario.id,
            nome="Ana Maria",
            cpf="98765432100",
            email="ana.maria@ubs.gov.br",
            telefone="84988887777",
            login="anamaria",
            perfil=Perfil.GESTOR,
        )

        assert atualizado.id == usuario.id
        assert atualizado.nome == "Ana Maria"
        assert atualizado.login == "anamaria"
        assert atualizado.perfil is Perfil.GESTOR

        assert (
            facade.buscar_usuario_por_id(usuario.id).nome
            == "Ana Maria"
        )

    def test_rejeita_atualizacao_com_login_invalido(
        self,
        facade_com_usuario,
    ):
        facade, usuario = facade_com_usuario

        with pytest.raises(ErroDeValidacao):
            facade.atualizar_usuario(
                usuario_id=usuario.id,
                nome=usuario.nome,
                cpf=usuario.cpf,
                email=usuario.email,
                telefone=usuario.telefone,
                login="ana2",
                perfil=usuario.perfil,
            )

    def test_desativa_usuario_e_bloqueia_a_autenticacao(
        self,
        facade_com_usuario,
    ):
        facade, usuario = facade_com_usuario

        desativado = facade.desativar_usuario(usuario.id)

        assert desativado.ativo is False
        assert len(facade.listar_usuarios()) == 1
        assert (
            facade.listar_usuarios(apenas_ativos=True) == []
        )

        with pytest.raises(UsuarioInativo):
            facade.autenticar(
                login="ana",
                senha="SenhaSecreta1!",
            )

    def test_reativa_usuario_desativado(
        self,
        facade_com_usuario,
    ):
        facade, usuario = facade_com_usuario

        facade.desativar_usuario(usuario.id)
        reativado = facade.reativar_usuario(usuario.id)

        assert reativado.ativo is True
        assert facade.autenticar(
            login="ana",
            senha="SenhaSecreta1!",
        )

    def test_operacoes_de_crud_passam_pelo_executor_de_comandos(
        self,
        facade_com_usuario,
    ):
        facade, usuario = facade_com_usuario

        facade.buscar_usuario_por_id(usuario.id)

        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoBuscarUsuarioPorId,
        )

        facade.desativar_usuario(usuario.id)

        assert isinstance(
            facade.executor.ultimo_comando,
            ComandoDesativarUsuario,
        )

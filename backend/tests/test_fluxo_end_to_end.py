"""Teste end-to-end do sistema, exercitado pela fachada.

Percorre o fluxo completo da aplicação até o disco, sem substituir nenhuma
peça por dublê: fábrica concreta de repositórios, adaptadores reais,
operações disparadas como comandos, persistência e leitura de volta.

Cada cenário roda duas vezes — uma sobre RAM e outra sobre SQLite em arquivo
— porque o Laboratório 2 exige que os dois mecanismos de persistência se
comportem da mesma forma.
"""

from dataclasses import dataclass

import pytest

from gestao_usuarios.adaptadores.adaptador_arquivo_de_log import (
    AdaptadorArquivoDeLog,
)
from gestao_usuarios.adaptadores.arquivo_de_log_simples import (
    ArquivoDeLogSimples,
)
from gestao_usuarios.adaptadores.seletor_fabrica import (
    obter_fabrica_repositorio,
)
from gestao_usuarios.aplicacao.comandos import (
    ComandoAtualizarUsuario,
    ComandoContarTotalEntidades,
    ComandoDesativarUsuario,
)
from gestao_usuarios.aplicacao.facade_singleton_controller import (
    FacadeDoSistema,
    FacadeSingletonController,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import (
    GerenciadorDeUnidades,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.aplicacao.relatorio_de_acessos_csv import (
    RelatorioDeAcessosCsv,
)
from gestao_usuarios.aplicacao.relatorio_de_acessos_texto import (
    RelatorioDeAcessosTexto,
)
from gestao_usuarios.dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
    UsuarioInativo,
    UsuarioNaoEncontrado,
)
from gestao_usuarios.dominio.usuario import Perfil


@dataclass
class Sistema:
    """Sistema montado para o teste, com acesso às peças públicas usadas."""

    facade: FacadeSingletonController
    usuarios: GerenciadorDeUsuarios
    unidades: GerenciadorDeUnidades
    acessos: object
    armazenamento: str


@pytest.fixture(autouse=True)
def limpar_singleton():
    """Isola cada teste, como se a aplicação subisse do zero."""
    FacadeSingletonController.resetar_instancia()
    yield
    FacadeSingletonController.resetar_instancia()


@pytest.fixture(
    params=[
        "memoria",
        "bd",
    ]
)
def sistema(request, tmp_path, monkeypatch) -> Sistema:
    """Monta o sistema com a fábrica concreta correspondente ao mecanismo.

    O diretório de trabalho é isolado porque a fábrica de banco grava
    ``usuarios.db`` e ``acessos.log`` no diretório corrente.

    Os gerenciadores devolvidos compartilham os mesmos repositórios da
    fachada — o estado vive na persistência, não nos objetos de controle.
    """
    monkeypatch.chdir(tmp_path)

    fabrica = obter_fabrica_repositorio(request.param)

    repositorio_usuarios = fabrica.criar_repositorio_usuario()
    repositorio_unidades = (
        fabrica.criar_repositorio_unidade_basica_saude()
    )
    repositorio_acessos = (
        fabrica.criar_repositorio_registro_de_acesso()
    )

    return Sistema(
        facade=FacadeSingletonController(
            repositorio_usuarios,
            repositorio_unidades,
            repositorio_acessos,
        ),
        usuarios=GerenciadorDeUsuarios(
            repositorio_usuarios,
            repositorio_acessos,
        ),
        unidades=GerenciadorDeUnidades(repositorio_unidades),
        acessos=repositorio_acessos,
        armazenamento=request.param,
    )


# ------------------------------------------------------------------ #
# Fluxo completo de ponta a ponta                                     #
# ------------------------------------------------------------------ #


def test_fluxo_completo_do_sistema(sistema: Sistema):
    facade = sistema.facade

    # --- 1. Cadastro de usuários ------------------------------------
    administradora = facade.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    medico = facade.adicionar_usuario(
        nome="Bruno Lima",
        cpf="98765432100",
        email="bruno@ubs.gov.br",
        telefone="84988887777",
        login="bruno",
        senha="OutraSenha2@",
        perfil="MEDICO",
    )

    assert administradora.id is not None
    assert medico.id != administradora.id
    assert administradora.senha_hash.startswith("pbkdf2_sha256$")
    assert "SenhaSecreta1!" not in administradora.senha_hash
    assert len(facade.listar_usuarios()) == 2

    # --- 2. Validações barram cadastros inválidos -------------------
    with pytest.raises(
        ErroDeValidacao,
        match="não pode conter números",
    ):
        facade.adicionar_usuario(
            nome="Carla",
            cpf="11122233344",
            email="carla@ubs.gov.br",
            telefone="84900001111",
            login="carla2",
            senha="TerceiraSenha3#",
            perfil=Perfil.GESTOR,
        )

    with pytest.raises(
        ErroDeValidacao,
        match="no máximo 12",
    ):
        facade.adicionar_usuario(
            nome="Carla",
            cpf="11122233344",
            email="carla@ubs.gov.br",
            telefone="84900001111",
            login="carlaaaaaaaaaaaaa",
            senha="TerceiraSenha3#",
            perfil=Perfil.GESTOR,
        )

    with pytest.raises(ErroDeValidacao):
        facade.adicionar_usuario(
            nome="Carla",
            cpf="11122233344",
            email="carla@ubs.gov.br",
            telefone="84900001111",
            login="carla",
            senha="fraca",
            perfil=Perfil.GESTOR,
        )

    with pytest.raises(CpfDuplicado):
        facade.adicionar_usuario(
            nome="Outra Ana",
            cpf="12345678901",
            email="outra@ubs.gov.br",
            telefone="84900002222",
            login="outraana",
            senha="QuartaSenha4$",
            perfil=Perfil.GESTOR,
        )

    with pytest.raises(LoginDuplicado):
        facade.adicionar_usuario(
            nome="Homônimo",
            cpf="55566677788",
            email="homonimo@ubs.gov.br",
            telefone="84900003333",
            login="ana",
            senha="QuintaSenha5%",
            perfil=Perfil.GESTOR,
        )

    # Nenhum cadastro inválido chegou ao repositório.
    assert len(facade.listar_usuarios()) == 2

    # --- 3. Autenticação --------------------------------------------
    autenticada = facade.autenticar(
        login="ana",
        senha="SenhaSecreta1!",
    )

    assert autenticada.id == administradora.id
    assert autenticada.perfil is Perfil.ADMINISTRADOR

    with pytest.raises(CredenciaisInvalidas):
        facade.autenticar(login="ana", senha="errada")

    with pytest.raises(CredenciaisInvalidas):
        facade.autenticar(login="naoexiste", senha="qualquer")

    # --- 4. Busca ----------------------------------------------------
    assert (
        facade.buscar_usuario_por_id(medico.id).nome
        == "Bruno Lima"
    )
    assert (
        facade.buscar_usuario_por_login("bruno").id == medico.id
    )

    with pytest.raises(UsuarioNaoEncontrado):
        facade.buscar_usuario_por_id(999)

    # --- 5. Atualização ----------------------------------------------
    atualizado = facade.atualizar_usuario(
        usuario_id=medico.id,
        nome="Bruno Lima da Silva",
        cpf="98765432100",
        email="bruno.lima@ubs.gov.br",
        telefone="84977776666",
        login="brunolima",
        perfil=Perfil.GESTOR,
    )

    assert atualizado.id == medico.id
    assert atualizado.login == "brunolima"
    assert atualizado.perfil is Perfil.GESTOR
    assert atualizado.senha_hash == medico.senha_hash

    # A atualização substitui o cadastro em vez de criar outro.
    assert len(facade.listar_usuarios()) == 2

    # O login antigo deixou de existir; o novo responde.
    with pytest.raises(UsuarioNaoEncontrado):
        facade.buscar_usuario_por_login("bruno")

    assert (
        facade.buscar_usuario_por_login("brunolima").id
        == medico.id
    )

    # A senha antiga continua válida — não foi tocada.
    assert facade.autenticar(
        login="brunolima",
        senha="OutraSenha2@",
    )

    # Atualização inválida não altera nada.
    with pytest.raises(LoginDuplicado):
        facade.atualizar_usuario(
            usuario_id=medico.id,
            nome=atualizado.nome,
            cpf=atualizado.cpf,
            email=atualizado.email,
            telefone=atualizado.telefone,
            login="ana",
            perfil=atualizado.perfil,
        )

    assert (
        facade.buscar_usuario_por_id(medico.id).login
        == "brunolima"
    )

    # --- 6. Troca de senha pela atualização --------------------------
    facade.atualizar_usuario(
        usuario_id=medico.id,
        nome=atualizado.nome,
        cpf=atualizado.cpf,
        email=atualizado.email,
        telefone=atualizado.telefone,
        login=atualizado.login,
        perfil=atualizado.perfil,
        senha="SenhaTrocada9&",
    )

    assert facade.autenticar(
        login="brunolima",
        senha="SenhaTrocada9&",
    )

    with pytest.raises(CredenciaisInvalidas):
        facade.autenticar(
            login="brunolima",
            senha="OutraSenha2@",
        )

    # --- 7. Desativação lógica ---------------------------------------
    desativado = facade.desativar_usuario(medico.id)

    assert desativado.ativo is False

    # O cadastro continua existindo — só o acesso foi bloqueado.
    assert len(facade.listar_usuarios()) == 2
    assert len(facade.listar_usuarios(apenas_ativos=True)) == 1

    with pytest.raises(UsuarioInativo):
        facade.autenticar(
            login="brunolima",
            senha="SenhaTrocada9&",
        )

    # --- 8. Reativação -----------------------------------------------
    assert facade.reativar_usuario(medico.id).ativo is True
    assert facade.autenticar(
        login="brunolima",
        senha="SenhaTrocada9&",
    )

    # --- 9. CRUD de UBS e desfazer (Memento) -------------------------
    unidade = facade.adicionar_unidade(
        nome="UBS Centro",
        cnpj="12345678000199",
        endereco="Rua Principal, 100",
        telefone="84999990000",
    )

    facade.atualizar_unidade(
        unidade_id=unidade.id,
        nome="UBS Centro Reformada",
        cnpj="12345678000199",
        endereco="Rua Nova, 200",
        telefone="84988887777",
    )

    restaurada = facade.desfazer_ultima_atualizacao_de_unidade()

    assert restaurada.nome == "UBS Centro"
    assert restaurada.endereco == "Rua Principal, 100"

    assert facade.remover_unidade(unidade.id).ativa is False
    assert facade.listar_unidades(apenas_ativas=True) == []

    # --- 10. Contagem agregada ---------------------------------------
    assert (
        facade.obter_quantidade_total_entidades_cadastradas() == 3
    )

    # --- 11. Relatórios das tentativas de acesso ---------------------
    texto = RelatorioDeAcessosTexto(sistema.acessos).gerar()
    csv = RelatorioDeAcessosCsv(sistema.acessos).gerar()

    assert "RELATÓRIO DE ACESSOS" in texto
    assert "ana" in texto
    assert "brunolima" in texto
    assert csv.startswith(
        "login,tentativas,sucessos,falhas,ultimo_acesso"
    )
    assert "TOTAL" in csv


def test_operacoes_do_fluxo_ficam_registradas_no_executor(
    sistema: Sistema,
):
    """O histórico do invoker reflete a ordem real das operações."""
    facade = sistema.facade

    usuario = facade.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    facade.atualizar_usuario(
        usuario_id=usuario.id,
        nome="Ana Maria",
        cpf=usuario.cpf,
        email=usuario.email,
        telefone=usuario.telefone,
        login="anamaria",
        perfil=usuario.perfil,
    )

    facade.desativar_usuario(usuario.id)

    historico = facade.executor.historico

    assert [
        type(comando).__name__
        for comando in historico
    ] == [
        "ComandoAdicionarUsuario",
        "ComandoAtualizarUsuario",
        "ComandoDesativarUsuario",
    ]

    # Um comando avulso também pode ser executado pela fachada.
    total = facade.executar_comando(
        ComandoContarTotalEntidades(
            sistema.usuarios,
            sistema.unidades,
        )
    )

    assert total == 1
    assert isinstance(
        facade.executor.ultimo_comando,
        ComandoContarTotalEntidades,
    )


def test_comandos_de_crud_podem_ser_executados_diretamente(
    sistema: Sistema,
):
    """Os comandos são objetos: o cliente pode montá-los e disparar depois."""
    facade = sistema.facade

    usuario = facade.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    atualizar = ComandoAtualizarUsuario(
        sistema.usuarios,
        usuario_id=usuario.id,
        nome="Ana Maria",
        cpf=usuario.cpf,
        email=usuario.email,
        telefone=usuario.telefone,
        login="anamaria",
        perfil=Perfil.GESTOR,
    )

    desativar = ComandoDesativarUsuario(
        sistema.usuarios,
        usuario.id,
    )

    # Montados antes, executados depois e na ordem escolhida pelo cliente.
    assert facade.executar_comando(atualizar).login == "anamaria"
    assert facade.executar_comando(desativar).ativo is False

    # O efeito é visível pela fachada: ambos falam com o mesmo repositório.
    recuperado = facade.buscar_usuario_por_id(usuario.id)

    assert recuperado.login == "anamaria"
    assert recuperado.ativo is False


# ------------------------------------------------------------------ #
# Aplicação real: seleção por variável de ambiente e reinício         #
# ------------------------------------------------------------------ #


def test_variavel_de_ambiente_seleciona_o_mecanismo_de_persistencia(
    tmp_path,
    monkeypatch,
):
    """Como o ``__main__`` faz: o mecanismo vem de ``STORAGE_TYPE``."""
    monkeypatch.setenv("STORAGE_TYPE", "memoria")
    monkeypatch.chdir(tmp_path)

    facade = FacadeSingletonController.instancia()

    facade.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    assert FacadeDoSistema is FacadeSingletonController
    assert FacadeDoSistema.instancia() is facade

    # Em RAM nada é gravado em disco.
    assert not (tmp_path / "usuarios.db").exists()


def test_dados_sobrevivem_ao_reinicio_quando_armazenados_em_sqlite(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("STORAGE_TYPE", "bd")
    monkeypatch.chdir(tmp_path)

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

    facade.atualizar_usuario(
        usuario_id=usuario.id,
        nome="Ana Maria",
        cpf=usuario.cpf,
        email=usuario.email,
        telefone=usuario.telefone,
        login="anamaria",
        perfil=Perfil.GESTOR,
    )

    facade.desativar_usuario(usuario.id)

    assert (tmp_path / "usuarios.db").exists()

    # Simula o encerramento e uma nova execução da aplicação.
    FacadeSingletonController.resetar_instancia()

    nova_facade = FacadeSingletonController.instancia()

    assert nova_facade is not facade

    recuperado = nova_facade.buscar_usuario_por_id(usuario.id)

    assert recuperado.nome == "Ana Maria"
    assert recuperado.login == "anamaria"
    assert recuperado.perfil is Perfil.GESTOR
    assert recuperado.ativo is False
    assert recuperado.senha_hash == usuario.senha_hash

    # A desativação continua valendo depois do reinício.
    with pytest.raises(UsuarioInativo):
        nova_facade.autenticar(
            login="anamaria",
            senha="SenhaSecreta1!",
        )

    # E a reativação volta a liberar o acesso.
    nova_facade.reativar_usuario(usuario.id)

    assert nova_facade.autenticar(
        login="anamaria",
        senha="SenhaSecreta1!",
    )


def test_log_de_acessos_persiste_em_arquivo_no_modo_banco(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("STORAGE_TYPE", "bd")
    monkeypatch.chdir(tmp_path)

    facade = FacadeSingletonController.instancia()

    facade.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="SenhaSecreta1!",
        perfil=Perfil.ADMINISTRADOR,
    )

    facade.autenticar(login="ana", senha="SenhaSecreta1!")

    with pytest.raises(CredenciaisInvalidas):
        facade.autenticar(login="ana", senha="errada")

    log = tmp_path / "acessos.log"

    assert log.exists()

    linhas = [
        linha
        for linha in log.read_text(
            encoding="utf-8"
        ).splitlines()
        if linha.strip()
    ]

    assert len(linhas) == 2
    assert linhas[0].endswith(";ana")
    assert linhas[0].split(";")[1] == "1"
    assert linhas[1].split(";")[1] == "0"

    # O Adapter relê o arquivo e devolve entidades de domínio.
    registros = AdaptadorArquivoDeLog(
        ArquivoDeLogSimples(str(log))
    ).buscar_todos()

    assert len(registros) == 2
    assert [
        registro.sucesso for registro in registros
    ] == [True, False]
    assert all(
        registro.login == "ana" for registro in registros
    )

    relatorio = RelatorioDeAcessosTexto(
        AdaptadorArquivoDeLog(ArquivoDeLogSimples(str(log)))
    ).gerar()

    assert "ana: 2 tentativa(s)" in relatorio

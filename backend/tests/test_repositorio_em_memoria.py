from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.dominio.usuario import Perfil, Usuario


def _usuario(cpf: str = "12345678901") -> Usuario:
    return Usuario.criar(
        nome="Ana",
        cpf=cpf,
        email=f"{cpf}@ubs.gov.br",
        telefone="84999990000",
        senha="Senha123!",
        perfil=Perfil.MEDICO,
    )


def test_salvar_atribui_id_sequencial():
    repositorio = RepositorioUsuarioEmMemoria()

    primeiro = repositorio.salvar(_usuario("11111111111"))
    segundo = repositorio.salvar(_usuario("22222222222"))

    assert primeiro.id == 1
    assert segundo.id == 2


def test_buscar_todos_retorna_usuarios_salvos():
    repositorio = RepositorioUsuarioEmMemoria()
    repositorio.salvar(_usuario("11111111111"))
    repositorio.salvar(_usuario("22222222222"))

    assert len(repositorio.buscar_todos()) == 2


def test_buscar_todos_retorna_lista_vazia_quando_nao_ha_usuarios():
    repositorio = RepositorioUsuarioEmMemoria()

    assert repositorio.buscar_todos() == []


def test_buscar_por_cpf_encontra_ou_devolve_none():
    repositorio = RepositorioUsuarioEmMemoria()
    repositorio.salvar(_usuario("11111111111"))

    assert repositorio.buscar_por_cpf("11111111111") is not None
    assert repositorio.buscar_por_cpf("00000000000") is None


def test_buscar_por_email_encontra_ou_devolve_none():
    repositorio = RepositorioUsuarioEmMemoria()
    repositorio.salvar(_usuario("11111111111"))

    assert repositorio.buscar_por_email("11111111111@ubs.gov.br") is not None
    assert repositorio.buscar_por_email("naoexiste@ubs.gov.br") is None


def test_buscar_todos_nao_vaza_a_colecao_interna():
    repositorio = RepositorioUsuarioEmMemoria()
    repositorio.salvar(_usuario("11111111111"))

    lista = repositorio.buscar_todos()
    lista.clear()

    assert len(repositorio.buscar_todos()) == 1

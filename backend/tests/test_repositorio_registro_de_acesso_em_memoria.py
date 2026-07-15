from datetime import datetime

from gestao_usuarios.adaptadores.repositorio_registro_de_acesso_em_memoria import (
    RepositorioRegistroDeAcessoEmMemoria,
)
from gestao_usuarios.dominio.registro_de_acesso import RegistroDeAcesso


def _registro(email: str = "ana@ubs.gov.br", sucesso: bool = True) -> RegistroDeAcesso:
    return RegistroDeAcesso.criar(
        email=email, sucesso=sucesso, data_hora=datetime(2026, 7, 15, 10, 30)
    )


def test_salvar_atribui_ids_sequenciais():
    repositorio = RepositorioRegistroDeAcessoEmMemoria()

    primeiro = repositorio.salvar(_registro())
    segundo = repositorio.salvar(_registro(sucesso=False))

    assert primeiro.id == 1
    assert segundo.id == 2


def test_buscar_todos_devolve_registros_salvos():
    repositorio = RepositorioRegistroDeAcessoEmMemoria()
    repositorio.salvar(_registro())
    repositorio.salvar(_registro(email="bruno@ubs.gov.br", sucesso=False))

    registros = repositorio.buscar_todos()

    assert len(registros) == 2
    assert registros[0].email == "ana@ubs.gov.br"
    assert registros[1].sucesso is False


def test_buscar_todos_devolve_lista_vazia_quando_nao_ha_registros():
    repositorio = RepositorioRegistroDeAcessoEmMemoria()

    assert repositorio.buscar_todos() == []

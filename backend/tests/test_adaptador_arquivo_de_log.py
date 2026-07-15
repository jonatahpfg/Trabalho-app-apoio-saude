"""Testes do padrão Adapter: AdaptadorArquivoDeLog sobre ArquivoDeLogSimples."""
from datetime import datetime

import pytest

from gestao_usuarios.adaptadores.adaptador_arquivo_de_log import AdaptadorArquivoDeLog
from gestao_usuarios.adaptadores.arquivo_de_log_simples import ArquivoDeLogSimples
from gestao_usuarios.dominio.erros import ErroDeAcessoAoArquivo, ErroDePersistencia
from gestao_usuarios.dominio.registro_de_acesso import RegistroDeAcesso


@pytest.fixture
def caminho_log(tmp_path):
    return str(tmp_path / "acessos.log")


@pytest.fixture
def adaptador(caminho_log) -> AdaptadorArquivoDeLog:
    return AdaptadorArquivoDeLog(ArquivoDeLogSimples(caminho_log))


def _registro(email: str = "ana@ubs.gov.br", sucesso: bool = True) -> RegistroDeAcesso:
    return RegistroDeAcesso.criar(
        email=email, sucesso=sucesso, data_hora=datetime(2026, 7, 15, 10, 30)
    )


def test_salvar_atribui_ids_sequenciais(adaptador):
    primeiro = adaptador.salvar(_registro())
    segundo = adaptador.salvar(_registro(sucesso=False))

    assert primeiro.id == 1
    assert segundo.id == 2


def test_buscar_todos_reconstroi_registros_salvos(adaptador):
    adaptador.salvar(_registro())
    adaptador.salvar(_registro(email="bruno@ubs.gov.br", sucesso=False))

    registros = adaptador.buscar_todos()

    assert len(registros) == 2
    assert registros[0].email == "ana@ubs.gov.br"
    assert registros[0].sucesso is True
    assert registros[0].data_hora == datetime(2026, 7, 15, 10, 30)
    assert registros[1].email == "bruno@ubs.gov.br"
    assert registros[1].sucesso is False


def test_registros_persistem_entre_instancias_do_adaptador(caminho_log):
    AdaptadorArquivoDeLog(ArquivoDeLogSimples(caminho_log)).salvar(_registro())

    nova_instancia = AdaptadorArquivoDeLog(ArquivoDeLogSimples(caminho_log))

    assert len(nova_instancia.buscar_todos()) == 1


def test_buscar_todos_devolve_lista_vazia_quando_arquivo_nao_existe(adaptador):
    assert adaptador.buscar_todos() == []


def test_preserva_email_que_contem_o_separador(adaptador):
    adaptador.salvar(_registro(email="a;b@ubs.gov.br"))

    registros = adaptador.buscar_todos()

    assert registros[0].email == "a;b@ubs.gov.br"


def test_lanca_erro_de_acesso_quando_linha_corrompida(caminho_log, adaptador):
    ArquivoDeLogSimples(caminho_log).anotar("linha-sem-formato-valido")

    with pytest.raises(ErroDeAcessoAoArquivo):
        adaptador.buscar_todos()


def test_lanca_erro_de_acesso_quando_nao_consegue_gravar(tmp_path):
    # O caminho é um diretório: open() para escrita falha com OSError.
    adaptador = AdaptadorArquivoDeLog(ArquivoDeLogSimples(str(tmp_path)))

    with pytest.raises(ErroDeAcessoAoArquivo):
        adaptador.salvar(_registro())


def test_erro_de_acesso_e_subtipo_de_erro_de_persistencia(tmp_path):
    """A hierarquia permite capturar qualquer falha de persistência com um tipo só."""
    adaptador = AdaptadorArquivoDeLog(ArquivoDeLogSimples(str(tmp_path)))

    with pytest.raises(ErroDePersistencia):
        adaptador.salvar(_registro())

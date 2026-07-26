"""Testes do Template Method de relatórios de estatísticas de acesso."""

from datetime import datetime

import pytest

from gestao_usuarios.adaptadores.adaptador_arquivo_de_log import (
    AdaptadorArquivoDeLog,
)
from gestao_usuarios.adaptadores.arquivo_de_log_simples import (
    ArquivoDeLogSimples,
)
from gestao_usuarios.adaptadores.repositorio_registro_de_acesso_em_memoria import (
    RepositorioRegistroDeAcessoEmMemoria,
)
from gestao_usuarios.aplicacao.relatorio_de_acessos import (
    RelatorioDeAcessos,
)
from gestao_usuarios.aplicacao.relatorio_de_acessos_csv import (
    RelatorioDeAcessosCsv,
)
from gestao_usuarios.aplicacao.relatorio_de_acessos_texto import (
    RelatorioDeAcessosTexto,
)
from gestao_usuarios.dominio.registro_de_acesso import (
    RegistroDeAcesso,
)


@pytest.fixture
def repositorio() -> RepositorioRegistroDeAcessoEmMemoria:
    """Dois logins: ana com 2 sucessos e 1 falha; bruno com 1 falha."""
    repositorio = RepositorioRegistroDeAcessoEmMemoria()

    eventos = [
        (
            "ana",
            True,
            datetime(2026, 7, 14, 9, 0),
        ),
        (
            "ana",
            False,
            datetime(2026, 7, 14, 12, 0),
        ),
        (
            "bruno",
            False,
            datetime(2026, 7, 15, 8, 0),
        ),
        (
            "ana",
            True,
            datetime(2026, 7, 15, 10, 30),
        ),
    ]

    for login, sucesso, data_hora in eventos:
        repositorio.salvar(
            RegistroDeAcesso.criar(
                login=login,
                sucesso=sucesso,
                data_hora=data_hora,
            )
        )

    return repositorio


def test_nao_permite_instanciar_a_classe_base():
    """RelatorioDeAcessos é abstrata: só as concretas definem a formatação."""
    with pytest.raises(TypeError):
        RelatorioDeAcessos(
            RepositorioRegistroDeAcessoEmMemoria()
        )


def test_relatorio_texto_segue_a_ordem_do_molde(
    repositorio,
):
    linhas = RelatorioDeAcessosTexto(
        repositorio
    ).gerar().splitlines()

    assert linhas[0] == "RELATÓRIO DE ACESSOS"
    assert linhas[1].startswith(
        "ana: 3 tentativa(s)"
    )
    assert linhas[2].startswith(
        "bruno: 1 tentativa(s)"
    )
    assert linhas[3].startswith(
        "Total: 4 tentativa(s)"
    )


def test_relatorio_texto_consolida_estatisticas_por_login(
    repositorio,
):
    relatorio = RelatorioDeAcessosTexto(
        repositorio
    ).gerar()

    assert (
        "ana: 3 tentativa(s) "
        "(2 sucesso(s), 1 falha(s))"
        in relatorio
    )

    assert (
        "último acesso em 15/07/2026 10:30"
        in relatorio
    )


def test_relatorio_texto_calcula_totais_e_taxa_de_sucesso(
    repositorio,
):
    relatorio = RelatorioDeAcessosTexto(
        repositorio
    ).gerar()

    assert (
        "Total: 4 tentativa(s) | "
        "2 sucesso(s) | 2 falha(s)"
        in relatorio
    )

    assert (
        "taxa de sucesso: 50.0%"
        in relatorio
    )


def test_relatorio_texto_sem_registros_mostra_totais_zerados():
    relatorio = RelatorioDeAcessosTexto(
        RepositorioRegistroDeAcessoEmMemoria()
    ).gerar()

    linhas = relatorio.splitlines()

    # Apenas cabeçalho e rodapé.
    assert len(linhas) == 2

    assert (
        "Total: 0 tentativa(s)"
        in linhas[1]
    )

    assert (
        "taxa de sucesso: 0.0%"
        in linhas[1]
    )


def test_relatorio_csv_segue_a_ordem_do_molde(
    repositorio,
):
    linhas = RelatorioDeAcessosCsv(
        repositorio
    ).gerar().splitlines()

    assert (
        linhas[0]
        == "login,tentativas,sucessos,falhas,ultimo_acesso"
    )

    assert (
        linhas[1]
        == '"ana",3,2,1,2026-07-15T10:30:00'
    )

    assert (
        linhas[2]
        == '"bruno",1,0,1,2026-07-15T08:00:00'
    )

    assert (
        linhas[3]
        == '"TOTAL",4,2,2,50.0%'
    )


def test_formatos_diferentes_partem_das_mesmas_estatisticas(
    repositorio,
):
    """O molde garante os mesmos números em qualquer formato — muda só a formatação."""
    texto = RelatorioDeAcessosTexto(
        repositorio
    ).gerar()

    csv = RelatorioDeAcessosCsv(
        repositorio
    ).gerar()

    assert (
        "3 tentativa(s)" in texto
        and '"ana",3' in csv
    )

    assert (
        "taxa de sucesso: 50.0%" in texto
        and "50.0%" in csv
    )


def test_relatorio_funciona_sobre_o_adapter_de_arquivo_de_log(
    tmp_path,
):
    """Integração dos dois padrões da Tarefa 5: Template Method sobre Adapter."""
    adaptador = AdaptadorArquivoDeLog(
        ArquivoDeLogSimples(
            str(
                tmp_path / "acessos.log"
            )
        )
    )

    adaptador.salvar(
        RegistroDeAcesso.criar(
            login="ana",
            sucesso=True,
            data_hora=datetime(
                2026,
                7,
                15,
                10,
                30,
            ),
        )
    )

    relatorio = RelatorioDeAcessosTexto(
        adaptador
    ).gerar()

    assert (
        "ana: 1 tentativa(s) "
        "(1 sucesso(s), 0 falha(s))"
        in relatorio
    )

    assert (
        "taxa de sucesso: 100.0%"
        in relatorio
    )
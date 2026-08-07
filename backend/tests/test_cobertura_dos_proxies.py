"""Garante que os Proxies cobrem toda a superfície dos gerenciadores reais.

Um Proxy de autorização só protege o que ele intercepta. Quando um caso de
uso novo é acrescentado ao gerenciador e o Proxy não é atualizado junto, a
operação passa a ser alcançável sem verificação de perfil — a falha é
silenciosa, porque nada quebra.

Estes testes falham nesse cenário, apontando exatamente qual operação ficou
descoberta.
"""

from __future__ import annotations

import pytest

from gestao_usuarios.aplicacao.gerenciador_de_unidades import (
    GerenciadorDeUnidades,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.aplicacao.proxy import (
    ProxyGerenciadorDeUnidades,
    ProxyGerenciadorDeUsuarios,
)

# Operações que o Proxy expõe sem exigir perfil, com a justificativa.
_OPERACOES_PUBLICAS = {
    # autenticar é a porta de entrada do sistema: quem chama ainda não
    # possui perfil verificado.
    "autenticar",
}


def _operacoes_publicas(classe: type) -> set[str]:
    """Devolve os métodos públicos declarados pela classe."""
    return {
        nome
        for nome in dir(classe)
        if not nome.startswith("_")
        and callable(getattr(classe, nome))
    }


@pytest.mark.parametrize(
    ("real", "proxy"),
    [
        (GerenciadorDeUsuarios, ProxyGerenciadorDeUsuarios),
        (GerenciadorDeUnidades, ProxyGerenciadorDeUnidades),
    ],
    ids=["usuarios", "unidades"],
)
def test_proxy_cobre_todas_as_operacoes_do_gerenciador(real, proxy):
    descobertas = _operacoes_publicas(real) - _operacoes_publicas(proxy)

    assert not descobertas, (
        f"{proxy.__name__} não intercepta {sorted(descobertas)}. "
        "Toda operação do gerenciador precisa passar pela verificação "
        "de perfil, senão a autorização pode ser contornada."
    )


@pytest.mark.parametrize(
    ("real", "proxy"),
    [
        (GerenciadorDeUsuarios, ProxyGerenciadorDeUsuarios),
        (GerenciadorDeUnidades, ProxyGerenciadorDeUnidades),
    ],
    ids=["usuarios", "unidades"],
)
def test_proxy_nao_expoe_operacao_inexistente_no_gerenciador(real, proxy):
    """O Proxy é um substituto do objeto real, não uma extensão dele."""
    excedentes = _operacoes_publicas(proxy) - _operacoes_publicas(real)

    assert not excedentes, (
        f"{proxy.__name__} expõe {sorted(excedentes)}, que não existe em "
        f"{real.__name__}. O Proxy deve espelhar o objeto real."
    )


@pytest.mark.parametrize(
    ("proxy", "sem_verificacao"),
    [
        (ProxyGerenciadorDeUsuarios, _OPERACOES_PUBLICAS),
        (ProxyGerenciadorDeUnidades, frozenset()),
    ],
    ids=["usuarios", "unidades"],
)
def test_toda_operacao_do_proxy_verifica_o_perfil(proxy, sem_verificacao):
    """Cada método do Proxy deve chamar ``_verificar_perfil`` antes de delegar.

    A checagem é feita no código-fonte do método porque o alvo é justamente
    a operação que alguém esqueceu de proteger — ela não seria exercitada
    por nenhum teste de comportamento existente.
    """
    import inspect

    desprotegidas = []

    for nome in sorted(_operacoes_publicas(proxy) - set(sem_verificacao)):
        codigo = inspect.getsource(getattr(proxy, nome))

        if "_verificar_perfil" not in codigo:
            desprotegidas.append(nome)

    assert not desprotegidas, (
        f"{proxy.__name__} delega {desprotegidas} sem chamar "
        "_verificar_perfil."
    )

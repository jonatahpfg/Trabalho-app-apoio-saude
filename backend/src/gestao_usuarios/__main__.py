"""Composição (fiação) do contexto — demonstra adicionar, listar e autenticar.

Este é um adaptador primário mínimo: monta o repositório adequado (RAM ou SQLite),
injeta-o no gerenciador e exercita os casos de uso.

Execução: ``python -m gestao_usuarios`` (a partir de ``backend/src``).
"""

from __future__ import annotations

import os
import sys

from .adaptadores.seletor_fabrica import obter_fabrica_repositorio
from .aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from .aplicacao.relatorio_de_acessos_csv import RelatorioDeAcessosCsv
from .aplicacao.relatorio_de_acessos_texto import RelatorioDeAcessosTexto
from .dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeAutenticacao,
    ErroDeDominio,
    ErroDePersistencia,
    LoginDuplicado,
)
from .dominio.usuario import Perfil


def main() -> None:
    # 1. Chaveamento de persistência usando variável de ambiente.
    # Define "memoria" como padrão. Se for definido como "bd", usa SQLite.
    tipo_armazenamento = os.environ.get(
        "STORAGE_TYPE",
        "memoria",
    ).lower()

    fabrica = obter_fabrica_repositorio(tipo_armazenamento)

    desc_tipo = (
        "Banco de Dados (SQLite)"
        if tipo_armazenamento == "bd"
        else "Memória (RAM)"
    )

    print(
        f"-> Inicializando armazenamento em {desc_tipo} "
        "via Abstract Factory..."
    )

    repositorio = fabrica.criar_repositorio_usuario()
    repositorio_acessos = fabrica.criar_repositorio_registro_de_acesso()

    gerenciador = GerenciadorDeUsuarios(
        repositorio,
        repositorio_acessos,
    )

    # 2. Cadastro de usuários.
    try:
        gerenciador.adicionar_usuario(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            login="ana",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )

        gerenciador.adicionar_usuario(
            nome="Bruno Lima",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            login="bruno",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )

    except (
        ErroDePersistencia,
        CpfDuplicado,
        LoginDuplicado,
    ) as erro:
        print(
            f"Erro ao inicializar usuários: {erro}",
            file=sys.stderr,
        )
        return

    # 3. Listagem de usuários cadastrados.
    print("\nUsuários cadastrados:")

    for usuario in gerenciador.listar_usuarios():
        print(
            f"  #{usuario.id} "
            f"{usuario.nome} "
            f"[login={usuario.login}] "
            f"({usuario.perfil.value}) "
            f"— ativo={usuario.ativo}"
        )

    # 4. CRUD: buscar, atualizar e desativar.
    # O mesmo roteiro vale para RAM e SQLite, pois o gerenciador só
    # conhece a porta RepositorioUsuario.
    print("\n--- Demonstração do CRUD de usuários ---")

    try:
        bruno = gerenciador.buscar_usuario_por_login("bruno")

        print(
            f"Buscado por login: #{bruno.id} {bruno.nome}"
        )

        atualizado = gerenciador.atualizar_usuario(
            usuario_id=bruno.id,
            nome="Bruno Lima da Silva",
            cpf=bruno.cpf,
            email="bruno.lima@ubs.gov.br",
            telefone="84977776666",
            login="brunolima",
            perfil=Perfil.GESTOR,
        )

        print(
            f"Atualizado: {atualizado.nome} "
            f"[login={atualizado.login}] "
            f"({atualizado.perfil.value})"
        )

        desativado = gerenciador.desativar_usuario(
            atualizado.id
        )

        print(
            f"Desativado: {desativado.nome} "
            f"— ativo={desativado.ativo}"
        )

        print(
            "Usuários ativos: "
            + ", ".join(
                usuario.login
                for usuario in gerenciador.listar_usuarios(
                    apenas_ativos=True
                )
            )
        )

    except ErroDeDominio as erro:
        # ErroDeDominio é a raiz de todos os erros de negócio, inclusive
        # das falhas de persistência — um único except cobre o roteiro.
        print(
            f"Erro no CRUD de usuários: {erro}",
            file=sys.stderr,
        )

    print("\n--- Demonstração de autenticação ---")

    # Cenário 1: login e senha corretos.
    try:
        usuario = gerenciador.autenticar(
            login="ana",
            senha="SenhaSecreta1!",
        )

        print(
            f"Login OK: {usuario.nome} "
            f"({usuario.perfil.value})"
        )

    except ErroDeAutenticacao as erro:
        print(f"Login falhou: {erro}")

    # Cenário 2: senha incorreta.
    try:
        gerenciador.autenticar(
            login="ana",
            senha="senha_errada",
        )

    except CredenciaisInvalidas as erro:
        print(f"CredenciaisInvalidas: {erro}")

    # Cenário 3: login inexistente.
    try:
        gerenciador.autenticar(
            login="naoexiste",
            senha="qualquer",
        )

    except CredenciaisInvalidas as erro:
        print(f"CredenciaisInvalidas: {erro}")

    # Template Method: mesmo esqueleto de relatório,
    # formatos diferentes.
    print("\n--- Relatório de estatísticas de acesso (texto) ---")
    print(
        RelatorioDeAcessosTexto(
            repositorio_acessos
        ).gerar()
    )

    print("\n--- Relatório de estatísticas de acesso (CSV) ---")
    print(
        RelatorioDeAcessosCsv(
            repositorio_acessos
        ).gerar()
    )


if __name__ == "__main__":
    main()
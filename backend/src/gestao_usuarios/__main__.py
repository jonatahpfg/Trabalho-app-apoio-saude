"""Composição (fiação) do contexto — demonstra adicionar, listar e autenticar.

Este é um adaptador primário mínimo: monta o repositório adequado (RAM ou SQLite),
injeta-o no gerenciador e exercita os casos de uso.

Sprint 6: demonstra os padrões Proxy (autorização por perfil) e Observer
(eventos de autenticação com log e estatísticas).

Execução: ``python -m gestao_usuarios`` (a partir de ``backend/src``).
"""

from __future__ import annotations

import os
import sys

from .adaptadores.seletor_fabrica import obter_fabrica_repositorio
from .aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from .aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from .aplicacao.observer import (
    ObservadorDeEstatisticasDeAutenticacao,
    ObservadorDeLogDeAutenticacao,
    PublicadorDeEventosDeAutenticacao,
)
from .aplicacao.proxy import (
    ProxyGerenciadorDeUnidades,
    ProxyGerenciadorDeUsuarios,
)
from .aplicacao.relatorio_de_acessos_csv import RelatorioDeAcessosCsv
from .aplicacao.relatorio_de_acessos_texto import RelatorioDeAcessosTexto
from .dominio.erros import (
    AcessoNegado,
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeAutenticacao,
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
    repositorio_unidades = fabrica.criar_repositorio_unidade_basica_saude()

    # ------------------------------------------------------------------ #
    # Observer: configura publicador e observadores antes do gerenciador  #
    # ------------------------------------------------------------------ #
    print("\n--- Configurando padrão Observer (Sprint 6) ---")
    publicador = PublicadorDeEventosDeAutenticacao()
    obs_log = ObservadorDeLogDeAutenticacao()
    obs_stats = ObservadorDeEstatisticasDeAutenticacao()
    publicador.assinar(obs_log)
    publicador.assinar(obs_stats)
    print(f"  Observadores inscritos: {publicador.total_observadores}")

    gerenciador = GerenciadorDeUsuarios(
        repositorio,
        repositorio_acessos,
        publicador,          # <- Observer integrado
    )
    gerenciador_unidades = GerenciadorDeUnidades(repositorio_unidades)

    # 2. Cadastro de usuários.
    try:
        admin = gerenciador.adicionar_usuario(
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

        gestor = gerenciador.adicionar_usuario(
            nome="Carla Dias",
            cpf="11122233344",
            email="carla@ubs.gov.br",
            telefone="84977776666",
            login="carla",
            senha="GestorSenha3#",
            perfil=Perfil.GESTOR,
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

    print("\n--- Demonstração de autenticação ---")

    # Cenário 1: login e senha corretos → Observer notificado (sucesso).
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

    # Cenário 2: senha incorreta → Observer notificado (falha).
    try:
        gerenciador.autenticar(
            login="ana",
            senha="senha_errada",
        )

    except CredenciaisInvalidas as erro:
        print(f"CredenciaisInvalidas: {erro}")

    # Cenário 3: login inexistente → Observer notificado (falha).
    try:
        gerenciador.autenticar(
            login="naoexiste",
            senha="qualquer",
        )

    except CredenciaisInvalidas as erro:
        print(f"CredenciaisInvalidas: {erro}")

    # ------------------------------------------------------------------ #
    # Observer: exibe resumo das estatísticas                             #
    # ------------------------------------------------------------------ #
    print("\n--- Resumo Observer (estatísticas de autenticação) ---")
    resumo = obs_stats.resumo()
    print(
        f"  Total de tentativas : {resumo['total']}\n"
        f"  Sucessos            : {resumo['sucessos']}\n"
        f"  Falhas              : {resumo['falhas']}"
    )

    print(f"\n  Eventos registrados no log: {len(obs_log.historico)}")

    # ------------------------------------------------------------------ #
    # Proxy: autorização por perfil (Sprint 6)                           #
    # ------------------------------------------------------------------ #
    print("\n--- Demonstração Proxy — autorização por perfil (Sprint 6) ---")

    # Proxy para o usuário ADMINISTRADOR
    proxy_admin_usr = ProxyGerenciadorDeUsuarios(gerenciador, admin)
    proxy_admin_ubs = ProxyGerenciadorDeUnidades(gerenciador_unidades, admin)

    # Proxy para o usuário MÉDICO
    medico = gerenciador.listar_usuarios()[1]   # Bruno Lima (MEDICO)
    proxy_medico_usr = ProxyGerenciadorDeUsuarios(gerenciador, medico)
    proxy_medico_ubs = ProxyGerenciadorDeUnidades(gerenciador_unidades, medico)

    # Proxy para o usuário GESTOR
    proxy_gestor_ubs = ProxyGerenciadorDeUnidades(gerenciador_unidades, gestor)

    # Cenário A: ADMINISTRADOR lista usuários (permitido)
    try:
        usuarios = proxy_admin_usr.listar_usuarios()
        print(
            f"\n[PROXY] ADMINISTRADOR lista usuários "
            f"→ OK ({len(usuarios)} usuários)"
        )
    except AcessoNegado as e:
        print(f"\n[PROXY] Acesso negado: {e}")

    # Cenário B: MÉDICO tenta listar usuários (negado)
    try:
        proxy_medico_usr.listar_usuarios()
        print("[PROXY] MÉDICO lista usuários → OK")
    except AcessoNegado as e:
        print(f"[PROXY] MÉDICO lista usuários → AcessoNegado: {e}")

    # Cenário C: MÉDICO tenta adicionar usuário (negado)
    try:
        proxy_medico_usr.adicionar_usuario(
            nome="Teste",
            cpf="00000000000",
            email="teste@ubs.gov.br",
            telefone="84900000000",
            login="teste",
            senha="SenhaTeste1!",
            perfil=Perfil.MEDICO,
        )
        print("[PROXY] MÉDICO adiciona usuário → OK")
    except AcessoNegado as e:
        print(f"[PROXY] MÉDICO adiciona usuário → AcessoNegado: {e}")

    # Cenário D: GESTOR adiciona UBS (permitido)
    try:
        ubs = proxy_gestor_ubs.adicionar_unidade(
            nome="UBS Central",
            cnpj="11222333000181",
            endereco="Rua das Flores, 100",
            telefone="84333334444",
        )
        print(
            f"[PROXY] GESTOR adiciona UBS "
            f"→ OK (id={ubs.id}, nome={ubs.nome})"
        )
    except AcessoNegado as e:
        print(f"[PROXY] GESTOR adiciona UBS → AcessoNegado: {e}")

    # Cenário E: MÉDICO tenta remover UBS (negado)
    try:
        proxy_medico_ubs.remover_unidade(1)
        print("[PROXY] MÉDICO remove UBS → OK")
    except AcessoNegado as e:
        print(f"[PROXY] MÉDICO remove UBS → AcessoNegado: {e}")

    # Cenário F: ADMINISTRADOR remove UBS (permitido)
    try:
        proxy_admin_ubs.remover_unidade(1)
        print("[PROXY] ADMINISTRADOR remove UBS → OK")
    except AcessoNegado as e:
        print(f"[PROXY] Acesso negado: {e}")

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
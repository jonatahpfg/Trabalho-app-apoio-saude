"""Composição (fiação) do contexto — demonstra adicionar, listar e autenticar.

Este é um adaptador primário mínimo: monta o repositório adequado (RAM ou SQLite),
injeta-o no gerenciador e exercita os casos de uso.

Execução: ``python -m gestao_usuarios`` (a partir de ``backend/src``).
"""

from __future__ import annotations

import os
import sys

# Importar o novo repositório de banco de dados e as exceções
from .adaptadores.adaptador_arquivo_de_log import AdaptadorArquivoDeLog
from .adaptadores.arquivo_de_log_simples import ArquivoDeLogSimples
from .adaptadores.repositorio_registro_de_acesso_em_memoria import (
    RepositorioRegistroDeAcessoEmMemoria,
)
from .adaptadores.repositorio_usuario_em_memoria import RepositorioUsuarioEmMemoria
from .adaptadores.repositorio_usuario_banco_de_dados import RepositorioUsuarioBancoDeDados
from .aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from .aplicacao.relatorio_de_acessos_csv import RelatorioDeAcessosCsv
from .aplicacao.relatorio_de_acessos_texto import RelatorioDeAcessosTexto
from .dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeAutenticacao,
    ErroDePersistencia
)
from .dominio.usuario import Perfil


def main() -> None:
    # 1. Chaveamento de persistência usando Variável de Ambiente
    # Define 'memoria' como padrão. Se for definido como 'bd', usa SQLite.
    tipo_armazenamento = os.environ.get("STORAGE_TYPE", "memoria").lower()

    if tipo_armazenamento == "bd": # Essa estrutura de if/else depois vou trocar para uma estrutura com polimorfismo,
                                   # mas por enquanto é a forma mais simples de demonstrar o chaveamento de persistência. (Flavio)
        print("-> Inicializando armazenamento em Banco de Dados (SQLite)...")
        # Cria ou abre o arquivo local 'usuarios.db'
        repositorio = RepositorioUsuarioBancoDeDados("usuarios.db")
        # Adapter (Tarefa 5): o log de linhas de texto atende a porta de acessos
        repositorio_acessos = AdaptadorArquivoDeLog(ArquivoDeLogSimples("acessos.log"))
    else:
        print("-> Inicializando armazenamento em Memória (RAM)...")
        repositorio = RepositorioUsuarioEmMemoria()
        repositorio_acessos = RepositorioRegistroDeAcessoEmMemoria()

    gerenciador = GerenciadorDeUsuarios(repositorio, repositorio_acessos)

    # 2. Tratamento de Exceções de Persistência/Banco de Dados ao salvar
    try:
        # Nota: Ajustamos as senhas originais ("senha_secreta" -> "SenhaSecreta1!")
        # para que passem na validação de força de senha da entidade Usuario.
        gerenciador.adicionar_usuario(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@ubs.gov.br",
            telefone="84999990000",
            senha="SenhaSecreta1!",
            perfil=Perfil.ADMINISTRADOR,
        )
        gerenciador.adicionar_usuario(
            nome="Bruno Lima",
            cpf="98765432100",
            email="bruno@ubs.gov.br",
            telefone="84988887777",
            senha="OutraSenha2@",
            perfil=Perfil.MEDICO,
        )
    except (ErroDePersistencia, CpfDuplicado) as e:
        print(f"Erro Crítico de Persistência/Banco de Dados ao inicializar: {e}", file=sys.stderr)
        # Finaliza com erro pois o banco falhou ou o CPF/E-mail já está cadastrado
        return

    # 3. Listagem de Usuários cadastrados
    print("\nUsuários cadastrados:")
    for usuario in gerenciador.listar_usuarios():
        print(f"  #{usuario.id} {usuario.nome} ({usuario.perfil.value}) — ativo={usuario.ativo}")

    print("\n--- Demonstração de autenticação ---")

    # Cenário 1: credenciais corretas
    try:
        u = gerenciador.autenticar(email="ana@ubs.gov.br", senha="SenhaSecreta1!")
        print(f"Login OK: {u.nome} ({u.perfil.value})")
    except ErroDeAutenticacao as e:
        print(f"Login falhou: {e}")

    # Cenário 2: senha errada  →  CredenciaisInvalidas
    try:
        gerenciador.autenticar(email="ana@ubs.gov.br", senha="errada")
    except CredenciaisInvalidas as e:
        print(f"CredenciaisInvalidas: {e}")

    # Cenário 3: e-mail inexistente  →  CredenciaisInvalidas
    try:
        gerenciador.autenticar(email="naoexiste@ubs.gov.br", senha="qualquer")
    except CredenciaisInvalidas as e:
        print(f"CredenciaisInvalidas: {e}")

    # Template Method (Tarefa 5): mesmo esqueleto de relatório, formatos diferentes
    print("\n--- Relatório de estatísticas de acesso (texto) ---")
    print(RelatorioDeAcessosTexto(repositorio_acessos).gerar())

    print("\n--- Relatório de estatísticas de acesso (CSV) ---")
    print(RelatorioDeAcessosCsv(repositorio_acessos).gerar())


if __name__ == "__main__":
    main()
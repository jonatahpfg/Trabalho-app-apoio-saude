"""Composição (fiação) do contexto — demonstra adicionar, listar e autenticar.

Este é um adaptador primário mínimo: monta o repositório em memória, injeta-o no
gerenciador e exercita os casos de uso da Sprint 1.

Execução: ``python -m gestao_usuarios`` (a partir de ``backend/src``).
"""

from __future__ import annotations

from .adaptadores.repositorio_usuario_em_memoria import RepositorioUsuarioEmMemoria
from .aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from .dominio.erros import CredenciaisInvalidas, ErroDeAutenticacao, UsuarioInativo
from .dominio.usuario import Perfil


def main() -> None:
    gerenciador = GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())

    gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        senha="senha_secreta",
        perfil=Perfil.ADMINISTRADOR,
    )
    gerenciador.adicionar_usuario(
        nome="Bruno Lima",
        cpf="98765432100",
        email="bruno@ubs.gov.br",
        telefone="84988887777",
        senha="outra_senha",
        perfil=Perfil.MEDICO,
    )

    print("Usuários cadastrados:")
    for usuario in gerenciador.listar_usuarios():
        print(f"  #{usuario.id} {usuario.nome} ({usuario.perfil.value}) — ativo={usuario.ativo}")

    print("\n--- Demonstração de autenticação ---")

    # Cenário 1: credenciais corretas
    try:
        u = gerenciador.autenticar(email="ana@ubs.gov.br", senha="senha_secreta")
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


if __name__ == "__main__":
    main()

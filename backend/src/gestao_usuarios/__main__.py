"""Composição (fiação) do contexto — demonstra adicionar e listar usuários.

Este é um adaptador primário mínimo: monta o repositório em memória, injeta-o no
gerenciador e exercita os dois casos de uso da Sprint 1.

Execução: ``python -m gestao_usuarios`` (a partir de ``backend/src``).
"""

from __future__ import annotations

from .adaptadores.repositorio_usuario_em_memoria import RepositorioUsuarioEmMemoria
from .aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from .dominio.usuario import Perfil


def main() -> None:
    gerenciador = GerenciadorDeUsuarios(RepositorioUsuarioEmMemoria())

    gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        perfil=Perfil.ADMINISTRADOR,
    )
    gerenciador.adicionar_usuario(
        nome="Bruno Lima",
        cpf="98765432100",
        email="bruno@ubs.gov.br",
        telefone="84988887777",
        perfil=Perfil.MEDICO,
    )

    print("Usuários cadastrados:")
    for usuario in gerenciador.listar_usuarios():
        print(f"  #{usuario.id} {usuario.nome} ({usuario.perfil.value}) — ativo={usuario.ativo}")


if __name__ == "__main__":
    main()

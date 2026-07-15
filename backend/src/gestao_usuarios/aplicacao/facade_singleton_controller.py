"""Controlador que aplica os padrões GoF Facade e Singleton."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..adaptadores.repositorio_usuario_em_memoria import RepositorioUsuarioEmMemoria
from ..adaptadores.repositorio_usuario_banco_de_dados import RepositorioUsuarioBancoDeDados
from ..aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from ..dominio.usuario import Perfil, Usuario

if TYPE_CHECKING:
    from ..portas.repositorio_usuario import RepositorioUsuario


class FacadeSingletonController:
    """Fachada (Facade) e instância única (Singleton) para gestão de usuários.

    Aplica o padrão Facade expondo apenas os três casos de uso principais
    (adicionar, listar, autenticar) e escondendo a montagem interna do
    GerenciadorDeUsuarios e do repositório.

    Aplica o padrão Singleton garantindo uma única instância por processo,
    criada na primeira chamada a instancia().
    """

    # atributo de classe que guarda a instância única (Singleton)
    _instancia_unica: FacadeSingletonController | None = None

    def __init__(self, repositorio: RepositorioUsuario) -> None:
        self._gerenciador = GerenciadorDeUsuarios(repositorio)

    @classmethod
    def instancia(cls) -> FacadeSingletonController:
        """Ponto de acesso global à instância única (lazy initialization)."""
        if cls._instancia_unica is None:
            cls._instancia_unica = cls(cls._criar_repositorio())
        return cls._instancia_unica

    @classmethod
    def _criar_repositorio(cls) -> RepositorioUsuario:
        # Escolhe o repositório conforme a variável de ambiente STORAGE_TYPE.
        # "bd" → SQLite; qualquer outro valor → memória (padrão).
        tipo = os.environ.get("STORAGE_TYPE", "memoria").lower()
        if tipo == "bd":
            return RepositorioUsuarioBancoDeDados("usuarios.db")
        return RepositorioUsuarioEmMemoria()

    @classmethod
    def resetar_instancia(cls) -> None:
        """Reseta a instância única. Usado apenas nos testes."""
        cls._instancia_unica = None

    # --- Facade: interface simplificada para o subsistema ---

    def adicionar_usuario(
        self,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        senha: str,
        perfil: Perfil | str,
    ) -> Usuario:
        return self._gerenciador.adicionar_usuario(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            senha=senha,
            perfil=perfil,
        )

    def listar_usuarios(self) -> list[Usuario]:
        return self._gerenciador.listar_usuarios()

    def autenticar(self, *, email: str, senha: str) -> Usuario:
        return self._gerenciador.autenticar(email=email, senha=senha)

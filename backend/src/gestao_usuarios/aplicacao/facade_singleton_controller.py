"""Controlador que aplica os padrões GoF Facade e Singleton.

Sprint 3 — Padrões 1: a fachada agora integra tanto o GerenciadorDeUsuarios
quanto o GerenciadorDeUnidades, e expõe o método
``obter_quantidade_total_entidades_cadastradas`` conforme solicitado.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..adaptadores.seletor_fabrica import obter_fabrica_repositorio
from ..aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from ..aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from ..dominio.unidade_basica_saude import UnidadeBasicaSaude
from ..dominio.usuario import Perfil, Usuario

if TYPE_CHECKING:
    from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
    from ..portas.repositorio_unidade_basica_saude import RepositorioUnidadeBasicaSaude
    from ..portas.repositorio_usuario import RepositorioUsuario


class FacadeSingletonController:
    """Fachada (Facade) e instância única (Singleton) para gestão do sistema.

    Aplica o padrão **Facade** expondo uma interface simplificada que esconde
    a montagem interna dos gerenciadores (GerenciadorDeUsuarios e
    GerenciadorDeUnidades) e seus repositórios.

    Aplica o padrão **Singleton** garantindo uma única instância por processo,
    criada na primeira chamada a ``instancia()``.

    Sprint 3 — inclui o método ``obter_quantidade_total_entidades_cadastradas``
    que retorna a soma de todas as entidades persistidas no sistema.
    """

    # atributo de classe que guarda a instância única (Singleton)
    _instancia_unica: FacadeSingletonController | None = None

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuario,
        repositorio_unidades: RepositorioUnidadeBasicaSaude,
        repositorio_acessos: RepositorioRegistroDeAcesso | None = None,
    ) -> None:
        self._gerenciador_usuarios = GerenciadorDeUsuarios(
            repositorio_usuarios,
            repositorio_acessos,
        )
        self._gerenciador_unidades = GerenciadorDeUnidades(
            repositorio_unidades
        )

    @classmethod
    def instancia(cls) -> FacadeSingletonController:
        """Ponto de acesso global à instância única (lazy initialization)."""
        if cls._instancia_unica is None:
            repo_usuarios, repo_unidades, repo_acessos = cls._criar_repositorios()
            cls._instancia_unica = cls(
                repo_usuarios,
                repo_unidades,
                repo_acessos,
            )

        return cls._instancia_unica

    @classmethod
    def _criar_repositorios(
        cls,
    ) -> tuple[
        RepositorioUsuario,
        RepositorioUnidadeBasicaSaude,
        RepositorioRegistroDeAcesso,
    ]:
        """Escolhe os repositórios utilizando a fábrica abstrata de persistência."""
        tipo = os.environ.get("STORAGE_TYPE", "memoria").lower()
        fabrica = obter_fabrica_repositorio(tipo)

        repo_usuarios = fabrica.criar_repositorio_usuario()
        repo_unidades = fabrica.criar_repositorio_unidade_basica_saude()
        repo_acessos = fabrica.criar_repositorio_registro_de_acesso()

        return repo_usuarios, repo_unidades, repo_acessos

    @classmethod
    def resetar_instancia(cls) -> None:
        """Reseta a instância única. Usado apenas nos testes."""
        cls._instancia_unica = None

    # --- Facade: interface simplificada para o subsistema ---

    # ---- Usuários ----

    def adicionar_usuario(
        self,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        senha: str,
        perfil: Perfil | str,
    ) -> Usuario:
        return self._gerenciador_usuarios.adicionar_usuario(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            senha=senha,
            perfil=perfil,
        )

    def listar_usuarios(self) -> list[Usuario]:
        return self._gerenciador_usuarios.listar_usuarios()

    def autenticar(self, *, login: str, senha: str) -> Usuario:
        return self._gerenciador_usuarios.autenticar(
            login=login,
            senha=senha,
        )

    # ---- Unidades Básicas de Saúde ----

    def adicionar_unidade(
        self,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        return self._gerenciador_unidades.adicionar_unidade(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

    def listar_unidades(
        self,
        *,
        apenas_ativas: bool = False,
    ) -> list[UnidadeBasicaSaude]:
        return self._gerenciador_unidades.listar_unidades(
            apenas_ativas=apenas_ativas
        )

    def buscar_unidade_por_id(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        return self._gerenciador_unidades.buscar_unidade_por_id(
            unidade_id
        )

    def atualizar_unidade(
        self,
        *,
        unidade_id: int,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        return self._gerenciador_unidades.atualizar_unidade(
            unidade_id=unidade_id,
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

    def remover_unidade(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        return self._gerenciador_unidades.remover_unidade(
            unidade_id
        )

    # ---- Método exigido pela Sprint 3 ----

    def obter_quantidade_total_entidades_cadastradas(self) -> int:
        """Retorna a quantidade total de entidades cadastradas no sistema.

        Soma o total de usuários e de unidades básicas de saúde persistidos.
        """
        total_usuarios = len(
            self._gerenciador_usuarios.listar_usuarios()
        )
        total_unidades = len(
            self._gerenciador_unidades.listar_unidades()
        )

        return total_usuarios + total_unidades
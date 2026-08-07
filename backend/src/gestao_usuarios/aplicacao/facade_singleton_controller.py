"""Controlador que aplica os padrões GoF Facade, Singleton e Command.

A fachada integra o GerenciadorDeUsuarios e o GerenciadorDeUnidades,
utilizando o padrão Command para desacoplar as operações de negócio e
centralizar a execução através do ExecutorDeComandos.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from ..adaptadores.seletor_fabrica import obter_fabrica_repositorio
from ..dominio.unidade_basica_saude import UnidadeBasicaSaude
from ..dominio.usuario import Perfil, Usuario
from .comandos import (
    Comando,
    ComandoAdicionarUnidade,
    ComandoAdicionarUsuario,
    ComandoAtualizarUnidade,
    ComandoAutenticarUsuario,
    ComandoBuscarUnidadePorId,
    ComandoContarTotalEntidades,
    ComandoDesfazerAtualizacaoDeUnidade,
    ComandoListarUnidades,
    ComandoListarUsuarios,
    ComandoRemoverUnidade,
    ExecutorDeComandos,
)
from .gerenciador_de_unidades import GerenciadorDeUnidades
from .gerenciador_de_usuarios import GerenciadorDeUsuarios

if TYPE_CHECKING:
    from ..portas.repositorio_registro_de_acesso import (
        RepositorioRegistroDeAcesso,
    )
    from ..portas.repositorio_unidade_basica_saude import (
        RepositorioUnidadeBasicaSaude,
    )
    from ..portas.repositorio_usuario import RepositorioUsuario


class FacadeSingletonController:
    """Fachada e instância única para gestão do sistema.

    Aplica o padrão Facade expondo uma interface simplificada que
    esconde os gerenciadores e seus repositórios.

    Aplica o padrão Singleton garantindo uma única instância por
    processo, criada na primeira chamada a ``instancia()``.

    Aplica o padrão Command convertendo cada requisição em um objeto
    de comando e delegando sua execução ao ``ExecutorDeComandos``.
    """

    _instancia_unica: FacadeSingletonController | None = None

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuario,
        repositorio_unidades: RepositorioUnidadeBasicaSaude,
        repositorio_acessos: RepositorioRegistroDeAcesso | None = None,
        executor: ExecutorDeComandos | None = None,
    ) -> None:
        self._gerenciador_usuarios = GerenciadorDeUsuarios(
            repositorio_usuarios,
            repositorio_acessos,
        )
        self._gerenciador_unidades = GerenciadorDeUnidades(
            repositorio_unidades
        )
        self._executor = executor or ExecutorDeComandos()

    @property
    def executor(self) -> ExecutorDeComandos:
        """Retorna o executor de comandos associado à fachada."""
        return self._executor

    @classmethod
    def instancia(cls) -> FacadeSingletonController:
        """Retorna a instância única da fachada."""
        if cls._instancia_unica is None:
            (
                repo_usuarios,
                repo_unidades,
                repo_acessos,
            ) = cls._criar_repositorios()

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
        """Cria os repositórios usando a fábrica selecionada."""
        tipo = os.environ.get(
            "STORAGE_TYPE",
            "memoria",
        ).lower()

        fabrica = obter_fabrica_repositorio(tipo)

        repo_usuarios = fabrica.criar_repositorio_usuario()
        repo_unidades = (
            fabrica.criar_repositorio_unidade_basica_saude()
        )
        repo_acessos = (
            fabrica.criar_repositorio_registro_de_acesso()
        )

        return (
            repo_usuarios,
            repo_unidades,
            repo_acessos,
        )

    @classmethod
    def resetar_instancia(cls) -> None:
        """Reseta a instância única para isolamento dos testes."""
        cls._instancia_unica = None

    # --- Execução genérica via Command ---

    def executar_comando(
        self,
        comando: Comando,
    ) -> Any:
        """Executa um comando concreto pelo executor da fachada."""
        return self._executor.executar(comando)

    # --- Usuários ---

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
        comando = ComandoAdicionarUsuario(
            self._gerenciador_usuarios,
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            senha=senha,
            perfil=perfil,
        )

        return self._executor.executar(comando)

    def listar_usuarios(self) -> list[Usuario]:
        comando = ComandoListarUsuarios(
            self._gerenciador_usuarios
        )

        return self._executor.executar(comando)

    def autenticar(
        self,
        *,
        login: str,
        senha: str,
    ) -> Usuario:
        comando = ComandoAutenticarUsuario(
            self._gerenciador_usuarios,
            login=login,
            senha=senha,
        )

        return self._executor.executar(comando)

    # --- Unidades Básicas de Saúde ---

    def adicionar_unidade(
        self,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        comando = ComandoAdicionarUnidade(
            self._gerenciador_unidades,
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

        return self._executor.executar(comando)

    def listar_unidades(
        self,
        *,
        apenas_ativas: bool = False,
    ) -> list[UnidadeBasicaSaude]:
        comando = ComandoListarUnidades(
            self._gerenciador_unidades,
            apenas_ativas=apenas_ativas,
        )

        return self._executor.executar(comando)

    def buscar_unidade_por_id(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        comando = ComandoBuscarUnidadePorId(
            self._gerenciador_unidades,
            unidade_id=unidade_id,
        )

        return self._executor.executar(comando)

    def atualizar_unidade(
        self,
        *,
        unidade_id: int,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        comando = ComandoAtualizarUnidade(
            self._gerenciador_unidades,
            unidade_id=unidade_id,
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

        return self._executor.executar(comando)

    def desfazer_ultima_atualizacao_de_unidade(
        self,
    ) -> UnidadeBasicaSaude:
        """Desfaz a última atualização bem-sucedida de uma UBS."""
        comando = ComandoDesfazerAtualizacaoDeUnidade(
            self._gerenciador_unidades
        )

        return self._executor.executar(comando)

    def remover_unidade(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        comando = ComandoRemoverUnidade(
            self._gerenciador_unidades,
            unidade_id=unidade_id,
        )

        return self._executor.executar(comando)

    # --- Contagem de entidades ---

    def obter_quantidade_total_entidades_cadastradas(
        self,
    ) -> int:
        """Retorna a quantidade total de entidades cadastradas."""
        comando = ComandoContarTotalEntidades(
            self._gerenciador_usuarios,
            self._gerenciador_unidades,
        )

        return self._executor.executar(comando)


FacadeDoSistema = FacadeSingletonController
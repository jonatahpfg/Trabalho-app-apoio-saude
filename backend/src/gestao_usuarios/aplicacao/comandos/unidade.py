"""Comandos concretos para operações com Unidades Básicas de Saúde (UBS)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...dominio.unidade_basica_saude import UnidadeBasicaSaude
from .base import Comando

if TYPE_CHECKING:
    from ..gerenciador_de_unidades import GerenciadorDeUnidades


class ComandoAdicionarUnidade(Comando):
    """Comando concreto para cadastrar uma nova UBS."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> None:
        self._gerenciador = gerenciador
        self._nome = nome
        self._cnpj = cnpj
        self._endereco = endereco
        self._telefone = telefone

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cnpj(self) -> str:
        return self._cnpj

    @property
    def endereco(self) -> str:
        return self._endereco

    @property
    def telefone(self) -> str:
        return self._telefone

    def executar(self) -> UnidadeBasicaSaude:
        return self._gerenciador.adicionar_unidade(
            nome=self._nome,
            cnpj=self._cnpj,
            endereco=self._endereco,
            telefone=self._telefone,
        )


class ComandoListarUnidades(Comando):
    """Comando concreto para listar as UBS cadastradas."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        *,
        apenas_ativas: bool = False,
    ) -> None:
        self._gerenciador = gerenciador
        self._apenas_ativas = apenas_ativas

    @property
    def apenas_ativas(self) -> bool:
        return self._apenas_ativas

    def executar(self) -> list[UnidadeBasicaSaude]:
        return self._gerenciador.listar_unidades(
            apenas_ativas=self._apenas_ativas
        )


class ComandoBuscarUnidadePorId(Comando):
    """Comando concreto para buscar uma UBS pelo seu identificador único."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        unidade_id: int,
    ) -> None:
        self._gerenciador = gerenciador
        self._unidade_id = unidade_id

    @property
    def unidade_id(self) -> int:
        return self._unidade_id

    def executar(self) -> UnidadeBasicaSaude:
        return self._gerenciador.buscar_unidade_por_id(self._unidade_id)


class ComandoAtualizarUnidade(Comando):
    """Comando concreto para atualizar os dados de uma UBS existente."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        *,
        unidade_id: int,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> None:
        self._gerenciador = gerenciador
        self._unidade_id = unidade_id
        self._nome = nome
        self._cnpj = cnpj
        self._endereco = endereco
        self._telefone = telefone

    @property
    def unidade_id(self) -> int:
        return self._unidade_id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cnpj(self) -> str:
        return self._cnpj

    @property
    def endereco(self) -> str:
        return self._endereco

    @property
    def telefone(self) -> str:
        return self._telefone

    def executar(self) -> UnidadeBasicaSaude:
        return self._gerenciador.atualizar_unidade(
            unidade_id=self._unidade_id,
            nome=self._nome,
            cnpj=self._cnpj,
            endereco=self._endereco,
            telefone=self._telefone,
        )


class ComandoRemoverUnidade(Comando):
    """Comando concreto para desativar logicamente uma UBS (soft delete)."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        unidade_id: int,
    ) -> None:
        self._gerenciador = gerenciador
        self._unidade_id = unidade_id

    @property
    def unidade_id(self) -> int:
        return self._unidade_id

    def executar(self) -> UnidadeBasicaSaude:
        return self._gerenciador.remover_unidade(self._unidade_id)


class ComandoDesfazerAtualizacaoDeUnidade(Comando):
    """Comando para restaurar o estado anterior da última UBS atualizada."""

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
    ) -> None:
        self._gerenciador = gerenciador

    def executar(self) -> UnidadeBasicaSaude:
        return (
            self._gerenciador
            .desfazer_ultima_atualizacao_de_unidade()
        )
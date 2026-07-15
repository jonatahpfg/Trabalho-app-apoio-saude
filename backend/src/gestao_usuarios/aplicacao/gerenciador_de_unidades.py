"""Casos de uso de gerenciamento de Unidades Básicas de Saúde — Controle (ECB)."""

from __future__ import annotations

from ..dominio.erros import CnpjDuplicado, UnidadeNaoEncontrada
from ..dominio.unidade_basica_saude import UnidadeBasicaSaude
from ..portas.repositorio_unidade_basica_saude import RepositorioUnidadeBasicaSaude


class GerenciadorDeUnidades:
    """Orquestra o CRUD completo de Unidades Básicas de Saúde."""

    def __init__(self, repositorio: RepositorioUnidadeBasicaSaude) -> None:
        self._repositorio = repositorio

    # --- Create ---

    def adicionar_unidade(
        self,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        """Valida os dados, garante CNPJ único e persiste a UBS."""
        unidade = UnidadeBasicaSaude.criar(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )
        if self._repositorio.buscar_por_cnpj(unidade.cnpj) is not None:
            raise CnpjDuplicado(
                f"Já existe uma unidade com o CNPJ {unidade.cnpj}"
            )
        return self._repositorio.salvar(unidade)

    # --- Read ---

    def listar_unidades(
        self, *, apenas_ativas: bool = False
    ) -> list[UnidadeBasicaSaude]:
        """Devolve todas as unidades cadastradas (opcionalmente só as ativas)."""
        todas = self._repositorio.buscar_todas()
        if apenas_ativas:
            return [u for u in todas if u.ativa]
        return todas

    def buscar_unidade_por_id(self, unidade_id: int) -> UnidadeBasicaSaude:
        """Busca uma UBS pelo id ou lança ``UnidadeNaoEncontrada``."""
        unidade = self._repositorio.buscar_por_id(unidade_id)
        if unidade is None:
            raise UnidadeNaoEncontrada(
                f"Unidade com id {unidade_id} não encontrada."
            )
        return unidade

    # --- Update ---

    def atualizar_unidade(
        self,
        *,
        unidade_id: int,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        """Atualiza os dados de uma UBS existente."""
        existente = self.buscar_unidade_por_id(unidade_id)

        atualizada = UnidadeBasicaSaude.criar(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )
        atualizada.id = existente.id
        atualizada.ativa = existente.ativa

        # Verifica duplicidade de CNPJ em outra unidade
        por_cnpj = self._repositorio.buscar_por_cnpj(atualizada.cnpj)
        if por_cnpj is not None and por_cnpj.id != atualizada.id:
            raise CnpjDuplicado(
                f"Já existe outra unidade com o CNPJ {atualizada.cnpj}"
            )

        return self._repositorio.salvar(atualizada)

    # --- Delete (lógico) ---

    def remover_unidade(self, unidade_id: int) -> UnidadeBasicaSaude:
        """Desativa logicamente uma UBS (soft delete)."""
        unidade = self.buscar_unidade_por_id(unidade_id)
        unidade.ativa = False
        return self._repositorio.salvar(unidade)

"""Casos de uso de gerenciamento de Unidades Básicas de Saúde — Controle (ECB)."""

from __future__ import annotations

from ..dominio.erros import (
    CnpjDuplicado,
    UnidadeNaoEncontrada,
)
from ..dominio.unidade_basica_saude import UnidadeBasicaSaude
from ..portas.repositorio_unidade_basica_saude import (
    RepositorioUnidadeBasicaSaude,
)
from .historico_de_unidade import HistoricoDeUnidade


class GerenciadorDeUnidades:
    """Orquestra o CRUD e o desfazer de Unidades Básicas de Saúde."""

    def __init__(
        self,
        repositorio: RepositorioUnidadeBasicaSaude,
        historico: HistoricoDeUnidade | None = None,
    ) -> None:
        self._repositorio = repositorio
        self._historico = historico or HistoricoDeUnidade()

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
        self,
        *,
        apenas_ativas: bool = False,
    ) -> list[UnidadeBasicaSaude]:
        """Devolve todas as unidades, opcionalmente apenas as ativas."""
        todas = self._repositorio.buscar_todas()

        if apenas_ativas:
            return [unidade for unidade in todas if unidade.ativa]

        return todas

    def buscar_unidade_por_id(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        """Busca uma UBS pelo ID ou lança UnidadeNaoEncontrada."""
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
        """Atualiza uma UBS e guarda seu estado anterior em um Memento."""
        existente = self.buscar_unidade_por_id(unidade_id)

        # A criação valida todos os novos dados antes de guardar o Memento.
        atualizada = UnidadeBasicaSaude.criar(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

        atualizada.id = existente.id
        atualizada.ativa = existente.ativa

        # Impede que a UBS receba o CNPJ pertencente a outra unidade.
        por_cnpj = self._repositorio.buscar_por_cnpj(
            atualizada.cnpj
        )

        if (
            por_cnpj is not None
            and por_cnpj.id != atualizada.id
        ):
            raise CnpjDuplicado(
                "Já existe outra unidade com o CNPJ "
                f"{atualizada.cnpj}"
            )

        # Captura o estado anterior, mas ainda não altera o histórico.
        memento = existente.criar_memento()

        # Primeiro confirma que a atualização foi persistida.
        resultado = self._repositorio.salvar(atualizada)

        # Somente uma atualização bem-sucedida pode ser desfeita.
        self._historico.salvar(memento)

        return resultado

    def desfazer_ultima_atualizacao_de_unidade(
        self,
    ) -> UnidadeBasicaSaude:
        """Restaura a UBS alterada na última atualização bem-sucedida."""
        memento = self._historico.obter_ultimo()

        if memento.id is None:
            raise UnidadeNaoEncontrada(
                "O estado salvo não possui um ID de unidade."
            )

        unidade = self.buscar_unidade_por_id(memento.id)

        # Verifica se o CNPJ antigo passou a pertencer a outra UBS.
        por_cnpj = self._repositorio.buscar_por_cnpj(
            memento.cnpj
        )

        if (
            por_cnpj is not None
            and por_cnpj.id != memento.id
        ):
            raise CnpjDuplicado(
                "Não foi possível restaurar o CNPJ "
                f"{memento.cnpj}, pois ele pertence a outra unidade."
            )

        unidade.restaurar(memento)

        restaurada = self._repositorio.salvar(unidade)

        # O desfazer só pode ser utilizado uma vez para essa atualização.
        self._historico.descartar_ultimo()

        return restaurada

    # --- Delete lógico ---

    def remover_unidade(
        self,
        unidade_id: int,
    ) -> UnidadeBasicaSaude:
        """Desativa logicamente uma UBS."""
        unidade = self.buscar_unidade_por_id(unidade_id)
        unidade.ativa = False

        return self._repositorio.salvar(unidade)
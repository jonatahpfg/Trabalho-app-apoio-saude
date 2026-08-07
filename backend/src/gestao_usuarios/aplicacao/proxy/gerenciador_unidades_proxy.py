"""Proxy de autorização para GerenciadorDeUnidades — padrão GoF Proxy.

O ProxyGerenciadorDeUnidades envolve o GerenciadorDeUnidades real e verifica
o perfil do usuário autenticado antes de delegar cada operação. Operações não
permitidas lançam AcessoNegado sem nunca alcançar o objeto real.

Participantes do padrão (GoF):
- Subject:        GerenciadorDeUnidades (interface compartilhada implícita)
- RealSubject:    GerenciadorDeUnidades (o gerenciador concreto)
- Proxy:          ProxyGerenciadorDeUnidades (esta classe)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...dominio.erros import AcessoNegado
from ...dominio.unidade_basica_saude import UnidadeBasicaSaude
from ...dominio.usuario import Perfil, Usuario

if TYPE_CHECKING:
    from ..gerenciador_de_unidades import GerenciadorDeUnidades


class ProxyGerenciadorDeUnidades:
    """Proxy de autorização por perfil para operações de Unidade Básica de Saúde.

    Recebe o usuário autenticado no momento da criação e usa seu perfil
    para decidir se cada operação pode ser delegada ao gerenciador real.

    Matriz de permissões
    --------------------
    Operação                              | ADMINISTRADOR | GESTOR | MÉDICO
    --------------------------------------|:---:|:---:|:---:
    adicionar_unidade                     |  ✅  |  ✅  |  ❌
    listar_unidades                       |  ✅  |  ✅  |  ✅
    buscar_unidade_por_id                 |  ✅  |  ✅  |  ✅
    atualizar_unidade                     |  ✅  |  ✅  |  ❌
    desfazer_ultima_atualizacao_de_unidade|  ✅  |  ✅  |  ❌
    remover_unidade                       |  ✅  |  ❌  |  ❌
    """

    # Perfis autorizados por operação
    _PERFIS_ADICIONAR: frozenset[Perfil] = frozenset(
        {Perfil.ADMINISTRADOR, Perfil.GESTOR}
    )
    _PERFIS_LEITURA: frozenset[Perfil] = frozenset(
        {Perfil.ADMINISTRADOR, Perfil.GESTOR, Perfil.MEDICO}
    )
    _PERFIS_ATUALIZAR: frozenset[Perfil] = frozenset(
        {Perfil.ADMINISTRADOR, Perfil.GESTOR}
    )
    _PERFIS_REMOVER: frozenset[Perfil] = frozenset({Perfil.ADMINISTRADOR})

    def __init__(
        self,
        gerenciador: GerenciadorDeUnidades,
        usuario_autenticado: Usuario,
    ) -> None:
        self._gerenciador = gerenciador
        self._usuario = usuario_autenticado

    # --- helpers internos ---

    def _verificar_perfil(
        self,
        perfis_permitidos: frozenset[Perfil],
        nome_operacao: str,
    ) -> None:
        """Verifica se o perfil do usuário autenticado está autorizado.

        Raises:
            AcessoNegado: se o perfil não está na lista de permitidos.
        """
        if self._usuario.perfil not in perfis_permitidos:
            nomes = ", ".join(p.value for p in sorted(perfis_permitidos, key=lambda p: p.value))
            raise AcessoNegado(
                f"Perfil '{self._usuario.perfil.value}' não tem permissão para "
                f"'{nome_operacao}'. Perfis autorizados: {nomes}."
            )

    # --- interface pública (espelha GerenciadorDeUnidades) ---

    def adicionar_unidade(
        self,
        *,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        """Adiciona uma UBS — exige ADMINISTRADOR ou GESTOR."""
        self._verificar_perfil(self._PERFIS_ADICIONAR, "adicionar_unidade")
        return self._gerenciador.adicionar_unidade(
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

    def listar_unidades(
        self, *, apenas_ativas: bool = False
    ) -> list[UnidadeBasicaSaude]:
        """Lista UBS — permitido para todos os perfis."""
        self._verificar_perfil(self._PERFIS_LEITURA, "listar_unidades")
        return self._gerenciador.listar_unidades(apenas_ativas=apenas_ativas)

    def buscar_unidade_por_id(self, unidade_id: int) -> UnidadeBasicaSaude:
        """Busca UBS por id — permitido para todos os perfis."""
        self._verificar_perfil(self._PERFIS_LEITURA, "buscar_unidade_por_id")
        return self._gerenciador.buscar_unidade_por_id(unidade_id)

    def atualizar_unidade(
        self,
        *,
        unidade_id: int,
        nome: str,
        cnpj: str,
        endereco: str,
        telefone: str,
    ) -> UnidadeBasicaSaude:
        """Atualiza UBS — exige ADMINISTRADOR ou GESTOR."""
        self._verificar_perfil(self._PERFIS_ATUALIZAR, "atualizar_unidade")
        return self._gerenciador.atualizar_unidade(
            unidade_id=unidade_id,
            nome=nome,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
        )

    def desfazer_ultima_atualizacao_de_unidade(self) -> UnidadeBasicaSaude:
        """Desfaz a última atualização de UBS — exige ADMINISTRADOR ou GESTOR.

        Desfazer reescreve os dados da unidade, então exige os mesmos perfis
        de ``atualizar_unidade``: é a operação que ela reverte.
        """
        self._verificar_perfil(
            self._PERFIS_ATUALIZAR,
            "desfazer_ultima_atualizacao_de_unidade",
        )
        return (
            self._gerenciador
            .desfazer_ultima_atualizacao_de_unidade()
        )

    def remover_unidade(self, unidade_id: int) -> UnidadeBasicaSaude:
        """Remove (desativa) UBS — exige somente ADMINISTRADOR."""
        self._verificar_perfil(self._PERFIS_REMOVER, "remover_unidade")
        return self._gerenciador.remover_unidade(unidade_id)

"""Proxy de autorização para GerenciadorDeUsuarios — padrão GoF Proxy.

O ProxyGerenciadorDeUsuarios envolve o GerenciadorDeUsuarios real e verifica
o perfil do usuário autenticado antes de delegar cada operação. Operações não
permitidas lançam AcessoNegado sem nunca alcançar o objeto real.

Participantes do padrão (GoF):
- Subject:        GerenciadorDeUsuarios (interface compartilhada implícita)
- RealSubject:    GerenciadorDeUsuarios (o gerenciador concreto)
- Proxy:          ProxyGerenciadorDeUsuarios (esta classe)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...dominio.erros import AcessoNegado
from ...dominio.usuario import Perfil, Usuario

if TYPE_CHECKING:
    from ..gerenciador_de_usuarios import GerenciadorDeUsuarios


class ProxyGerenciadorDeUsuarios:
    """Proxy de autorização por perfil para operações de usuário.

    Recebe o usuário autenticado no momento da criação e usa seu perfil
    para decidir se cada operação pode ser delegada ao gerenciador real.

    Matriz de permissões
    --------------------
    Operação                 | ADMINISTRADOR | GESTOR | MÉDICO
    -------------------------|:---:|:---:|:---:
    adicionar_usuario        |  ✅  |  ❌  |  ❌
    listar_usuarios          |  ✅  |  ✅  |  ❌
    buscar_usuario_por_id    |  ✅  |  ✅  |  ❌
    buscar_usuario_por_login |  ✅  |  ✅  |  ❌
    atualizar_usuario        |  ✅  |  ❌  |  ❌
    desativar_usuario        |  ✅  |  ❌  |  ❌
    reativar_usuario         |  ✅  |  ❌  |  ❌
    autenticar               |  ✅  |  ✅  |  ✅  (operação pública)

    O cadastro de usuário guarda dado pessoal, então a leitura fica restrita
    aos perfis que já podiam listar, e toda escrita — incluir, alterar,
    desativar e reativar — é privativa do ADMINISTRADOR.
    """

    # Perfis autorizados por operação
    _PERFIS_ADICIONAR: frozenset[Perfil] = frozenset({Perfil.ADMINISTRADOR})
    _PERFIS_LEITURA: frozenset[Perfil] = frozenset(
        {Perfil.ADMINISTRADOR, Perfil.GESTOR}
    )
    _PERFIS_ATUALIZAR: frozenset[Perfil] = frozenset({Perfil.ADMINISTRADOR})
    _PERFIS_DESATIVAR: frozenset[Perfil] = frozenset({Perfil.ADMINISTRADOR})

    def __init__(
        self,
        gerenciador: GerenciadorDeUsuarios,
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

    # --- interface pública (espelha GerenciadorDeUsuarios) ---

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
        """Adiciona um usuário — exige perfil ADMINISTRADOR."""
        self._verificar_perfil(self._PERFIS_ADICIONAR, "adicionar_usuario")
        return self._gerenciador.adicionar_usuario(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            senha=senha,
            perfil=perfil,
        )

    def listar_usuarios(
        self,
        *,
        apenas_ativos: bool = False,
    ) -> list[Usuario]:
        """Lista usuários — exige perfil ADMINISTRADOR ou GESTOR."""
        self._verificar_perfil(self._PERFIS_LEITURA, "listar_usuarios")
        return self._gerenciador.listar_usuarios(
            apenas_ativos=apenas_ativos
        )

    def buscar_usuario_por_id(self, usuario_id: int) -> Usuario:
        """Busca um usuário pelo id — exige perfil ADMINISTRADOR ou GESTOR."""
        self._verificar_perfil(
            self._PERFIS_LEITURA,
            "buscar_usuario_por_id",
        )
        return self._gerenciador.buscar_usuario_por_id(usuario_id)

    def buscar_usuario_por_login(self, login: str) -> Usuario:
        """Busca um usuário pelo login — exige perfil ADMINISTRADOR ou GESTOR."""
        self._verificar_perfil(
            self._PERFIS_LEITURA,
            "buscar_usuario_por_login",
        )
        return self._gerenciador.buscar_usuario_por_login(login)

    def atualizar_usuario(
        self,
        *,
        usuario_id: int,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        perfil: Perfil | str,
        senha: str | None = None,
    ) -> Usuario:
        """Atualiza um usuário — exige perfil ADMINISTRADOR.

        A alteração de perfil e a redefinição de senha passam por aqui, o que
        torna esta a operação mais sensível do cadastro: um perfil não
        autorizado poderia promover a si mesmo a ADMINISTRADOR.
        """
        self._verificar_perfil(
            self._PERFIS_ATUALIZAR,
            "atualizar_usuario",
        )
        return self._gerenciador.atualizar_usuario(
            usuario_id=usuario_id,
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            perfil=perfil,
            senha=senha,
        )

    def desativar_usuario(self, usuario_id: int) -> Usuario:
        """Desativa um usuário — exige perfil ADMINISTRADOR."""
        self._verificar_perfil(
            self._PERFIS_DESATIVAR,
            "desativar_usuario",
        )
        return self._gerenciador.desativar_usuario(usuario_id)

    def reativar_usuario(self, usuario_id: int) -> Usuario:
        """Reativa um usuário — exige perfil ADMINISTRADOR."""
        self._verificar_perfil(
            self._PERFIS_DESATIVAR,
            "reativar_usuario",
        )
        return self._gerenciador.reativar_usuario(usuario_id)

    def autenticar(self, *, login: str, senha: str) -> Usuario:
        """Autentica um usuário — operação pública, sem restrição de perfil."""
        # autenticar é a porta de entrada do sistema; não requer perfil prévio
        return self._gerenciador.autenticar(login=login, senha=senha)

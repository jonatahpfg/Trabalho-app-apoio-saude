"""Casos de uso de gerenciamento de usuários — o Controle do padrão ECB."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
    UsuarioInativo,
)
from ..dominio.registro_de_acesso import RegistroDeAcesso
from ..dominio.senha import verificar
from ..dominio.usuario import Perfil, Usuario
from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
from ..portas.repositorio_usuario import RepositorioUsuario

if TYPE_CHECKING:
    from .observer.evento import EventoDeAutenticacao
    from .observer.publicador import PublicadorDeEventosDeAutenticacao


class GerenciadorDeUsuarios:
    """Orquestra a adição, a listagem e a autenticação de usuários."""

    def __init__(
        self,
        repositorio: RepositorioUsuario,
        repositorio_acessos: RepositorioRegistroDeAcesso | None = None,
        publicador: PublicadorDeEventosDeAutenticacao | None = None,
    ) -> None:
        self._repositorio = repositorio
        # Porta opcional: sem ela o gerenciador funciona normalmente,
        # apenas não gera estatísticas de acesso.
        self._repositorio_acessos = repositorio_acessos
        # Observer opcional: sem ele o gerenciador não publica eventos.
        self._publicador = publicador

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
        """Valida os dados, garante CPF e login únicos e persiste o usuário."""
        usuario = Usuario.criar(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            senha=senha,
            perfil=perfil,
        )

        if self._repositorio.buscar_por_cpf(usuario.cpf) is not None:
            raise CpfDuplicado(
                f"Já existe um usuário com o CPF {usuario.cpf}"
            )

        if self._repositorio.buscar_por_login(usuario.login) is not None:
            raise LoginDuplicado(
                f"Já existe um usuário com o login {usuario.login!r}"
            )

        return self._repositorio.salvar(usuario)

    def listar_usuarios(self) -> list[Usuario]:
        """Devolve todos os usuários cadastrados."""
        return self._repositorio.buscar_todos()

    def autenticar(self, *, login: str, senha: str) -> Usuario:
        """Valida credenciais e devolve o usuário autenticado.

        Quando a porta de acessos está configurada, cada tentativa real de
        login (sucesso ou falha) é registrada para as estatísticas de acesso.

        Aplica as boas práticas dos artigos do professor:

        - Taborda — "Seja específico": lança CredenciaisInvalidas (não
          uma Exception genérica) quando o login não existe ou a senha
          está errada; lança UsuarioInativo quando a conta está bloqueada.
          Ambas derivam de ErroDeAutenticacao, permitindo que o chamador
          capture qualquer falha de login com um único tipo se quiser.

        - PLoP 2018 (Coelho et al.) — evita "Catch Generic" e
          "Destructive Wrapping": nenhuma exceção é capturada aqui sem ser
          relançada; o rastro de causa é preservado implicitamente porque
          nenhum wrapping acontece — as exceções são lançadas diretamente
          sem encapsular outra.

        Raises:
            ErroDeValidacao: login ou senha em branco.
            CredenciaisInvalidas: login não cadastrado ou senha errada.
            UsuarioInativo: usuário existe, senha correta, mas conta inativa.
        """
        # Pré-condições verificadas primeiro (Taborda: lance o quanto antes)
        if not login or not str(login).strip():
            raise ErroDeValidacao("Campo obrigatório ausente: login")

        if not senha or not str(senha).strip():
            raise ErroDeValidacao("Campo obrigatório ausente: senha")

        login = str(login).strip()

        usuario = self._repositorio.buscar_por_login(login)

        # Não distinguimos "login inexistente" de "senha errada" para não
        # vazar informação ao atacante — CredenciaisInvalidas cobre os dois.
        # A comparação é feita contra o hash (NF007): a senha em texto puro
        # nunca é armazenada nem comparada diretamente.
        if usuario is None or not verificar(senha, usuario.senha_hash):
            self._registrar_acesso(login, sucesso=False)
            self._publicar_evento(login, sucesso=False)
            raise CredenciaisInvalidas(
                "Login ou senha incorretos."
            )

        # Só após confirmar as credenciais verificamos se a conta está ativa.
        # UsuarioInativo é separado de CredenciaisInvalidas porque a ação
        # corretiva é diferente: reativar a conta, não redefinir a senha.
        if not usuario.ativo:
            self._registrar_acesso(login, sucesso=False)
            self._publicar_evento(login, sucesso=False)
            raise UsuarioInativo(
                f"A conta do usuário '{usuario.nome}' está desativada."
            )

        self._registrar_acesso(login, sucesso=True)
        self._publicar_evento(login, sucesso=True)
        return usuario

    def _registrar_acesso(self, login: str, *, sucesso: bool) -> None:
        """Registra a tentativa de login para as estatísticas de acesso.

        Tentativas barradas nas pré-condições (campos em branco) não são
        registradas: não chegam a ser uma tentativa real de autenticação.
        """
        if self._repositorio_acessos is None:
            return

        self._repositorio_acessos.salvar(
            RegistroDeAcesso.criar(
                login=login,
                sucesso=sucesso,
            )
        )

    def _publicar_evento(self, login: str, *, sucesso: bool) -> None:
        """Publica um EventoDeAutenticacao para os observadores inscritos.

        Padrão Observer (Sprint 6): o gerenciador notifica o publicador sem
        conhecer os observadores concretos. A importação é local para evitar
        dependência circular entre os subpacotes.
        """
        if self._publicador is None:
            return

        from .observer.evento import EventoDeAutenticacao  # noqa: PLC0415

        self._publicador.notificar(
            EventoDeAutenticacao(login=login, sucesso=sucesso)
        )
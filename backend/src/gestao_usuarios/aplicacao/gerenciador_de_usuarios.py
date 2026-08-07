"""Casos de uso de gerenciamento de usuários — o Controle do padrão ECB."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..dominio.erros import (
    CpfDuplicado,
    CredenciaisInvalidas,
    ErroDeValidacao,
    LoginDuplicado,
    UsuarioInativo,
    UsuarioNaoEncontrado,
)
from ..dominio.registro_de_acesso import RegistroDeAcesso
from ..dominio.senha import verificar
from ..dominio.usuario import Perfil, Usuario
from ..dominio.validacoes.validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)
from ..portas.repositorio_registro_de_acesso import RepositorioRegistroDeAcesso
from ..portas.repositorio_usuario import RepositorioUsuario

if TYPE_CHECKING:
    from .observer.publicador import PublicadorDeEventosDeAutenticacao


class GerenciadorDeUsuarios:
    """Orquestra o CRUD e a autenticação de usuários."""

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

    # --- Create ---

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

        self._garantir_cpf_disponivel(usuario)
        self._garantir_login_disponivel(usuario)

        return self._repositorio.salvar(usuario)

    # --- Read ---

    def listar_usuarios(
        self,
        *,
        apenas_ativos: bool = False,
    ) -> list[Usuario]:
        """Devolve todos os usuários, opcionalmente apenas os ativos."""
        todos = self._repositorio.buscar_todos()

        if apenas_ativos:
            return [usuario for usuario in todos if usuario.ativo]

        return todos

    def buscar_usuario_por_id(
        self,
        usuario_id: int,
    ) -> Usuario:
        """Busca um usuário pelo id ou lança ``UsuarioNaoEncontrado``.

        Diferente das buscas do repositório, que devolvem ``None``, o caso de
        uso é explícito quanto à ausência do registro (Taborda: seja
        específico e lance o quanto antes).

        Raises:
            UsuarioNaoEncontrado: não existe usuário com o id informado.
        """
        usuario = self._repositorio.buscar_por_id(usuario_id)

        if usuario is None:
            raise UsuarioNaoEncontrado(
                f"Usuário com id {usuario_id} não encontrado."
            )

        return usuario

    def buscar_usuario_por_login(
        self,
        login: str,
    ) -> Usuario:
        """Busca um usuário pelo login ou lança ``UsuarioNaoEncontrado``.

        Raises:
            ErroDeValidacao: login não informado.
            UsuarioNaoEncontrado: não existe usuário com o login informado.
        """
        login = ValidadorTextoObrigatorio.validar(
            login,
            "login",
        )

        usuario = self._repositorio.buscar_por_login(login)

        if usuario is None:
            raise UsuarioNaoEncontrado(
                f"Usuário com login {login!r} não encontrado."
            )

        return usuario

    # --- Update ---

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
        """Atualiza os dados cadastrais de um usuário existente.

        A senha é opcional: quando informada, é validada pela política de
        senhas e substituída pelo novo hash; quando omitida, a senha atual
        é preservada.

        O identificador e a situação de ativação nunca são alterados aqui —
        a desativação tem seu próprio caso de uso.

        Raises:
            UsuarioNaoEncontrado: não existe usuário com o id informado.
            ErroDeValidacao: algum dado informado é inválido.
            CpfDuplicado: o CPF já pertence a outro usuário.
            LoginDuplicado: o login já pertence a outro usuário.
        """
        existente = self.buscar_usuario_por_id(usuario_id)

        # A entidade revalida todos os dados antes de qualquer persistência.
        atualizado = existente.atualizar_dados(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            perfil=perfil,
        )

        if senha is not None:
            atualizado = atualizado.alterar_senha(senha)

        self._garantir_cpf_disponivel(atualizado)
        self._garantir_login_disponivel(atualizado)

        return self._repositorio.salvar(atualizado)

    # --- Delete lógico ---

    def desativar_usuario(
        self,
        usuario_id: int,
    ) -> Usuario:
        """Desativa logicamente um usuário, bloqueando seu acesso ao sistema.

        O registro nunca é apagado: apenas passa a ser recusado na
        autenticação com ``UsuarioInativo``.

        Raises:
            UsuarioNaoEncontrado: não existe usuário com o id informado.
        """
        usuario = self.buscar_usuario_por_id(usuario_id)

        return self._repositorio.salvar(usuario.desativar())

    def reativar_usuario(
        self,
        usuario_id: int,
    ) -> Usuario:
        """Reativa um usuário previamente desativado.

        Raises:
            UsuarioNaoEncontrado: não existe usuário com o id informado.
        """
        usuario = self.buscar_usuario_por_id(usuario_id)

        return self._repositorio.salvar(usuario.ativar())

    # --- Autenticação ---

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

    # --- Regras de unicidade ---

    def _garantir_cpf_disponivel(self, usuario: Usuario) -> None:
        """Impede que o CPF do usuário pertença a outro cadastro.

        Na criação o usuário ainda não possui id, então qualquer registro
        encontrado caracteriza duplicidade. Na atualização, o próprio
        usuário é ignorado na comparação.

        Raises:
            CpfDuplicado: o CPF já pertence a outro usuário.
        """
        encontrado = self._repositorio.buscar_por_cpf(usuario.cpf)

        if encontrado is not None and encontrado.id != usuario.id:
            raise CpfDuplicado(
                f"Já existe um usuário com o CPF {usuario.cpf}"
            )

    def _garantir_login_disponivel(self, usuario: Usuario) -> None:
        """Impede que o login do usuário pertença a outro cadastro.

        Raises:
            LoginDuplicado: o login já pertence a outro usuário.
        """
        encontrado = self._repositorio.buscar_por_login(usuario.login)

        if encontrado is not None and encontrado.id != usuario.id:
            raise LoginDuplicado(
                f"Já existe um usuário com o login {usuario.login!r}"
            )

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
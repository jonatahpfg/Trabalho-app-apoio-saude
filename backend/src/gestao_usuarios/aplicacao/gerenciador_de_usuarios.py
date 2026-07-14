"""Casos de uso de gerenciamento de usuários — o Controle do padrão ECB."""

from __future__ import annotations

from ..dominio.erros import CpfDuplicado, CredenciaisInvalidas, ErroDeValidacao, UsuarioInativo
from ..dominio.senha import verificar
from ..dominio.usuario import Perfil, Usuario
from ..portas.repositorio_usuario import RepositorioUsuario


class GerenciadorDeUsuarios:
    """Orquestra a adição, a listagem e a autenticação de usuários."""

    def __init__(self, repositorio: RepositorioUsuario) -> None:
        self._repositorio = repositorio

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
        """Valida os dados, garante CPF único e persiste o usuário."""
        usuario = Usuario.criar(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            senha=senha,
            perfil=perfil,
        )
        if self._repositorio.buscar_por_cpf(usuario.cpf) is not None:
            raise CpfDuplicado(f"Já existe um usuário com o CPF {usuario.cpf}")
        return self._repositorio.salvar(usuario)

    def listar_usuarios(self) -> list[Usuario]:
        """Devolve todos os usuários cadastrados."""
        return self._repositorio.buscar_todos()

    def autenticar(self, *, email: str, senha: str) -> Usuario:
        """Valida credenciais e devolve o usuário autenticado.

        Aplica as boas práticas dos artigos do professor:

        - Taborda — "Seja específico": lança CredenciaisInvalidas (não
          uma Exception genérica) quando o e-mail não existe ou a senha
          está errada; lança UsuarioInativo quando a conta está bloqueada.
          Ambas derivam de ErroDeAutenticacao, permitindo que o chamador
          capture qualquer falha de login com um único tipo se quiser.

        - PLoP 2018 (Coelho et al.) — evita "Catch Generic" e
          "Destructive Wrapping": nenhuma exceção é capturada aqui sem ser
          relançada; o rastro de causa é preservado implicitamente porque
          nenhum wrapping acontece — as exceções são lançadas diretamente
          sem encapsular outra.

        Raises:
            ErroDeValidacao: e-mail ou senha em branco.
            CredenciaisInvalidas: e-mail não cadastrado ou senha errada.
            UsuarioInativo: usuário existe, senha correta, mas conta inativa.
        """
        # Pré-condições verificadas primeiro (Taborda: lance o quanto antes)
        if not email or not str(email).strip():
            raise ErroDeValidacao("Campo obrigatório ausente: email")
        if not senha or not str(senha).strip():
            raise ErroDeValidacao("Campo obrigatório ausente: senha")

        usuario = self._repositorio.buscar_por_email(email)

        # Não distinguimos "e-mail inexistente" de "senha errada" para não
        # vazar informação ao atacante — CredenciaisInvalidas cobre os dois.
        # A comparação é feita contra o hash (NF007): a senha em texto puro
        # nunca é armazenada nem comparada diretamente.
        if usuario is None or not verificar(senha, usuario.senha_hash):
            raise CredenciaisInvalidas(
                "E-mail ou senha incorretos."
            )

        # Só após confirmar as credenciais verificamos se a conta está ativa.
        # UsuarioInativo é separado de CredenciaisInvalidas porque a ação
        # corretiva é diferente: reativar a conta, não redefinir a senha.
        if not usuario.ativo:
            raise UsuarioInativo(
                f"A conta do usuário '{usuario.nome}' está desativada."
            )

        return usuario

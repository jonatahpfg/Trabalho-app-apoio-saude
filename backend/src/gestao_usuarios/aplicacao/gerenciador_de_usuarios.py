"""Casos de uso de gerenciamento de usuários — o Controle do padrão ECB."""

from __future__ import annotations

from ..dominio.erros import CpfDuplicado
from ..dominio.usuario import Perfil, Usuario
from ..portas.repositorio_usuario import RepositorioUsuario


class GerenciadorDeUsuarios:
    """Orquestra a adição e a listagem de usuários sobre um RepositorioUsuario."""

    def __init__(self, repositorio: RepositorioUsuario) -> None:
        self._repositorio = repositorio

    def adicionar_usuario(
        self,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Valida os dados, garante CPF único e persiste o usuário."""
        usuario = Usuario.criar(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            perfil=perfil,
        )
        if self._repositorio.buscar_por_cpf(usuario.cpf) is not None:
            raise CpfDuplicado(f"Já existe um usuário com o CPF {usuario.cpf}")
        return self._repositorio.salvar(usuario)

    def listar_usuarios(self) -> list[Usuario]:
        """Devolve todos os usuários cadastrados."""
        return self._repositorio.buscar_todos()

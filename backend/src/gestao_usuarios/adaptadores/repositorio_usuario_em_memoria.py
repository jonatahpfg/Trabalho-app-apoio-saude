"""Adaptador de persistência em memória (RAM) da porta RepositorioUsuario."""

from __future__ import annotations

from dataclasses import replace

from ..dominio.usuario import Usuario


class RepositorioUsuarioEmMemoria:
    """Guarda os usuários numa coleção em memória. Some quando o processo termina."""

    def __init__(self) -> None:
        self._usuarios: dict[int, Usuario] = {}
        self._proximo_id = 1

    def salvar(self, usuario: Usuario) -> Usuario:
        if usuario.id is None:
            usuario = replace(usuario, id=self._proximo_id)
            self._proximo_id += 1
        self._usuarios[usuario.id] = usuario
        return replace(usuario)

    def buscar_todos(self) -> list[Usuario]:
        return [replace(usuario) for usuario in self._usuarios.values()]

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        for usuario in self._usuarios.values():
            if usuario.cpf == cpf:
                return replace(usuario)
        return None

    def buscar_por_email(self, email: str) -> Usuario | None:
        for usuario in self._usuarios.values():
            if usuario.email == email:
                return replace(usuario)
        return None

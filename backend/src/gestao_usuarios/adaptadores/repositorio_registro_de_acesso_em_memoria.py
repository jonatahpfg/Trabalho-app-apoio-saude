"""Adaptador de persistência em memória (RAM) da porta RepositorioRegistroDeAcesso."""

from __future__ import annotations

from dataclasses import replace

from ..dominio.registro_de_acesso import RegistroDeAcesso


class RepositorioRegistroDeAcessoEmMemoria:
    """Guarda os registros de acesso numa coleção em memória. Some quando o processo termina."""

    def __init__(self) -> None:
        self._registros: dict[int, RegistroDeAcesso] = {}
        self._proximo_id = 1

    def salvar(self, registro: RegistroDeAcesso) -> RegistroDeAcesso:
        if registro.id is None:
            registro = replace(registro, id=self._proximo_id)
            self._proximo_id += 1
        self._registros[registro.id] = registro
        return replace(registro)

    def buscar_todos(self) -> list[RegistroDeAcesso]:
        return [replace(registro) for registro in self._registros.values()]

"""Entidade RegistroDeAcesso — evento de tentativa de autenticação."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .erros import ErroDeValidacao


@dataclass
class RegistroDeAcesso:
    """Evento registrado a cada tentativa de autenticação.

    Guarda o login informado, e não uma referência ao usuário, porque
    tentativas realizadas com logins inexistentes também precisam aparecer
    nas estatísticas de acesso.

    Use ``RegistroDeAcesso.criar`` para garantir as invariantes.
    """

    login: str
    sucesso: bool
    data_hora: datetime
    id: int | None = None

    @classmethod
    def criar(
        cls,
        *,
        login: str,
        sucesso: bool,
        data_hora: datetime | None = None,
    ) -> RegistroDeAcesso:
        """Cria um registro válido ou lança ``ErroDeValidacao``.

        Quando ``data_hora`` não é informada, utiliza o momento atual.
        """

        if login is None or not str(login).strip():
            raise ErroDeValidacao(
                "Campo obrigatório ausente: login"
            )

        if not isinstance(sucesso, bool):
            raise ErroDeValidacao(
                f"Valor inválido para sucesso: {sucesso!r}"
            )

        return cls(
            login=str(login).strip(),
            sucesso=sucesso,
            data_hora=data_hora or datetime.now(),
        )
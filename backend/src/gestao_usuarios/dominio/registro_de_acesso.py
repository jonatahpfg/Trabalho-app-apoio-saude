"""Entidade RegistroDeAcesso — evento de tentativa de autenticação."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .erros import ErroDeValidacao


@dataclass
class RegistroDeAcesso:
    """Evento de login registrado a cada tentativa de autenticação.

    Guarda o e-mail informado (e não uma referência ao usuário) porque
    tentativas com e-mail inexistente também precisam aparecer nas
    estatísticas de acesso. Use ``RegistroDeAcesso.criar`` para garantir
    as invariantes.
    """

    email: str
    sucesso: bool
    data_hora: datetime
    id: int | None = None

    @classmethod
    def criar(
        cls,
        *,
        email: str,
        sucesso: bool,
        data_hora: datetime | None = None,
    ) -> RegistroDeAcesso:
        """Cria um registro válido ou lança ``ErroDeValidacao``.

        Quando ``data_hora`` não é informada, usa o momento atual.
        """
        if email is None or not str(email).strip():
            raise ErroDeValidacao("Campo obrigatório ausente: email")
        if not isinstance(sucesso, bool):
            raise ErroDeValidacao(f"Valor inválido para sucesso: {sucesso!r}")

        return cls(
            email=str(email).strip(),
            sucesso=sucesso,
            data_hora=data_hora or datetime.now(),
        )

"""Adapter (GoF) da porta RepositorioRegistroDeAcesso para ArquivoDeLogSimples.

Papéis do padrão nesta implementação:

- **Target**: a porta ``RepositorioRegistroDeAcesso`` — a interface que o
  núcleo espera.
- **Adaptee**: ``ArquivoDeLogSimples`` — componente existente que só entende
  linhas de texto.
- **Adapter**: ``AdaptadorArquivoDeLog`` — traduz ``RegistroDeAcesso`` de/para
  linhas de log, permitindo que o componente incompatível atenda à porta.

Formato de cada linha: ``id;sucesso;data_hora_iso;email`` (e-mail por último
para tolerar e-mails que contenham o separador).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from ..dominio.erros import ErroDeAcessoAoArquivo
from ..dominio.registro_de_acesso import RegistroDeAcesso
from .arquivo_de_log_simples import ArquivoDeLogSimples

_SEPARADOR = ";"
_TOTAL_DE_CAMPOS = 4


class AdaptadorArquivoDeLog:
    """Implementa a porta RepositorioRegistroDeAcesso sobre um log de texto."""

    def __init__(self, arquivo_de_log: ArquivoDeLogSimples) -> None:
        self._arquivo_de_log = arquivo_de_log

    def salvar(self, registro: RegistroDeAcesso) -> RegistroDeAcesso:
        try:
            if registro.id is None:
                registro = replace(registro, id=len(self._arquivo_de_log.ler_linhas()) + 1)
            self._arquivo_de_log.anotar(_registro_para_linha(registro))
            return replace(registro)
        except OSError as erro:
            raise ErroDeAcessoAoArquivo("Falha ao gravar registro de acesso no log.") from erro

    def buscar_todos(self) -> list[RegistroDeAcesso]:
        try:
            linhas = self._arquivo_de_log.ler_linhas()
        except OSError as erro:
            raise ErroDeAcessoAoArquivo("Falha ao ler o log de acessos.") from erro
        return [_linha_para_registro(linha) for linha in linhas if linha.strip()]


def _registro_para_linha(registro: RegistroDeAcesso) -> str:
    sucesso = "1" if registro.sucesso else "0"
    return _SEPARADOR.join(
        [str(registro.id), sucesso, registro.data_hora.isoformat(), registro.email]
    )


def _linha_para_registro(linha: str) -> RegistroDeAcesso:
    partes = linha.split(_SEPARADOR, _TOTAL_DE_CAMPOS - 1)
    if len(partes) != _TOTAL_DE_CAMPOS:
        raise ErroDeAcessoAoArquivo(f"Linha corrompida no log de acessos: {linha!r}")
    id_texto, sucesso_texto, data_hora_texto, email = partes
    try:
        return RegistroDeAcesso(
            id=int(id_texto),
            sucesso=sucesso_texto == "1",
            data_hora=datetime.fromisoformat(data_hora_texto),
            email=email,
        )
    except ValueError as erro:
        raise ErroDeAcessoAoArquivo(
            f"Linha corrompida no log de acessos: {linha!r}"
        ) from erro

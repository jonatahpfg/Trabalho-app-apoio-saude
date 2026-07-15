"""Componente de log em arquivo texto — o Adaptee do padrão Adapter (Tarefa 5).

Representa um componente pré-existente com interface própria e incompatível
com as portas do núcleo: só sabe anotar linhas de texto no fim de um arquivo
e lê-las de volta. Não conhece nenhuma entidade do domínio — quem precisar
gravar objetos deve usar um Adapter (ver ``adaptador_arquivo_de_log.py``).
"""

from __future__ import annotations

from pathlib import Path


class ArquivoDeLogSimples:
    """Anota e lê linhas de texto em um arquivo de log."""

    def __init__(self, caminho: str) -> None:
        self._caminho = Path(caminho)

    def anotar(self, linha: str) -> None:
        """Acrescenta uma linha ao fim do arquivo, criando-o se não existir."""
        with open(self._caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(linha + "\n")

    def ler_linhas(self) -> list[str]:
        """Devolve todas as linhas do arquivo, sem a quebra de linha final.

        Arquivo inexistente equivale a log vazio.
        """
        if not self._caminho.exists():
            return []
        with open(self._caminho, encoding="utf-8") as arquivo:
            return [linha.rstrip("\n") for linha in arquivo]

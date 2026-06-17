"""Adaptador de persistência em Banco de Dados SQLite (BD) da porta RepositorioUsuario."""

from __future__ import annotations

import sqlite3
from dataclasses import replace

from ..dominio.erros import ErroDeAcessoAoBanco
from ..dominio.usuario import Usuario


class RepositorioUsuarioBancoDeDados:
    """Implementação simples do repositório em SQLite contendo apenas criação da tabela e inserção."""

    def __init__(self, caminho_db: str = ":memory:") -> None:
        self.caminho_db = caminho_db
        try:
            self._criar_tabela()
        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco("Falha ao inicializar o banco de dados.", e) from e

    def _obter_conexao(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho_db)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_tabela(self) -> None:
        with self._obter_conexao() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    telefone TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    perfil TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def salvar(self, usuario: Usuario) -> Usuario:
        """Salva (insere) o usuário no banco de dados SQLite."""
        try:
            with self._obter_conexao() as conn:
                if usuario.id is None:
                    # Inserir novo usuário
                    cursor = conn.execute(
                        """
                        INSERT INTO usuarios (nome, cpf, email, telefone, senha, perfil, ativo)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            usuario.nome,
                            usuario.cpf,
                            usuario.email,
                            usuario.telefone,
                            usuario.senha,
                            usuario.perfil.value,
                            1 if usuario.ativo else 0,
                        ),
                    )
                    novo_id = cursor.lastrowid
                    return replace(usuario, id=novo_id)
                else:
                    # Atualizar usuário existente
                    conn.execute(
                        """
                        UPDATE usuarios
                        SET nome = ?, cpf = ?, email = ?, telefone = ?, senha = ?, perfil = ?, ativo = ?
                        WHERE id = ?
                        """,
                        (
                            usuario.nome,
                            usuario.cpf,
                            usuario.email,
                            usuario.telefone,
                            usuario.senha,
                            usuario.perfil.value,
                            1 if usuario.ativo else 0,
                            usuario.id,
                        ),
                    )
                    return replace(usuario)
        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco(f"Erro ao salvar usuário com CPF {usuario.cpf}.", e) from e

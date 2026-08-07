"""Adaptador de persistência em Banco de Dados SQLite (BD) da porta RepositorioUsuario."""

from __future__ import annotations

import sqlite3
from dataclasses import replace

from ..dominio.erros import ErroDeAcessoAoBanco
from ..dominio.usuario import Perfil, Usuario


class RepositorioUsuarioBancoDeDados:
    """Implementação da porta RepositorioUsuario em SQLite."""

    def __init__(self, caminho_db: str = ":memory:") -> None:
        self.caminho_db = caminho_db
        try:
            # Conexão única mantida pelo repositório: com ":memory:" cada
            # sqlite3.connect() criaria um banco novo e vazio.
            self._conexao = sqlite3.connect(self.caminho_db)
            self._conexao.row_factory = sqlite3.Row
            self._criar_tabela()
        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco(
                "Falha ao inicializar o banco de dados.", e
            ) from e

    def _obter_conexao(self) -> sqlite3.Connection:
        return self._conexao

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
                    login TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    perfil TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def salvar(self, usuario: Usuario) -> Usuario:
        """Salva (insere ou atualiza) o usuário no banco de dados SQLite."""
        try:
            with self._obter_conexao() as conn:
                if usuario.id is None:
                    # Inserir novo usuário
                    cursor = conn.execute(
                        """
                        INSERT INTO usuarios (
                            nome,
                            cpf,
                            email,
                            telefone,
                            login,
                            senha_hash,
                            perfil,
                            ativo
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            usuario.nome,
                            usuario.cpf,
                            usuario.email,
                            usuario.telefone,
                            usuario.login,
                            usuario.senha_hash,
                            usuario.perfil.value,
                            1 if usuario.ativo else 0,
                        ),
                    )
                    novo_id = cursor.lastrowid
                    return replace(usuario, id=novo_id)

                # Atualizar usuário existente
                conn.execute(
                    """
                    UPDATE usuarios
                    SET
                        nome = ?,
                        cpf = ?,
                        email = ?,
                        telefone = ?,
                        login = ?,
                        senha_hash = ?,
                        perfil = ?,
                        ativo = ?
                    WHERE id = ?
                    """,
                    (
                        usuario.nome,
                        usuario.cpf,
                        usuario.email,
                        usuario.telefone,
                        usuario.login,
                        usuario.senha_hash,
                        usuario.perfil.value,
                        1 if usuario.ativo else 0,
                        usuario.id,
                    ),
                )
                return replace(usuario)

        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco(
                f"Erro ao salvar usuário com CPF {usuario.cpf}.", e
            ) from e

    def buscar_todos(self) -> list[Usuario]:
        """Devolve todos os usuários cadastrados."""
        try:
            with self._obter_conexao() as conn:
                linhas = conn.execute(
                    "SELECT * FROM usuarios"
                ).fetchall()

                return [
                    _linha_para_usuario(linha)
                    for linha in linhas
                ]
        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco(
                "Erro ao listar usuários.", e
            ) from e

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Devolve o usuário com o id informado, ou ``None`` se não existir."""
        return self._buscar_por_campo("id", usuario_id)

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        """Devolve o usuário com o CPF informado, ou ``None`` se não existir."""
        return self._buscar_por_campo("cpf", cpf)

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Devolve o usuário com o e-mail informado, ou ``None`` se não existir."""
        return self._buscar_por_campo("email", email)

    def buscar_por_login(self, login: str) -> Usuario | None:
        """Devolve o usuário com o login informado, ou ``None`` se não existir."""
        return self._buscar_por_campo("login", login)

    def _buscar_por_campo(
        self,
        campo: str,
        valor: object,
    ) -> Usuario | None:
        # ``campo`` nunca vem do usuário final: é sempre uma constante
        # definida nos métodos públicos acima. O valor consultado segue
        # parametrizado, protegendo a consulta contra SQL injection.
        try:
            with self._obter_conexao() as conn:
                linha = conn.execute(
                    f"SELECT * FROM usuarios WHERE {campo} = ?",
                    (valor,),
                ).fetchone()

                return (
                    _linha_para_usuario(linha)
                    if linha is not None
                    else None
                )

        except sqlite3.Error as e:
            raise ErroDeAcessoAoBanco(
                f"Erro ao buscar usuário por {campo}.", e
            ) from e


def _linha_para_usuario(linha: sqlite3.Row) -> Usuario:
    """Converte uma linha da tabela ``usuarios`` na entidade de domínio."""
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        cpf=linha["cpf"],
        email=linha["email"],
        telefone=linha["telefone"],
        login=linha["login"],
        senha_hash=linha["senha_hash"],
        perfil=Perfil(linha["perfil"]),
        ativo=bool(linha["ativo"]),
    )
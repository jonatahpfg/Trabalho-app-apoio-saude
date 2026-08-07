"""Entidade Usuario e o enum Perfil — o núcleo do domínio."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .senha import gerar_hash
from .validacoes.validador_email import ValidadorEmail
from .validacoes.validador_login import ValidadorLogin
from .validacoes.validador_perfil import ValidadorPerfil
from .validacoes.validador_senha import ValidadorSenha
from .validacoes.validador_texto_obrigatorio import (
    ValidadorTextoObrigatorio,
)


class Perfil(str, Enum):
    """Perfil de acesso do usuário (RF03)."""

    ADMINISTRADOR = "ADMINISTRADOR"
    GESTOR = "GESTOR"
    MEDICO = "MEDICO"


@dataclass(frozen=True)
class DadosCadastraisDeUsuario:
    """Dados cadastrais já validados de um usuário.

    Existe para que a criação e a atualização compartilhem exatamente as
    mesmas regras de validação, sem duplicá-las na entidade.
    """

    nome: str
    cpf: str
    email: str
    telefone: str
    login: str
    perfil: Perfil


@dataclass
class Usuario:
    """Usuário do sistema.

    Use ``Usuario.criar`` para garantir as invariantes.
    """

    nome: str
    cpf: str
    email: str
    telefone: str
    login: str
    senha_hash: str
    perfil: Perfil
    ativo: bool = True
    id: int | None = None

    @classmethod
    def criar(
        cls,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        senha: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Cria um usuário válido ou lança ``ErroDeValidacao``.

        As regras de validação são delegadas para classes específicas,
        reduzindo o acoplamento da entidade e facilitando a manutenção
        e a evolução das regras de negócio.

        O login é obrigatório e deve possuir no máximo 12 caracteres.

        A senha é validada em texto puro e armazenada apenas como hash.
        A entidade nunca armazena a senha original.
        """
        dados = cls._validar_dados_cadastrais(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            perfil=perfil,
        )

        senha = ValidadorSenha.validar(
            senha,
            nome=dados.nome,
            email=dados.email,
        )

        return cls(
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            telefone=dados.telefone,
            login=dados.login,
            senha_hash=gerar_hash(senha),
            perfil=dados.perfil,
        )

    def atualizar_dados(
        self,
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        perfil: Perfil | str,
    ) -> Usuario:
        """Devolve uma cópia do usuário com os dados cadastrais atualizados.

        As mesmas regras aplicadas na criação são revalidadas aqui, de modo
        que um usuário nunca chega a existir em estado inválido.

        O identificador, a senha e a situação de ativação são preservados:
        a alteração de senha é feita por ``alterar_senha`` e a desativação
        por ``desativar``, cada uma com sua própria regra de negócio.

        Raises:
            ErroDeValidacao: qualquer dado cadastral informado é inválido.
        """
        dados = self._validar_dados_cadastrais(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            login=login,
            perfil=perfil,
        )

        return replace(
            self,
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            telefone=dados.telefone,
            login=dados.login,
            perfil=dados.perfil,
        )

    def alterar_senha(self, senha: str) -> Usuario:
        """Devolve uma cópia do usuário com a nova senha já convertida em hash.

        A senha em texto puro nunca é armazenada (NF007): apenas o hash
        resultante substitui o anterior.

        Raises:
            ErroDeValidacao: a nova senha não atende à política de senhas.
        """
        senha = ValidadorSenha.validar(
            senha,
            nome=self.nome,
            email=self.email,
        )

        return replace(
            self,
            senha_hash=gerar_hash(senha),
        )

    def desativar(self) -> Usuario:
        """Devolve uma cópia do usuário marcada como inativa.

        A exclusão é sempre lógica: o histórico do usuário é preservado e
        apenas o acesso ao sistema é bloqueado.
        """
        return replace(self, ativo=False)

    def ativar(self) -> Usuario:
        """Devolve uma cópia do usuário marcada como ativa."""
        return replace(self, ativo=True)

    @staticmethod
    def _validar_dados_cadastrais(
        *,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        login: str,
        perfil: Perfil | str,
    ) -> DadosCadastraisDeUsuario:
        """Valida e normaliza os dados cadastrais comuns à criação e à atualização."""
        return DadosCadastraisDeUsuario(
            nome=ValidadorTextoObrigatorio.validar(
                nome,
                "nome",
            ),
            cpf=ValidadorTextoObrigatorio.validar(
                cpf,
                "cpf",
            ),
            email=ValidadorEmail.validar(
                email,
            ),
            telefone=ValidadorTextoObrigatorio.validar(
                telefone,
                "telefone",
            ),
            login=ValidadorLogin.validar(
                login,
            ),
            perfil=ValidadorPerfil.validar(
                perfil,
                Perfil,
            ),
        )
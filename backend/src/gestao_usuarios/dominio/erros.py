"""Erros do domínio de gerenciamento de usuários."""


class ErroDeDominio(Exception):
    """Erro base do domínio."""


class ErroDeValidacao(ErroDeDominio):
    """Dados de usuário inválidos."""


class CpfDuplicado(ErroDeDominio):
    """Já existe um usuário cadastrado com o mesmo CPF."""

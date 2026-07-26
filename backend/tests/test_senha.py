"""Testes do módulo de hash de senha (NF007)."""

from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import (
    GerenciadorDeUsuarios,
)
from gestao_usuarios.dominio.senha import (
    ALGORITMO,
    ITERACOES,
    gerar_hash,
    verificar,
)
from gestao_usuarios.dominio.usuario import Perfil


def test_hash_tem_formato_esperado():
    partes = gerar_hash(
        "Senha123!"
    ).split("$")

    assert partes[0] == ALGORITMO
    assert int(partes[1]) == ITERACOES
    assert len(
        bytes.fromhex(partes[2])
    ) == 16  # salt
    assert len(
        bytes.fromhex(partes[3])
    ) == 32  # sha256


def test_verificar_aceita_senha_correta():
    assert verificar(
        "Senha123!",
        gerar_hash("Senha123!"),
    ) is True


def test_verificar_rejeita_senha_incorreta():
    assert verificar(
        "senha_errada",
        gerar_hash("Senha123!"),
    ) is False


def test_hashes_da_mesma_senha_sao_diferentes():
    """O salt aleatório garante hashes distintos para a mesma senha."""
    assert (
        gerar_hash("Senha123!")
        != gerar_hash("Senha123!")
    )


def test_verificar_rejeita_hash_em_formato_invalido():
    assert verificar(
        "Senha123!",
        "texto-que-nao-e-hash",
    ) is False

    assert verificar(
        "Senha123!",
        "",
    ) is False


def test_usuario_persistido_nao_guarda_senha_em_texto_puro():
    """NF007: o repositório recebe apenas o hash, nunca a senha original."""
    gerenciador = GerenciadorDeUsuarios(
        RepositorioUsuarioEmMemoria()
    )

    usuario = gerenciador.adicionar_usuario(
        nome="Ana Souza",
        cpf="12345678901",
        email="ana@ubs.gov.br",
        telefone="84999990000",
        login="ana",
        senha="Senha123!!",
        perfil=Perfil.MEDICO,
    )

    assert (
        "Senha123!!"
        not in usuario.senha_hash
    )

    assert usuario.senha_hash.startswith(
        f"{ALGORITMO}$"
    )
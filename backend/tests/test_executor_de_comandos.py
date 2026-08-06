"""Testes unitários para o ExecutorDeComandos (Invoker do padrão Command)."""

import pytest

from gestao_usuarios.adaptadores.repositorio_unidade_em_memoria import (
    RepositorioUnidadeEmMemoria,
)
from gestao_usuarios.adaptadores.repositorio_usuario_em_memoria import (
    RepositorioUsuarioEmMemoria,
)
from gestao_usuarios.aplicacao.comandos import (
    Comando,
    ComandoAdicionarUnidade,
    ComandoAdicionarUsuario,
    ComandoContarTotalEntidades,
    ExecutorDeComandos,
)
from gestao_usuarios.aplicacao.gerenciador_de_unidades import GerenciadorDeUnidades
from gestao_usuarios.aplicacao.gerenciador_de_usuarios import GerenciadorDeUsuarios
from gestao_usuarios.dominio.usuario import Perfil


class ComandoCustomizado(Comando):
    """Comando simples para teste de execução e resultado."""

    def __init__(self, valor: int) -> None:
        self.valor = valor

    def executar(self) -> int:
        return self.valor * 2


class ComandoComFalha(Comando):
    """Comando que gera erro ao executar."""

    def executar(self) -> None:
        raise ValueError("Falha intencional de execução")


def test_executor_executa_comando_e_retorna_resultado():
    executor = ExecutorDeComandos()
    comando = ComandoCustomizado(21)

    resultado = executor.executar(comando)

    assert resultado == 42
    assert executor.historico == [comando]
    assert executor.ultimo_comando is comando


def test_executor_mantem_historico_ordenado():
    executor = ExecutorDeComandos()
    cmd1 = ComandoCustomizado(1)
    cmd2 = ComandoCustomizado(2)
    cmd3 = ComandoCustomizado(3)

    executor.executar(cmd1)
    executor.executar(cmd2)
    executor.executar(cmd3)

    assert executor.historico == [cmd1, cmd2, cmd3]
    assert executor.ultimo_comando is cmd3


def test_executor_limpar_historico():
    executor = ExecutorDeComandos()
    executor.executar(ComandoCustomizado(10))

    assert len(executor.historico) == 1

    executor.limpar_historico()

    assert executor.historico == []
    assert executor.ultimo_comando is None


def test_executor_rejeita_objeto_que_nao_e_comando():
    executor = ExecutorDeComandos()

    with pytest.raises(TypeError) as exc_info:
        executor.executar("nao_sou_um_comando")  # type: ignore

    assert "não é uma instância de Comando" in str(exc_info.value)


def test_executor_nao_registra_no_historico_se_comando_falhar():
    executor = ExecutorDeComandos()
    cmd_falho = ComandoComFalha()

    with pytest.raises(ValueError, match="Falha intencional"):
        executor.executar(cmd_falho)

    assert executor.historico == []
    assert executor.ultimo_comando is None


def test_executor_com_comando_contar_total_entidades():
    repo_usuarios = RepositorioUsuarioEmMemoria()
    repo_unidades = RepositorioUnidadeEmMemoria()
    gerenciador_usuarios = GerenciadorDeUsuarios(repo_usuarios)
    gerenciador_unidades = GerenciadorDeUnidades(repo_unidades)

    executor = ExecutorDeComandos()

    cmd_contar = ComandoContarTotalEntidades(
        gerenciador_usuarios,
        gerenciador_unidades,
    )
    assert executor.executar(cmd_contar) == 0

    executor.executar(
        ComandoAdicionarUsuario(
            gerenciador_usuarios,
            nome="Carlos",
            cpf="11122233344",
            email="carlos@ubs.gov.br",
            telefone="84911112222",
            login="carlos",
            senha="SenhaForte1!",
            perfil=Perfil.GESTOR,
        )
    )
    executor.executar(
        ComandoAdicionarUnidade(
            gerenciador_unidades,
            nome="UBS 1",
            cnpj="11111111000111",
            endereco="Rua 1",
            telefone="84911111111",
        )
    )

    assert executor.executar(cmd_contar) == 2

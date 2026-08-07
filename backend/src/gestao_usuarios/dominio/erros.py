"""Erros do domínio de gerenciamento de usuários.

Hierarquia de exceções aplicando os princípios de boas práticas:
- Taborda: seja específico, o nome da exceção revela o problema,
  agrupe exceções de uma mesma camada sob uma base comum.
- PLoP 2018 (Coelho et al.): evite Catch Generic, preserve o rastro
  (cause chain) e não faça Destructive Wrapping.
"""


class ErroDeDominio(Exception):
    """Raiz de todos os erros de domínio.

    Permite que o chamador capture qualquer erro de negócio com um único
    tipo sem precisar conhecer todas as subclasses (Taborda: camadas e
    exceções). Nunca lance esta classe diretamente — use uma subclasse
    específica.
    """


class ErroDeValidacao(ErroDeDominio):
    """Dados de entrada inválidos (campo obrigatório vazio, formato errado etc.).

    Lançada cedo, assim que a pré-condição falha (Taborda: seja específico
    e lance o quanto antes).
    """


class CpfDuplicado(ErroDeDominio):
    """Já existe um usuário cadastrado com o mesmo CPF."""


class LoginDuplicado(ErroDeDominio):
    """Já existe um usuário cadastrado com o mesmo login."""


# ---------------------------------------------------------------------------
# Exceções de autenticação — subárvore ErroDeAutenticacao
#
# Seguindo Taborda ("Camadas e exceções"): todas as falhas de login ficam
# sob ErroDeAutenticacao, que é a exceção de fronteira desta camada.
# O chamador pode capturar ErroDeAutenticacao para tratar qualquer falha
# de login, ou capturar uma subclasse específica quando precisar de
# tratamento diferenciado.
# ---------------------------------------------------------------------------


class ErroDeAutenticacao(ErroDeDominio):
    """Base de todos os erros de autenticação/login.

    Não lançar diretamente — use CredenciaisInvalidas ou UsuarioInativo.
    """


class CredenciaisInvalidas(ErroDeAutenticacao):
    """Login ou senha incorretos.

    Intencionalmente genérica entre "login não encontrado" e "senha errada"
    para não vazar ao atacante qual parte está errada (segurança por
    obscuridade mínima). O nome revela o que deu errado sem revelar o porquê
    técnico (Taborda: o quê, o onde, o porquê — mas apenas o necessário).
    """


class UsuarioInativo(ErroDeAutenticacao):
    """Usuário existe e a senha está correta, mas a conta está desativada.

    Exceção separada de CredenciaisInvalidas porque a ação corretiva é
    diferente: o administrador precisa reativar a conta, não redefinir a
    senha (Taborda: seja específico o suficiente para guiar o tratamento).
    """


class ErroDePersistencia(ErroDeDominio):
    """Falha ao salvar ou recuperar dados do banco.

    Pode ser causada por falhas de infraestrutura (banco indisponível) ou
    por violação de regras de negócio (CPF duplicado). O nome genérico
    reflete a natureza técnica da falha, sem vazar detalhes de implementação
    (Taborda: o nome da exceção deve revelar o problema, mas não detalhes
    técnicos desnecessários).
    """


class ErroDeAcessoAoArquivo(ErroDePersistencia):
    """Falha ao acessar o arquivo de dados.

    Pode ser causada por falta de permissão, arquivo corrompido ou
    indisponibilidade do sistema de arquivos. O nome genérico reflete a
    natureza técnica da falha, sem vazar detalhes de implementação (Taborda:
    o nome da exceção deve revelar o problema, mas não detalhes técnicos
    desnecessários).
    """


class ErroDeAcessoAoBanco(ErroDePersistencia):
    """Falha ao acessar o banco de dados.

    Pode ser causada por falhas de rede, autenticação ou configuração do
    banco. O nome genérico reflete a natureza técnica da falha, sem vazar
    detalhes de implementação (Taborda: o nome da exceção deve revelar o
    problema, mas não detalhes técnicos desnecessários).
    """


# ---------------------------------------------------------------------------
# Exceções de Unidade Básica de Saúde
# ---------------------------------------------------------------------------


class CnpjDuplicado(ErroDeDominio):
    """Já existe uma unidade cadastrada com o mesmo CNPJ."""


class UnidadeNaoEncontrada(ErroDeDominio):
    """Unidade Básica de Saúde não encontrada com o identificador informado."""


class NenhumaAtualizacaoParaDesfazer(ErroDeDominio):
    """Não existe uma atualização de UBS disponível para ser desfeita."""


# ---------------------------------------------------------------------------
# Exceções de Autorização — subárvore AcessoNegado
#
# Lançadas pelo padrão Proxy quando o perfil do usuário autenticado não
# possui permissão para executar a operação solicitada (Sprint 6).
# ---------------------------------------------------------------------------


class AcessoNegado(ErroDeDominio):
    """Operação não permitida para o perfil do usuário autenticado.

    Lançada pelo Proxy quando o perfil não consta na lista de perfis
    autorizados para a operação. O nome revela claramente o problema
    (Taborda: seja específico) sem expor detalhes de implementação.
    """

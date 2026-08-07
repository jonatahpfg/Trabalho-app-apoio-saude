# Backend — Gerenciamento de Usuários

Backend em Python do App Experimental de Triagem em Saúde, organizado em
[arquitetura hexagonal](../docs/adr/ADR-001-arquitetura-hexagonal.md)
([stack: ADR-002](../docs/adr/ADR-002-stack-tecnologica.md)).

## Estrutura

```
src/gestao_usuarios/
├── dominio/        entidades e regras de negócio
│   ├── Usuario (CRUD completo + exclusão lógica)
│   ├── UnidadeBasicaSaude
│   ├── RegistroDeAcesso
│   ├── Perfil
│   └── erros de domínio
├── portas/         contratos da aplicação
│   ├── RepositorioUsuario (inclui buscar_por_id)
│   ├── RepositorioUnidadeBasicaSaude
│   ├── RepositorioRegistroDeAcesso
│   └── FabricaRepositorio
├── aplicacao/      casos de uso e regras de aplicação
│   ├── GerenciadorDeUsuarios
│   ├── GerenciadorDeUnidades
│   ├── FacadeSingletonController
│   └── relatórios de acesso
└── adaptadores/    implementações de infraestrutura
    ├── repositórios em memória
    ├── repositório SQLite de usuários
    ├── fábricas concretas de repositórios
    └── adapter de arquivo de log
```

A dependência aponta sempre para dentro: adaptadores dependem do domínio, nunca o contrário.

## Gerenciamento de usuários

O CRUD de `Usuario` é exposto por `GerenciadorDeUsuarios` e, com o padrão
Command, também por `FacadeSingletonController`:

| Operação | Caso de uso | Erros possíveis |
| -------- | ----------- | --------------- |
| Cadastrar | `adicionar_usuario(...)` | `ErroDeValidacao`, `CpfDuplicado`, `LoginDuplicado` |
| Listar | `listar_usuarios(apenas_ativos=False)` | — |
| Buscar por id | `buscar_usuario_por_id(id)` | `UsuarioNaoEncontrado` |
| Buscar por login | `buscar_usuario_por_login(login)` | `ErroDeValidacao`, `UsuarioNaoEncontrado` |
| Atualizar | `atualizar_usuario(...)` | `UsuarioNaoEncontrado`, `ErroDeValidacao`, `CpfDuplicado`, `LoginDuplicado` |
| Desativar | `desativar_usuario(id)` | `UsuarioNaoEncontrado` |
| Reativar | `reativar_usuario(id)` | `UsuarioNaoEncontrado` |
| Autenticar | `autenticar(login, senha)` | `ErroDeValidacao`, `CredenciaisInvalidas`, `UsuarioInativo` |

A remoção é sempre **lógica**: o cadastro é preservado e apenas o acesso é
bloqueado ([ADR-004](../docs/adr/ADR-004-exclusao-logica-de-usuarios.md)).
A senha só é alterada quando informada na atualização, e nunca é armazenada
em texto puro.

### Regras de validação

**Login** — obrigatório, no máximo 12 caracteres e **sem números**.

**Senha** — política do AWS IAM: de 8 a 128 caracteres, ao menos três dos
quatro grupos (maiúsculas, minúsculas, números e caracteres especiais) e
diferente do nome e do e-mail do usuário.

Toda violação é sinalizada por `ErroDeValidacao`, subclasse de `ErroDeDominio`.

## Persistência

O mecanismo é escolhido na inicialização pela variável de ambiente
`STORAGE_TYPE`, resolvida pelo Abstract Factory:

```bash
python -m gestao_usuarios              # memória (RAM) — padrão
STORAGE_TYPE=bd python -m gestao_usuarios   # SQLite
```

As falhas de infraestrutura do SQLite são traduzidas para `ErroDeAcessoAoBanco`
e as do arquivo de log para `ErroDeAcessoAoArquivo`, ambas subclasses de
`ErroDePersistencia`, preservando a exceção original na cadeia de causa.

## Ambiente

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Testes

```bash
pytest                                   # roda os testes
pytest --cov=gestao_usuarios --cov-report=term-missing   # com cobertura
```

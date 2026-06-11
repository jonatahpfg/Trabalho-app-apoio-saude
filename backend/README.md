# Backend — Gerenciamento de Usuários

Backend em Python do App Experimental de Triagem em Saúde, organizado em
[arquitetura hexagonal](../docs/adr/ADR-001-arquitetura-hexagonal.md)
([stack: ADR-002](../docs/adr/ADR-002-stack-tecnologica.md)).

## Estrutura

```
src/gestao_usuarios/
├── dominio/        entidades e regras (Usuario, Perfil, erros)
├── portas/         contratos (RepositorioUsuario)
├── aplicacao/      casos de uso (GerenciadorDeUsuarios)
└── adaptadores/    implementações das portas (repositório em memória)
```

A dependência aponta sempre para dentro: adaptadores dependem do domínio, nunca o contrário.

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

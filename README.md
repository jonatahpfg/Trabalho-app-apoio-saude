# App de Apoio à Triagem Médica

Aplicativo móvel de apoio à triagem clínica na atenção primária, desenvolvido como projeto
acadêmico da disciplina de Engenharia de Software. O sistema centraliza o cadastro de unidades
de saúde, gestores, médicos e pacientes, e oferece módulos de triagem assistida por IA —
sempre com validação final do profissional de saúde.

> O sistema não substitui avaliação médica, diagnóstico ou protocolos institucionais
> de atendimento.

## Estrutura

```
backend/   Serviço em Python 3.12 — arquitetura hexagonal (domínio, portas, aplicação, adaptadores)
mobile/    Aplicativo React Native (sprints futuras)
docs/      Documentação: requisitos, diagramas e ADRs
```

## Começando

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                        # testes
cd src && python -m gestao_usuarios   # demo (STORAGE_TYPE=bd para SQLite)
```

Detalhes em [`backend/README.md`](backend/README.md).

## Documentação

- [Documento de Requisitos](https://docs.google.com/document/d/1aYtdkwlBACGB7D5SwdqcBMFRpFpb9utuG5owqmn-l4s/edit)
- [Diagramas do sistema](docs/diagramas-sistema.md)
- [ADR-001 — Arquitetura Hexagonal](docs/adr/ADR-001-arquitetura-hexagonal.md)
- [ADR-002 — Stack tecnológica](docs/adr/ADR-002-stack-tecnologica.md)
- [Guia de contribuição](CONTRIBUTING.md)

## Equipe

Jonata Henrique Paiva · Esdras Lucas · Flávio Mesquita · Gabriel Silva · Mateus Fonseca

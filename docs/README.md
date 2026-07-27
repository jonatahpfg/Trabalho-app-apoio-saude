# Documentação do Projeto

Esta pasta reúne os documentos, diagramas e registros de decisões
arquiteturais do App Experimental de Apoio à Triagem Médica.

## Documentação atual

- [Diagramas e visão atual do sistema](diagramas-sistema.md)
- [Documento de Requisitos](documento-de-requisi# Documentação do Projeto

Esta pasta reúne os documentos, diagramas e registros de decisões
arquiteturais do App Experimental de Apoio à Triagem Médica.

## Documentação atual

- [Diagramas e visão atual do sistema](diagramas-sistema.md)
- [Diagrama de classes atual](diagrama-classes.puml)
- [Documento de Requisitos](documento-de-requisitos.docx)
- [Registros de Decisões Arquiteturais](adr/README.md)

## Diagramas

### Estado atual

- `diagrama-classes.puml` — diagrama oficial correspondente ao estado
  atual do backend.

### Evolução do projeto

- `diagrama-classes-v2.puml` — evolução referente à Sprint 3;
- `diagrama-classes-final-sprint4.puml` — diagrama consolidado da
  Sprint 4, revisado após o feedback da avaliação.

Os diagramas são mantidos no repositório para demonstrar a evolução
da arquitetura e da implementação ao longo das Sprints.

## Complementos

- [Casos de uso e análise — Sprint 4](complemento-sprint4-casos-uso-e-analise.md)

O complemento da Sprint 4 representa o contexto daquela entrega.
A documentação correspondente ao estado atual do sistema está
concentrada em `diagramas-sistema.md` e `diagrama-classes.puml`.

## Alterações após a avaliação

Após o feedback da avaliação, o contexto de gerenciamento de usuários
recebeu duas alterações principais.

### Autenticação por login

A autenticação passou a utilizar **login e senha**, em substituição ao
uso do e-mail como identificador de autenticação.

O login:

- é obrigatório;
- deve possuir no máximo 12 caracteres;
- deve ser único no sistema.

O e-mail continua sendo mantido como dado cadastral do usuário.

### Separação das validações

As validações anteriormente concentradas na entidade `Usuario` foram
separadas em componentes específicos do domínio:

- `ValidadorLogin`;
- `ValidadorEmail`;
- `ValidadorSenha`;
- `ValidadorPerfil`;
- `ValidadorTextoObrigatorio`.

Essa organização reduz o acoplamento da entidade `Usuario` e facilita
a manutenção e evolução das regras de negócio.

## Decisões arquiteturais

As principais decisões arquiteturais estão registradas no diretório
[`adr/`](adr/README.md), incluindo:

- adoção de Arquitetura Hexagonal;
- definição da stack tecnológica;
- adoção do login como identificador de autenticação.tos.docx)
- [ADRs](adr/README.md)

## Diagramas

### Estado atual

- `diagrama-classes-atual.puml` — diagrama correspondente ao estado
  atual do backend.

### Histórico

- `diagrama-classes.puml` — diagrama produzido em etapa anterior;
- `diagrama-classes-v2.puml` — evolução referente à Sprint 3;
- `diagrama-classes-final-sprint4.puml` — versão produzida ao final
  da Sprint 4.

Os diagramas históricos são preservados para demonstrar a evolução
do projeto.

## Complementos históricos

- [Casos de uso e análise — Sprint 4](complemento-sprint4-casos-uso-e-analise.md)

## Alterações após a avaliação

Após o feedback da avaliação, o contexto de gerenciamento de usuários
recebeu duas alterações principais:

1. autenticação passou de e-mail e senha para **login e senha**;
2. as validações da entidade `Usuario` foram separadas em componentes
   específicos do domínio.

### Regras atuais do login

- obrigatório;
- máximo de 12 caracteres;
- único no sistema.

O e-mail continua sendo mantido como dado cadastral.
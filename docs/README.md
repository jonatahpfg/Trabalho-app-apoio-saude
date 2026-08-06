# Documentação do Projeto

Esta pasta reúne os documentos, diagramas e registros de decisões
arquiteturais do App Experimental de Apoio à Triagem Médica.

## Documentação atual

- [Diagramas e visão atual do sistema](diagramas-sistema.md)
- [Diagrama de classes — Sprint 5 (Command)](diagrama-classes-sprint5-command.puml)
- [Documento de Requisitos](documento-de-requisitos.docx)
- [Registros de Decisões Arquiteturais](adr/README.md)

## Diagramas

### Estado atual

- `diagrama-classes-sprint5-command.puml` — diagrama correspondente ao estado
  atual do backend com a integração do **Padrão Command**.
- `diagrama-classes.puml` — diagrama oficial inicial do backend.

### Evolução do projeto

- `diagrama-classes-v2.puml` — evolução referente à Sprint 3 (Facade + Singleton);
- `diagrama-classes-final-sprint4.puml` — diagrama consolidado da
  Sprint 4, revisado após o feedback da avaliação;
- `diagrama-classes-sprint5-command.puml` — diagrama com o padrão Command da Sprint 5.

Os diagramas são mantidos no repositório para demonstrar a evolução
da arquitetura e da implementação ao longo das Sprints.

## Complementos

- [Casos de uso e análise — Sprint 4](complemento-sprint4-casos-uso-e-analise.md)

O complemento da Sprint 4 representa o contexto daquela entrega.
A documentação correspondente ao estado atual do sistema está
concentrada em `diagramas-sistema.md` e `diagrama-classes-sprint5-command.puml`.

## Padrão Command (Sprint 5)

A Sprint 5 refatora a camada de aplicação para adotar o padrão **Command (GoF)**:
- Criação da interface abstrata `Comando` com o método `executar()`;
- Criação do `ExecutorDeComandos` que atua como invoker e gerencia o histórico de execução;
- Encapsulamento das operações de Usuário e UBS em comandos concretos (`ComandoAdicionarUsuario`, `ComandoListarUsuarios`, `ComandoAutenticarUsuario`, `ComandoAdicionarUnidade`, `ComandoListarUnidades`, `ComandoBuscarUnidadePorId`, `ComandoAtualizarUnidade`, `ComandoRemoverUnidade`, `ComandoContarTotalEntidades`);
- A `FacadeSingletonController` (com alias `FacadeDoSistema`) passa a delegar todas as operações de negócio por meio da instanciação e execução desses comandos.

## Decisões arquiteturais

As principais decisões arquiteturais estão registradas no diretório
[`adr/`](adr/README.md), incluindo:

- adoção de Arquitetura Hexagonal;
- definição da stack tecnológica;
- adoção do login como identificador de autenticação.
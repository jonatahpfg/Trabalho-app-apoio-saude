# Documentação do Projeto

Esta pasta reúne os documentos, diagramas e registros de decisões
arquiteturais do App Experimental de Apoio à Triagem Médica.

## Documentação atual

- [Diagramas e visão atual do sistema](diagramas-sistema.md)
- [Diagrama de classes — Sprint 6 (Memento)](diagrama-classes-sprint6-memento.puml)
- [Diagrama de classes — Sprint 5 (Command)](diagrama-classes-sprint5-command.puml)
- [Documento de Requisitos](documento-de-requisitos.docx)
- [Registros de Decisões Arquiteturais](adr/README.md)

## Diagramas

### Estado atual

- `diagrama-classes-sprint6-memento.puml` — diagrama correspondente ao estado
  atual do backend com a integração do **Padrão Memento**;
- `diagramas-sistema.md` — visão consolidada da arquitetura e dos padrões
  implementados no sistema;
- `diagrama-classes.puml` — diagrama oficial inicial do backend.

### Evolução do projeto

- `diagrama-classes-v2.puml` — evolução referente à Sprint 3
  (Facade + Singleton);
- `diagrama-classes-final-sprint4.puml` — diagrama consolidado da
  Sprint 4, revisado após o feedback da avaliação;
- `diagrama-classes-sprint5-command.puml` — diagrama com o padrão
  Command da Sprint 5;
- `diagrama-classes-sprint6-memento.puml` — diagrama com o padrão
  Memento aplicado ao desfazer da última atualização de uma UBS.

Os diagramas são mantidos no repositório para demonstrar a evolução
da arquitetura e da implementação ao longo das Sprints.

## Complementos

- [Casos de uso e análise — Sprint 4](complemento-sprint4-casos-uso-e-analise.md)

O complemento da Sprint 4 representa o contexto daquela entrega.
A documentação correspondente ao estado atual do sistema está
concentrada em `diagramas-sistema.md` e
`diagrama-classes-sprint6-memento.puml`.

## Padrão Command (Sprint 5)

A Sprint 5 refatora a camada de aplicação para adotar o padrão
**Command (GoF)**:

- Criação da interface abstrata `Comando` com o método `executar()`;
- Criação do `ExecutorDeComandos`, que atua como invoker e gerencia
  o histórico de execução;
- Encapsulamento das operações de Usuário e UBS em comandos concretos,
  como `ComandoAdicionarUsuario`, `ComandoListarUsuarios`,
  `ComandoAutenticarUsuario`, `ComandoAdicionarUnidade`,
  `ComandoListarUnidades`, `ComandoBuscarUnidadePorId`,
  `ComandoAtualizarUnidade`, `ComandoRemoverUnidade` e
  `ComandoContarTotalEntidades`;
- A `FacadeSingletonController`, também disponível pelo alias
  `FacadeDoSistema`, passa a delegar as operações de negócio por meio
  da criação e execução desses comandos.

## Padrão Memento (Sprint 6)

A Sprint 6 integra o padrão **Memento (GoF)** ao gerenciamento de
Unidades Básicas de Saúde, permitindo desfazer a última atualização
bem-sucedida de uma UBS.

### Participantes do padrão

- `UnidadeBasicaSaude` atua como **Originator**:
  - cria um Memento por meio de `criar_memento()`;
  - recupera um estado anterior por meio de `restaurar()`;

- `MementoUnidadeBasicaSaude` atua como **Memento**:
  - representa uma cópia imutável do estado de uma UBS;
  - armazena `id`, `nome`, `cnpj`, `endereco`, `telefone` e `ativa`;

- `HistoricoDeUnidade` atua como **Caretaker**:
  - mantém apenas o último Memento disponível;
  - permite salvar, recuperar e descartar o último estado;

- `GerenciadorDeUnidades` coordena o processo:
  - cria o Memento antes da alteração;
  - registra o Memento somente após uma atualização bem-sucedida;
  - restaura e persiste o estado anterior quando o desfazer é solicitado;

- `ComandoDesfazerAtualizacaoDeUnidade` encapsula a operação de
  desfazer utilizando o padrão Command já existente;

- `FacadeSingletonController` disponibiliza a operação
  `desfazer_ultima_atualizacao_de_unidade()` para os clientes
  da aplicação.

### Regra de desfazer

O sistema mantém somente o estado anterior da **última atualização
bem-sucedida** de uma Unidade Básica de Saúde.

Assim:

1. uma atualização bem-sucedida substitui o Memento anterior;
2. uma atualização inválida não cria nem substitui o estado salvo;
3. ao desfazer, o estado anterior é restaurado e persistido;
4. depois de uma restauração bem-sucedida, o Memento é descartado;
5. uma segunda tentativa de desfazer, sem uma nova atualização,
   resulta em `NenhumaAtualizacaoParaDesfazer`.

Essa estratégia atende ao requisito de desfazer somente a alteração
mais recente, sem manter uma pilha completa de versões anteriores.

## Decisões arquiteturais

As principais decisões arquiteturais estão registradas no diretório
[`adr/`](adr/README.md), incluindo:

- adoção de Arquitetura Hexagonal;
- definição da stack tecnológica;
- adoção do login como identificador de autenticação.
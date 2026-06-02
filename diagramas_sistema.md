# Diagramas do Sistema: Mobile Diagn (Gerenciamento de Usuários)

Abaixo estão os diagramas atualizados, focados na parte de **gerenciamento de usuários** e unidades de saúde. Foram adicionados mais detalhes às entidades (atributos) e incluída a funcionalidade do Médico cadastrar pacientes.

## 1. Diagrama de Casos de Uso

Este diagrama ilustra as interações entre os atores responsáveis pela administração do sistema e pelo atendimento (Admin, Gestor da Unidade de Saúde e Médico).

```mermaid
flowchart LR
    Admin([Admin])
    Gestor([Gestor da Unidade de Saúde])
    Medico([Médico])

    subgraph Gerenciamento de Usuários
        UC1(Cadastrar Unidade Básica de Saúde)
        UC2(Gerenciar Solução)
        UC3(Cadastrar Médico)
        UC4(Gerenciar Unidade de Saúde)
        UC5(Consultar Próprio Cadastro)
        UC6(Cadastrar Paciente)
    end

    Admin --> UC1
    Admin --> UC2

    Gestor --> UC3
    Gestor --> UC4

    Medico --> UC5
    Medico --> UC6
```


> [!NOTE]
> - **Admin:** Atua no nível mais alto, gerenciando o sistema e sendo responsável por cadastrar as Unidades Básicas de Saúde (UBS).
> - **Gestor da Unidade de Saúde:** Atua localmente na sua respectiva UBS, com permissão para gerenciar as rotinas da unidade e cadastrar os Médicos associados a ela.
> - **Médico:** O profissional de saúde que pode consultar seus próprios dados e é o responsável pelo **cadastro dos Pacientes** no sistema.

---

## 2. Diagrama de Classe de Análise (Fronteira, Controle, Entidade)

O diagrama abaixo utiliza o padrão **ECB (Entity, Control, Boundary)**, com entidades enriquecidas de atributos e a adição do fluxo de gestão de pacientes.

```mermaid
classDiagram
    %% Fronteiras (Boundary) - Interfaces com as quais os atores interagem
    class TelaAdmin {
        <<Boundary>>
        +exibirPainelAdmin()
        +solicitarDadosUBS()
    }
    
    class TelaGestor {
        <<Boundary>>
        +exibirPainelGestaoUBS()
        +solicitarDadosMedico()
    }
    
    class TelaMedico {
        <<Boundary>>
        +exibirPerfil()
        +solicitarDadosPaciente()
    }

    %% Controles (Control) - Coordenam fluxos e regras de negócio
    class ControleSistemaGlobal {
        <<Control>>
        +cadastrarUBS(dados)
        +gerenciarSolucao()
    }
    
    class ControleGestaoUnidade {
        <<Control>>
        +cadastrarMedico(dados, idUBS)
        +atualizarDadosUnidade(idUBS)
    }
    
    class ControleMedico {
        <<Control>>
        +consultarPerfil(idMedico)
        +cadastrarPaciente(dadosPaciente, idMedico)
    }

    %% Entidades (Entity) - Representam os dados de forma enriquecida
    class UnidadeBasicaSaude {
        <<Entity>>
        +id: int
        +nome: string
        +cnpj: string
        +endereco: string
        +telefone: string
        +horarioFuncionamento: string
        +statusAtiva: boolean
    }
    
    class Gestor {
        <<Entity>>
        +id: int
        +cpf: string
        +nome: string
        +email: string
        +telefone: string
        +dataContratacao: Date
    }
    
    class Medico {
        <<Entity>>
        +id: int
        +crm: string
        +nome: string
        +especialidade: string
        +telefone: string
        +email: string
        +ativo: boolean
    }
    
    class Paciente {
        <<Entity>>
        +id: int
        +cpf: string
        +nome: string
        +dataNascimento: Date
        +sexo: string
        +telefone: string
        +endereco: string
        +historicoFamiliar: string
    }

    %% Relações e Associações
    TelaAdmin --> ControleSistemaGlobal : "solicita"
    TelaGestor --> ControleGestaoUnidade : "solicita"
    TelaMedico --> ControleMedico : "solicita"
    
    ControleSistemaGlobal --> UnidadeBasicaSaude : "instancia / persiste"
    ControleSistemaGlobal --> Gestor : "associa Gestor à UBS"
    
    ControleGestaoUnidade --> Medico : "instancia / persiste"
    ControleGestaoUnidade --> UnidadeBasicaSaude : "consulta / gerencia"
    
    ControleMedico --> Medico : "consulta"
    ControleMedico --> Paciente : "instancia / persiste"
    ControleMedico --> Paciente : "vincula Paciente ao Médico/UBS"
```



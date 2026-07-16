# Complemento de Documentação — Casos de Uso e Diagrama de Classe até Sprint 4

**Projeto:** App Experimental de Apoio à Triagem Médica  
**Contexto documentado:** Gerenciamento de usuários, unidades básicas de saúde e estatísticas de acesso.

Este documento complementa `docs/diagramas-sistema.md` com:

1. descrição dos 3 casos de uso mais relevantes;
2. diagrama de casos de uso contemplando os requisitos funcionais tratados até a Sprint 4;
3. diagrama de classe de análise considerando CRUD de duas entidades, Repository, Adapter e Template Method.

---

## 1. Descrição dos 3 casos de uso mais relevantes

### UC01 — Autenticar por perfil

| Campo | Descrição |
| ----- | --------- |
| Atores principais | Administrador, Gestor da Unidade, Médico |
| Objetivo | Permitir que um usuário acesse o sistema de acordo com seu perfil. |
| Pré-condições | O usuário deve estar cadastrado e ativo. |
| Pós-condições | O acesso é autorizado ou recusado; a tentativa de autenticação é registrada para estatísticas. |
| Requisitos relacionados | RF03 — Autenticar por perfil; NF008 — Controle de acesso por perfil. |

**Fluxo principal**

1. O usuário informa e-mail e senha.
2. O sistema valida se os campos obrigatórios foram preenchidos.
3. O sistema consulta o usuário pelo e-mail.
4. O sistema verifica a senha usando o hash armazenado.
5. O sistema verifica se o usuário está ativo.
6. O sistema registra a tentativa de acesso como `RegistroDeAcesso`.
7. O sistema libera o acesso conforme o perfil do usuário.

**Fluxos alternativos**

- Se o e-mail não existir ou a senha estiver incorreta, o sistema lança erro de credenciais inválidas.
- Se o usuário estiver inativo, o sistema recusa o acesso.
- Se e-mail ou senha estiverem vazios, o sistema retorna erro de validação.

---

### UC02 — Gerenciar usuários

| Campo | Descrição |
| ----- | --------- |
| Atores principais | Administrador, Gestor da Unidade |
| Objetivo | Cadastrar e consultar usuários que operam o sistema. |
| Pré-condições | O ator deve estar autenticado e possuir perfil autorizado. |
| Pós-condições | O usuário é cadastrado, listado ou validado conforme as regras de domínio. |
| Requisitos relacionados | RF02 — Gerenciar gestores e médicos; NF008 — Controle de acesso por perfil. |

**Fluxo principal**

1. O ator solicita o cadastro de um novo usuário.
2. O sistema recebe nome, CPF, e-mail, telefone, senha e perfil.
3. O sistema valida os dados obrigatórios e a força da senha.
4. O sistema verifica se já existe usuário com o mesmo CPF.
5. O sistema cria a entidade `Usuario`.
6. O sistema persiste o usuário por meio da porta `RepositorioUsuario`.
7. O sistema permite listar os usuários cadastrados.

**Fluxos alternativos**

- Se o CPF já estiver cadastrado, o sistema lança `CpfDuplicado`.
- Se os dados forem inválidos, o sistema lança `ErroDeValidacao`.
- Se houver falha de persistência, o erro é tratado na camada de infraestrutura.

---

### UC03 — Gerenciar unidades básicas de saúde

| Campo | Descrição |
| ----- | --------- |
| Atores principais | Administrador, Gestor da Unidade |
| Objetivo | Realizar o CRUD de Unidades Básicas de Saúde. |
| Pré-condições | O ator deve estar autenticado e possuir permissão para gerenciar unidades. |
| Pós-condições | A unidade é cadastrada, consultada, atualizada ou removida logicamente. |
| Requisitos relacionados | Sprint 3 — CRUD de nova entidade relacionada ao domínio do projeto. |

**Fluxo principal**

1. O ator solicita o cadastro de uma Unidade Básica de Saúde.
2. O sistema recebe nome, CNPJ, endereço e telefone.
3. O sistema valida os campos obrigatórios e o formato do CNPJ.
4. O sistema verifica se já existe uma unidade com o mesmo CNPJ.
5. O sistema cria a entidade `UnidadeBasicaSaude`.
6. O sistema persiste a unidade por meio da porta `RepositorioUnidadeBasicaSaude`.
7. O sistema permite listar, buscar, atualizar e remover logicamente a unidade.

**Fluxos alternativos**

- Se o CNPJ já estiver cadastrado, o sistema lança `CnpjDuplicado`.
- Se a unidade não existir, o sistema lança `UnidadeNaoEncontrada`.
- Na remoção, a unidade não é apagada fisicamente; ela é marcada como inativa.

---

## 2. Diagrama de casos de uso

O diagrama abaixo contempla os principais requisitos funcionais tratados até a Sprint 4: autenticação por perfil, gerenciamento de usuários, gerenciamento de unidades, registro de acessos e geração de relatórios de estatísticas.

```mermaid
flowchart LR
    Admin([Administrador])
    Gestor([Gestor da Unidade])
    Medico([Médico])

    subgraph Sistema[App de Apoio à Triagem Médica]
        UC_AUTH(("Autenticar por Perfil"))
        UC_GER_USU["Gerenciar Usuários"]
        UC_ADD_USU["Cadastrar Usuário"]
        UC_LIST_USU["Listar Usuários"]
        UC_TOGGLE_USU["Ativar / Desativar Usuário"]
        UC_SELF["Consultar Próprio Cadastro"]

        UC_GER_UBS["Gerenciar Unidades Básicas de Saúde"]
        UC_ADD_UBS["Cadastrar UBS"]
        UC_LIST_UBS["Listar UBS"]
        UC_UPDATE_UBS["Atualizar UBS"]
        UC_REMOVE_UBS["Remover UBS"]

        UC_REG_ACESSO["Registrar Acesso"]
        UC_RELATORIO["Gerar Relatório de Estatísticas de Acesso"]
    end

    Admin --> UC_AUTH
    Gestor --> UC_AUTH
    Medico --> UC_AUTH

    Admin --> UC_GER_USU
    Admin --> UC_TOGGLE_USU
    Admin --> UC_GER_UBS
    Admin --> UC_RELATORIO

    Gestor --> UC_GER_USU
    Gestor --> UC_GER_UBS
    Gestor --> UC_RELATORIO

    Medico --> UC_SELF

    UC_GER_USU -.->|"include"| UC_AUTH
    UC_GER_UBS -.->|"include"| UC_AUTH
    UC_SELF -.->|"include"| UC_AUTH
    UC_RELATORIO -.->|"include"| UC_AUTH

    UC_GER_USU --> UC_ADD_USU
    UC_GER_USU --> UC_LIST_USU

    UC_GER_UBS --> UC_ADD_UBS
    UC_GER_UBS --> UC_LIST_UBS
    UC_GER_UBS --> UC_UPDATE_UBS
    UC_GER_UBS --> UC_REMOVE_UBS

    UC_AUTH -.->|"include"| UC_REG_ACESSO
    UC_RELATORIO -.->|"consulta"| UC_REG_ACESSO
```

---

## 3. Diagrama de classe de análise até a Sprint 4

Este diagrama considera a evolução do projeto até a Sprint 4:

- CRUD de `Usuario`;
- CRUD de `UnidadeBasicaSaude`;
- padrão **Repository** para separar negócio e persistência;
- padrão **Factory Method / Abstract Factory** para seleção de repositórios;
- padrão **Adapter** para adaptar arquivo de log à porta de registros de acesso;
- padrão **Template Method** para geração de relatórios;
- padrões **Facade** e **Singleton** na fachada principal.

```mermaid
classDiagram
    %% =======================
    %% Domínio / Entidades
    %% =======================

    class Usuario {
        <<Entity>>
        +id: int
        +nome: string
        +cpf: string
        +email: string
        +telefone: string
        +senha_hash: string
        +perfil: Perfil
        +ativo: boolean
        +criar(dados) Usuario
    }

    class Perfil {
        <<enumeration>>
        ADMINISTRADOR
        GESTOR
        MEDICO
    }

    class UnidadeBasicaSaude {
        <<Entity>>
        +id: int
        +nome: string
        +cnpj: string
        +endereco: string
        +telefone: string
        +ativa: boolean
        +criar(dados) UnidadeBasicaSaude
    }

    class RegistroDeAcesso {
        <<Entity>>
        +id: int
        +email: string
        +sucesso: boolean
        +data_hora: datetime
        +criar(dados) RegistroDeAcesso
    }

    Usuario --> Perfil : possui

    %% =======================
    %% Portas / Repository
    %% =======================

    class RepositorioUsuario {
        <<Repository>>
        <<interface>>
        +salvar(usuario) Usuario
        +buscar_todos() List~Usuario~
        +buscar_por_cpf(cpf) Usuario
        +buscar_por_email(email) Usuario
    }

    class RepositorioUnidadeBasicaSaude {
        <<Repository>>
        <<interface>>
        +salvar(unidade) UnidadeBasicaSaude
        +buscar_todas() List~UnidadeBasicaSaude~
        +buscar_por_id(id) UnidadeBasicaSaude
        +buscar_por_cnpj(cnpj) UnidadeBasicaSaude
    }

    class RepositorioRegistroDeAcesso {
        <<Repository>>
        <<interface>>
        +salvar(registro) RegistroDeAcesso
        +buscar_todos() List~RegistroDeAcesso~
    }

    %% =======================
    %% Aplicação / Business
    %% =======================

    class GerenciadorDeUsuarios {
        <<Control>>
        -repositorio: RepositorioUsuario
        -repositorio_acessos: RepositorioRegistroDeAcesso
        +adicionar_usuario(dados) Usuario
        +listar_usuarios() List~Usuario~
        +autenticar(email, senha) Usuario
    }

    class GerenciadorDeUnidades {
        <<Control>>
        -repositorio: RepositorioUnidadeBasicaSaude
        +adicionar_unidade(dados) UnidadeBasicaSaude
        +listar_unidades(apenas_ativas) List~UnidadeBasicaSaude~
        +buscar_unidade_por_id(id) UnidadeBasicaSaude
        +atualizar_unidade(dados) UnidadeBasicaSaude
        +remover_unidade(id) UnidadeBasicaSaude
    }

    class FacadeSingletonController {
        <<Facade>>
        <<Singleton>>
        -instancia_unica: FacadeSingletonController
        -gerenciador_usuarios: GerenciadorDeUsuarios
        -gerenciador_unidades: GerenciadorDeUnidades
        +instancia() FacadeSingletonController
        +adicionar_usuario(dados) Usuario
        +listar_usuarios() List~Usuario~
        +autenticar(email, senha) Usuario
        +adicionar_unidade(dados) UnidadeBasicaSaude
        +listar_unidades() List~UnidadeBasicaSaude~
        +atualizar_unidade(dados) UnidadeBasicaSaude
        +remover_unidade(id) UnidadeBasicaSaude
        +obter_quantidade_total_entidades_cadastradas() int
    }

    GerenciadorDeUsuarios ..> RepositorioUsuario : usa porta
    GerenciadorDeUsuarios ..> RepositorioRegistroDeAcesso : registra acessos
    GerenciadorDeUsuarios ..> Usuario : cria/autentica

    GerenciadorDeUnidades ..> RepositorioUnidadeBasicaSaude : usa porta
    GerenciadorDeUnidades ..> UnidadeBasicaSaude : CRUD

    FacadeSingletonController --> GerenciadorDeUsuarios : delega
    FacadeSingletonController --> GerenciadorDeUnidades : delega

    %% =======================
    %% Factory / Seleção de repositórios
    %% =======================

    class FabricaRepositorio {
        <<Abstract Factory>>
        <<interface>>
        +criar_repositorio_usuario() RepositorioUsuario
        +criar_repositorio_unidade_basica_saude() RepositorioUnidadeBasicaSaude
        +criar_repositorio_registro_de_acesso() RepositorioRegistroDeAcesso
    }

    class FabricaRepositorioEmMemoria {
        <<Concrete Factory>>
    }

    class FabricaRepositorioBancoDeDados {
        <<Concrete Factory>>
    }

    class SeletorFabrica {
        <<Factory Method>>
        +obter_fabrica_repositorio(tipo) FabricaRepositorio
    }

    FabricaRepositorio <|.. FabricaRepositorioEmMemoria
    FabricaRepositorio <|.. FabricaRepositorioBancoDeDados
    SeletorFabrica ..> FabricaRepositorio : seleciona

    %% =======================
    %% Infra / Adaptadores
    %% =======================

    class RepositorioUsuarioEmMemoria {
        <<Repository Adapter>>
    }

    class RepositorioUsuarioBancoDeDados {
        <<Repository Adapter>>
    }

    class RepositorioUnidadeEmMemoria {
        <<Repository Adapter>>
    }

    class RepositorioRegistroDeAcessoEmMemoria {
        <<Repository Adapter>>
    }

    RepositorioUsuario <|.. RepositorioUsuarioEmMemoria
    RepositorioUsuario <|.. RepositorioUsuarioBancoDeDados
    RepositorioUnidadeBasicaSaude <|.. RepositorioUnidadeEmMemoria
    RepositorioRegistroDeAcesso <|.. RepositorioRegistroDeAcessoEmMemoria

    RepositorioUsuarioEmMemoria ..> Usuario : persiste
    RepositorioUsuarioBancoDeDados ..> Usuario : persiste
    RepositorioUnidadeEmMemoria ..> UnidadeBasicaSaude : persiste
    RepositorioRegistroDeAcessoEmMemoria ..> RegistroDeAcesso : persiste

    %% =======================
    %% Adapter
    %% =======================

    class AdaptadorArquivoDeLog {
        <<Adapter>>
        +salvar(registro) RegistroDeAcesso
        +buscar_todos() List~RegistroDeAcesso~
    }

    class ArquivoDeLogSimples {
        <<Adaptee>>
        +anotar(linha)
        +ler_linhas() List~string~
    }

    RepositorioRegistroDeAcesso <|.. AdaptadorArquivoDeLog
    AdaptadorArquivoDeLog --> ArquivoDeLogSimples : adapta

    %% =======================
    %% Template Method
    %% =======================

    class RelatorioDeAcessos {
        <<Template Method>>
        <<abstract>>
        +gerar() string
        #calcular_estatisticas(registros) EstatisticasDeAcesso
        #cabecalho()* string
        #linha_por_email(estatistica)* string
        #rodape(estatisticas)* string
    }

    class RelatorioDeAcessosTexto
    class RelatorioDeAcessosCsv

    RelatorioDeAcessos ..> RepositorioRegistroDeAcesso : consulta registros
    RelatorioDeAcessos <|-- RelatorioDeAcessosTexto
    RelatorioDeAcessos <|-- RelatorioDeAcessosCsv
```

---

## 4. Rastreabilidade complementar

| Item solicitado | Onde está representado |
| --------------- | ---------------------- |
| Descrição dos 3 casos de uso mais relevantes | Seção 1 deste documento |
| Diagrama de casos de uso com requisitos funcionais | Seção 2 deste documento |
| CRUD de `Usuario` | `GerenciadorDeUsuarios`, `Usuario`, `RepositorioUsuario` |
| CRUD de `UnidadeBasicaSaude` | `GerenciadorDeUnidades`, `UnidadeBasicaSaude`, `RepositorioUnidadeBasicaSaude` |
| Repository | `RepositorioUsuario`, `RepositorioUnidadeBasicaSaude`, `RepositorioRegistroDeAcesso` |
| Factory Method | `SeletorFabrica.obter_fabrica_repositorio()` |
| Abstract Factory | `FabricaRepositorio` e fábricas concretas |
| Adapter | `AdaptadorArquivoDeLog` e `ArquivoDeLogSimples` |
| Template Method | `RelatorioDeAcessos.gerar()` e subclasses |
| Facade | `FacadeSingletonController` |
| Singleton | `FacadeSingletonController.instancia()` |



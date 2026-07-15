# Diagramas do Sistema — Gerenciamento de Usuários

**App Experimental de Triagem em Saúde**

Este documento concentra os diagramas do **contexto de Gerenciamento de Usuários**:
o cadastro e a administração dos perfis que operam o sistema — **Administrador**,
**Gestor da Unidade de Saúde** e **Médico**.

> O **Paciente** não é usuário do sistema (ver Documento de Requisitos, §2.4): seus dados
> são registrados pelo Médico no contexto de *Atendimento/Triagem*, que será diagramado
> em sprint própria. Por isso ele não aparece aqui.

Os diagramas estão alinhados aos requisitos **RF02** (gerenciar gestores e médicos),
**RF03** (autenticar por perfil) e **NF008** (controle de acesso por perfil), e à decisão
arquitetural [ADR-001 — Arquitetura Hexagonal](adr/ADR-001-arquitetura-hexagonal.md).

---

## 1. Diagrama de Casos de Uso

Atores e suas interações com o contexto de gerenciamento de usuários. Há três atores
(mínimo de dois atendido): **Administrador** e **Gestor** dirigem a gestão; o **Médico**
consulta o próprio cadastro.

```mermaid
flowchart LR
    Admin([Administrador])
    Gestor([Gestor da Unidade])
    Medico([Médico])

    subgraph SGU[Gerenciamento de Usuários]
        UC_AUTH(("Autenticar por Perfil"))
        UC_ADD("Adicionar Usuário")
        UC_LIST("Listar Usuários")
        UC_TOGGLE("Ativar / Desativar Usuário")
        UC_SELF("Consultar Próprio Cadastro")
    end

    Admin --> UC_ADD
    Admin --> UC_LIST
    Admin --> UC_TOGGLE

    Gestor --> UC_ADD
    Gestor --> UC_LIST

    Medico --> UC_SELF

    UC_ADD -.->|"«include»"| UC_AUTH
    UC_LIST -.->|"«include»"| UC_AUTH
    UC_TOGGLE -.->|"«include»"| UC_AUTH
    UC_SELF -.->|"«include»"| UC_AUTH
```

> [!NOTE]
> **Hierarquia de permissões (NF008):**
> - **Administrador:** adiciona **Gestores** e os vincula a uma UBS; lista e ativa/desativa usuários no escopo global.
> - **Gestor:** adiciona **Médicos** dentro da **sua própria** unidade; lista os usuários da unidade.
> - **Médico:** consulta apenas o próprio cadastro.
>
> Toda ação de gestão exige **Autenticar por Perfil** («include»), garantindo que um perfil
> não acesse funções de outro.

**Foco da Sprint 1:** os casos de uso **Adicionar Usuário** e **Listar Usuários**.

---

## 2. Diagrama de Classe de Análise (ECB)

Padrão **ECB (Entity, Control, Boundary)**. A leitura em chave hexagonal (ADR-001):
a **Fronteira** é um *adaptador primário*, o **Controle** é o *núcleo / caso de uso*, as
**Entidades** são o *domínio*, e `RepositorioUsuario` é uma **porta secundária**.

Para o **Laboratório 2 — Tratamento de Erros**, o diagrama foi atualizado para incluir:

* os campos `login` e `senha` na entidade `Usuario`;
* validações de campos usando exceções;
* tratamento de CPF duplicado;
* tratamento de erro de persistência;
* dois mecanismos de persistência: memória RAM e arquivo binário;
* manutenção da arquitetura hexagonal, com o núcleo dependendo da porta `RepositorioUsuario`.

O arquivo PlantUML do diagrama está disponível em:
[`diagrama-classes.puml`](diagrama-classes.puml)

```mermaid
classDiagram
    %% ---------- Fronteira (Boundary) = adaptador primário ----------
    class TelaGerenciamentoUsuarios {
        <<Boundary>>
        +exibirFormularioUsuario()
        +exibirListaUsuarios(usuarios)
        +solicitarDadosUsuario()
    }

    %% ---------- Controle (Control) = núcleo / casos de uso ----------
    class GerenciadorDeUsuarios {
        <<Control>>
        -repositorio: RepositorioUsuario
        +adicionarUsuario(dados) Usuario
        +listarUsuarios() List~Usuario~
        +ativarOuDesativar(id, ativo)
    }

    %% ---------- Porta secundária (hexagonal) ----------
    class RepositorioUsuario {
        <<interface>>
        +salvar(usuario) Usuario
        +buscarTodos() List~Usuario~
        +buscarPorCpf(cpf) Usuario
        +buscarPorId(id) Usuario
    }

    %% ---------- Adaptadores de persistência ----------
    class RepositorioUsuarioEmMemoria {
        <<Adapter>>
        -usuarios: Dict~int, Usuario~
        -proximoId: int
        +salvar(usuario) Usuario
        +buscarTodos() List~Usuario~
        +buscarPorCpf(cpf) Usuario
        +buscarPorId(id) Usuario
    }

    class RepositorioUsuarioArquivoBinario {
        <<Adapter>>
        -caminhoArquivo: string
        +salvar(usuario) Usuario
        +buscarTodos() List~Usuario~
        +buscarPorCpf(cpf) Usuario
        +buscarPorId(id) Usuario
    }

    %% ---------- Entidades (Entity) = domínio ----------
    class Usuario {
        <<Entity>>
        +id: int
        +nome: string
        +cpf: string
        +email: string
        +telefone: string
        +login: string
        +senha: string
        +ativo: boolean
        +perfil: Perfil
        +criar(dados) Usuario
    }

    class Perfil {
        <<enumeration>>
        ADMINISTRADOR
        GESTOR
        MEDICO
    }

    class Administrador {
        <<Entity>>
    }

    class Gestor {
        <<Entity>>
        +dataCadastro: Date
        +idUnidade: int
    }

    class Medico {
        <<Entity>>
        +crm: string
        +especialidade: string
        +idUnidade: int
    }

    class UnidadeBasicaSaude {
        <<Entity>>
        +id: int
        +nome: string
        +cnpj: string
        +endereco: string
        +telefone: string
        +horarioFuncionamento: string
        +ativa: boolean
    }

    %% ---------- Exceções ----------
    class ErroDeDominio {
        <<Exception>>
    }

    class ErroDeValidacao {
        <<Exception>>
    }

    class CpfDuplicado {
        <<Exception>>
    }

    class ErroDePersistencia {
        <<Exception>>
    }

    %% ---------- Relações ----------
    TelaGerenciamentoUsuarios ..> GerenciadorDeUsuarios : solicita

    GerenciadorDeUsuarios ..> RepositorioUsuario : usa «porta»
    GerenciadorDeUsuarios ..> Usuario : cria / consulta
    GerenciadorDeUsuarios ..> CpfDuplicado : lança

    RepositorioUsuario <|.. RepositorioUsuarioEmMemoria
    RepositorioUsuario <|.. RepositorioUsuarioArquivoBinario
    RepositorioUsuario ..> Usuario : persiste

    RepositorioUsuarioArquivoBinario ..> ErroDePersistencia : lança

    Usuario <|-- Administrador
    Usuario <|-- Gestor
    Usuario <|-- Medico
    Usuario --> Perfil : possui
    Usuario ..> ErroDeValidacao : lança

    ErroDeDominio <|-- ErroDeValidacao
    ErroDeDominio <|-- CpfDuplicado
    ErroDeDominio <|-- ErroDePersistencia

    Gestor --> UnidadeBasicaSaude : vinculado a
    Medico --> UnidadeBasicaSaude : vinculado a
```

> [!NOTE]
>
> * `Usuario` é a **abstração comum** dos três perfis; `Perfil` distingue o tipo de acesso (RF03).
> * No Laboratório 2, `Usuario` passa a representar também os dados de autenticação `login` e `senha`.
> * As validações de `login`, `senha`, e demais campos obrigatórios são representadas por `ErroDeValidacao`.
> * `GerenciadorDeUsuarios` continua dependendo da **interface** `RepositorioUsuario`, nunca de uma implementação concreta.
> * `RepositorioUsuarioEmMemoria` e `RepositorioUsuarioArquivoBinario` são adaptadores intercambiáveis da mesma porta.
> * Falhas de leitura ou gravação no arquivo binário são representadas por `ErroDePersistencia`.


---

## 3. Tarefa 5 — Padrões Adapter e Template Method (estatísticas de acesso)

Cada tentativa de autenticação passa a ser registrada como `RegistroDeAcesso`
pela porta `RepositorioRegistroDeAcesso`, e os relatórios de estatísticas são
gerados por um **Template Method** que funciona sobre qualquer adaptador da
porta — inclusive o **Adapter** de arquivo de log.

```mermaid
classDiagram
    %% ---------- Núcleo ----------
    class GerenciadorDeUsuarios {
        <<Control>>
        -repositorio: RepositorioUsuario
        -repositorioAcessos: RepositorioRegistroDeAcesso
        +autenticar(email, senha) Usuario
    }

    class RegistroDeAcesso {
        <<Entity>>
        +id: int
        +email: string
        +sucesso: boolean
        +dataHora: DateTime
        +criar(dados) RegistroDeAcesso
    }

    class RepositorioRegistroDeAcesso {
        <<interface>>
        +salvar(registro) RegistroDeAcesso
        +buscarTodos() List~RegistroDeAcesso~
    }

    %% ---------- Padrão Adapter ----------
    class RepositorioRegistroDeAcessoEmMemoria {
        <<Adapter>>
    }

    class AdaptadorArquivoDeLog {
        <<Adapter GoF>>
        +salvar(registro) RegistroDeAcesso
        +buscarTodos() List~RegistroDeAcesso~
    }

    class ArquivoDeLogSimples {
        <<Adaptee>>
        +anotar(linha)
        +lerLinhas() List~string~
    }

    %% ---------- Padrão Template Method ----------
    class RelatorioDeAcessos {
        <<abstract>>
        +gerar() string
        #calcularEstatisticas(registros) EstatisticasDeAcesso
        #cabecalho()* string
        #linhaPorEmail(estatistica)* string
        #rodape(estatisticas)* string
    }

    class RelatorioDeAcessosTexto
    class RelatorioDeAcessosCsv

    %% ---------- Relações ----------
    GerenciadorDeUsuarios ..> RepositorioRegistroDeAcesso : usa «porta»
    GerenciadorDeUsuarios ..> RegistroDeAcesso : cria

    RepositorioRegistroDeAcesso <|.. RepositorioRegistroDeAcessoEmMemoria
    RepositorioRegistroDeAcesso <|.. AdaptadorArquivoDeLog
    AdaptadorArquivoDeLog --> ArquivoDeLogSimples : adapta

    RelatorioDeAcessos ..> RepositorioRegistroDeAcesso : usa «porta»
    RelatorioDeAcessos <|-- RelatorioDeAcessosTexto
    RelatorioDeAcessos <|-- RelatorioDeAcessosCsv
```

> [!NOTE]
> **Adapter (GoF):** `AdaptadorArquivoDeLog` (Adapter) traduz `RegistroDeAcesso` de/para
> linhas de texto, permitindo que `ArquivoDeLogSimples` (Adaptee, interface incompatível)
> atenda à porta `RepositorioRegistroDeAcesso` (Target).
>
> **Template Method (GoF):** `RelatorioDeAcessos.gerar()` fixa o esqueleto do algoritmo
> (coletar → calcular estatísticas → cabeçalho/corpo/rodapé); as concretas implementam
> apenas os hooks de formatação (`*` = abstrato).

---

## 4. Sprint 3 — Padrões Facade + Singleton e CRUD de Unidade Básica de Saúde

### 4.1 Nova entidade: UnidadeBasicaSaude

A Sprint 3 introduz o cadastro (CRUD) da entidade **UnidadeBasicaSaude** (UBS),
que possui relacionamento indireto com **Usuario** — os perfis Gestor e Médico
estão vinculados a uma unidade de saúde. A entidade segue as mesmas invariantes
do domínio: validação de campos obrigatórios e validação de formato de CNPJ.

### 4.2 Padrões Singleton e Facade: FacadeSingletonController

A classe `FacadeSingletonController` aplica dois padrões GoF simultaneamente:

- **Singleton:** garante que exista uma única instância por processo, criada
  sob demanda (*lazy initialization*) na primeira chamada ao método de classe
  `instancia()`. O atributo de classe `_instancia_unica` armazena a referência.

- **Facade:** expõe uma interface simplificada que esconde a montagem interna
  dos dois gerenciadores (`GerenciadorDeUsuarios` e `GerenciadorDeUnidades`)
  e seus respectivos repositórios. O cliente da fachada não precisa conhecer
  a arquitetura interna — basta chamar métodos como `adicionar_usuario()`,
  `adicionar_unidade()` ou `obter_quantidade_total_entidades_cadastradas()`.

O método `obter_quantidade_total_entidades_cadastradas()` retorna a soma de
todas as entidades (usuários + unidades) persistidas no sistema, conforme
exigido pela atividade da Sprint 3.

O arquivo PlantUML do diagrama atualizado está disponível em:
[`diagrama-classes-v2.puml`](diagrama-classes-v2.puml)

```mermaid
classDiagram
    %% ---------- Padrão Facade + Singleton ----------
    class FacadeSingletonController {
        <<Facade>>
        <<Singleton>>
        -{static} _instancia_unica: FacadeSingletonController
        -_gerenciador_usuarios: GerenciadorDeUsuarios
        -_gerenciador_unidades: GerenciadorDeUnidades
        +{static} instancia() FacadeSingletonController
        +{static} resetar_instancia()
        +obter_quantidade_total_entidades_cadastradas() int
        +adicionar_usuario(…) Usuario
        +listar_usuarios() List~Usuario~
        +autenticar(email, senha) Usuario
        +adicionar_unidade(…) UnidadeBasicaSaude
        +listar_unidades(apenas_ativas) List~UnidadeBasicaSaude~
        +buscar_unidade_por_id(id) UnidadeBasicaSaude
        +atualizar_unidade(…) UnidadeBasicaSaude
        +remover_unidade(id) UnidadeBasicaSaude
    }

    %% ---------- Gerenciadores (Controllers) ----------
    class GerenciadorDeUsuarios {
        <<Control>>
        -repositorio: RepositorioUsuario
        -repositorio_acessos: RepositorioRegistroDeAcesso
        +adicionar_usuario(…) Usuario
        +listar_usuarios() List~Usuario~
        +autenticar(email, senha) Usuario
    }

    class GerenciadorDeUnidades {
        <<Control>>
        -repositorio: RepositorioUnidadeBasicaSaude
        +adicionar_unidade(…) UnidadeBasicaSaude
        +listar_unidades(apenas_ativas) List~UnidadeBasicaSaude~
        +buscar_unidade_por_id(id) UnidadeBasicaSaude
        +atualizar_unidade(…) UnidadeBasicaSaude
        +remover_unidade(id) UnidadeBasicaSaude
    }

    %% ---------- Portas secundárias ----------
    class RepositorioUsuario {
        <<interface>>
        +salvar(usuario) Usuario
        +buscar_todos() List~Usuario~
        +buscar_por_cpf(cpf) Usuario
        +buscar_por_email(email) Usuario
    }

    class RepositorioUnidadeBasicaSaude {
        <<interface>>
        +salvar(unidade) UnidadeBasicaSaude
        +buscar_todas() List~UnidadeBasicaSaude~
        +buscar_por_id(id) UnidadeBasicaSaude
        +buscar_por_cnpj(cnpj) UnidadeBasicaSaude
    }

    %% ---------- Entidades ----------
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

    %% ---------- Adaptadores ----------
    class RepositorioUsuarioEmMemoria {
        <<Adapter>>
    }
    class RepositorioUsuarioBancoDeDados {
        <<Adapter>>
    }
    class RepositorioUnidadeEmMemoria {
        <<Adapter>>
    }

    %% ---------- Exceções ----------
    class CnpjDuplicado {
        <<Exception>>
    }
    class UnidadeNaoEncontrada {
        <<Exception>>
    }

    %% ---------- Relações ----------
    FacadeSingletonController --> GerenciadorDeUsuarios : delega
    FacadeSingletonController --> GerenciadorDeUnidades : delega

    GerenciadorDeUsuarios ..> RepositorioUsuario : usa «porta»
    GerenciadorDeUsuarios ..> Usuario : cria / consulta
    GerenciadorDeUnidades ..> RepositorioUnidadeBasicaSaude : usa «porta»
    GerenciadorDeUnidades ..> UnidadeBasicaSaude : cria / consulta

    RepositorioUsuario <|.. RepositorioUsuarioEmMemoria
    RepositorioUsuario <|.. RepositorioUsuarioBancoDeDados
    RepositorioUnidadeBasicaSaude <|.. RepositorioUnidadeEmMemoria

    Usuario --> Perfil : possui

    GerenciadorDeUnidades ..> CnpjDuplicado : lança
    GerenciadorDeUnidades ..> UnidadeNaoEncontrada : lança
```

> [!NOTE]
> **Singleton:** `FacadeSingletonController.instancia()` é o único ponto de acesso.
> A construção direta (`__init__`) continua pública para facilitar testes com
> repositórios injetados, mas em produção deve-se usar sempre `instancia()`.
>
> **Facade:** o cliente da fachada não precisa conhecer `GerenciadorDeUsuarios`
> nem `GerenciadorDeUnidades` — toda a orquestração interna está encapsulada.
>
> **Contagem de entidades:** `obter_quantidade_total_entidades_cadastradas()`
> soma usuários e unidades persistidos, conforme exigido pela Sprint 3.

---

## 5. Rastreabilidade

| Caso de uso / item técnico      | Requisito / Laboratório  | Entrega          |
| ------------------------------- | ------------------------ | ---------------- |
| Autenticar por Perfil           | RF03 / NF008             | futura           |
| Adicionar Usuário               | RF02                     | Sprint 1 / Sprint 2 |
| Listar Usuários                 | RF02                     | Sprint 1         |
| Validar Login                   | Sprint 2                    | Sprint 2            |
| Validar Senha                   | Sprint 2 / Política AWS IAM | Sprint 2            |
| Tratar Erros de Validação       | Sprint 2                    | Sprint 2            |
| Persistência em Memória RAM     | ADR-002 / Sprint 2          | Sprint 1 / Sprint 2 |
| Persistência em Arquivo Binário | Sprint 2                    | Sprint 2            |
| Tratar Erros de Persistência    | Sprint 2                    | Sprint 2            |
| Ativar / Desativar Usuário      | RF01 / RF02              | futura           |
| Consultar Próprio Cadastro      | RF Médico                | futura           |
| Registrar Acessos (autenticação) | Tarefa 5 / NF011-C      | Tarefa 5         |
| Adapter de Log de Acessos       | Tarefa 5 (padrão Adapter) | Tarefa 5        |
| Relatórios de Estatísticas      | Tarefa 5 (Template Method) | Tarefa 5       |
| CRUD Unidade Básica de Saúde    | Sprint 3 (nova entidade)  | Sprint 3        |
| Facade + Singleton Controller   | Sprint 3 (Padrões GoF)   | Sprint 3         |
| Contagem total de entidades     | Sprint 3 (método Facade)  | Sprint 3        |
| Diagrama de classes atualizado  | Sprint 3 (diagrama v2)   | Sprint 3         |


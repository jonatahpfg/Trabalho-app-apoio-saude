# Documento de Requisitos — App Experimental de Triagem Médica

Este documento especifica os Requisitos Funcionais (RF), Requisitos Não Funcionais (RNF) e Regras de Negócio (RN) do **App Experimental de Apoio à Triagem Médica**, atualizados até a versão final do sistema (Sprint 7), contemplando a Arquitetura Hexagonal, os Padrões de Projeto GoF e o Modelo C4.

---

## 1. Visão Geral do Sistema

O sistema é um aplicativo de apoio à triagem clínica na atenção primária de saúde. Ele oferece o gerenciamento completo de **Usuários** (Administradores, Gestores e Médicos), o gerenciamento de **Unidades Básicas de Saúde (UBS)**, o **Registro de Acessos** dos usuários, a geração de **Relatórios Estatísticos**, o mecanismo de **Desfazer Alterações em UBS (Memento)** e o controle rigoroso de **Autorização por Perfil (Proxy RBAC)**.

---

## 2. Requisitos Funcionais (RF)

| Código | Nome | Descrição |
| :--- | :--- | :--- |
| **RF01** | **Gerenciar Unidades Básicas de Saúde (UBS)** | O sistema deve permitir cadastrar, listar, buscar por ID, atualizar e desativar logicamente Unidades Básicas de Saúde. |
| **RF02** | **Gerenciar Usuários** | O sistema deve permitir cadastrar, listar (com filtro de ativos), buscar por ID/login, atualizar dados/senha e desativar/reativar logicamente usuários. |
| **RF03** | **Autenticar Usuário** | O sistema deve autenticar usuários por meio de `login` e `senha`, emitindo exceções apropriadas para erros e notificando observadores sobre o evento. |
| **RF04** | **Registrar Acessos** | O sistema deve registrar automaticamente cada tentativa de login (sucesso ou falha) contendo e-mail/login, status e data/hora. |
| **RF05** | **Gerar Relatórios de Acesso** | O sistema deve permitir a geração de relatórios consolidados de acesso nos formatos Texto e CSV. |
| **RF06** | **Desfazer Atualização de UBS** | O sistema deve permitir desfazer a última atualização bem-sucedida realizada em uma UBS, restaurando seu estado anterior exato. |
| **RF07** | **Contagem Total de Entidades** | O sistema deve fornecer a contagem combinada de entidades cadastradas (usuários e unidades) via fachada. |

---

## 3. Requisitos Não Funcionais (RNF)

| Código | Nome | Descrição |
| :--- | :--- | :--- |
| **RNF01** | **Arquitetura Hexagonal** | A aplicação deve separar rigidamente o Domínio, as Portas (Interfaces), a Aplicação (Gerenciadores/Comandos) e os Adaptadores (Persistência e Log). |
| **RNF02** | **Modelo C4 de Arquitetura** | A documentação arquitetural deve ser estruturada em 4 níveis: Contexto, Contêineres, Componentes e Código. |
| **RNF03** | **Padrões de Projeto GoF** | O sistema deve implementar de forma explícita 11 padrões GoF (Facade, Singleton, Command, Memento, Proxy, Observer, Repository, Factory Method, Abstract Factory, Adapter, Template Method). |
| **RNF04** | **Armazenamento Plural (RAM e SQLite)** | O repositório deve suportar alternância dinâmica entre persistência em Memória RAM e banco de dados SQLite sem alteração do código de aplicação. |
| **RNF05** | **Segurança de Senhas** | As senhas nunca devem ser salvas em texto plano; devem ser armazenadas exclusivamente em formato de hash criptográfico. |
| **RNF06** | **Controle de Acesso por Perfil (RBAC)** | Operações sensíveis devem passar por verificação de perfil via Proxy antes da execução no gerenciador real. |
| **RNF07** | **Preservação de Registros (Exclusão Lógica)** | Nenhuma exclusão de Usuário ou UBS deve apagar fisicamente registros do banco; deve ser realizada exclusão lógica (`ativo = False`). |
| **RNF08** | **Desacoplamento por Eventos** | A notificação de login para auditoria e estatísticas deve ocorrer por publicação de eventos (Observer) sem acoplamento direto no gerenciador. |
| **RNF09** | **Integridade de Validações** | Entidades alteradas devem retornar novas instâncias imutáveis de forma que uma falha de validação nunca corrompa o objeto existente. |
| **RNF10** | **Interface Unificada por Comandos** | A camada de aplicação deve encapsular todas as intenções de usuário como instâncias do padrão Command executadas por um Invoker central. |

---

## 4. Regras de Negócio (RN)

- **RN01 — Login Obrigatório e Formato:** Todo usuário deve possuir login obrigatório, com no máximo 12 caracteres e **sem conter números**.
- **RN02 — Política de Senhas:** A senha deve ter entre 8 e 128 caracteres, conter pelo menos 3 dos 4 grupos (letras maiúsculas, minúsculas, números e caracteres especiais) e ser diferente do nome e do e-mail.
- **RN03 — CPF e CNPJ Únicos:** Não é permitido cadastrar dois usuários com o mesmo CPF ou login, nem duas UBS com o mesmo CNPJ.
- **RN04 — Matriz de Permissões RBAC:**
  - **ADMINISTRADOR:** Acesso total a todas as operações de Usuários e UBS.
  - **GESTOR:** Pode gerenciar UBS, listar/buscar usuários e gerar relatórios. Não pode criar/alterar usuários nem remover UBS.
  - **MÉDICO:** Pode apenas autenticar-se e consultar dados próprios ou listar UBS ativas.
- **RN05 — Regra do Memento para UBS:**
  - Guarda apenas o estado imutável anterior à **última atualização bem-sucedida**.
  - Atualizações inválidas não afetam o Memento salvo.
  - Ao executar o desfazer, o estado é restaurado, persistido e o Memento é **descartado** (não permite desfazer duplo sequencial sem nova alteração).
- **RN06 — Autenticação de Usuário Inativo:** Tentativas de login por usuários desativados devem ser recusadas com a exceção `UsuarioInativo`.

---

## 5. Rastreabilidade com os Padrões e Camadas C4

| Requisito / Padrão | Módulo de Código | Nível C4 |
| :--- | :--- | :--- |
| **Facade / Singleton** | `FacadeSingletonController` | Componente / Código |
| **Command** | `ExecutorDeComandos`, `Comando` (e concretos) | Componente / Código |
| **Proxy** | `ProxyGerenciadorDeUsuarios`, `ProxyGerenciadorDeUnidades` | Componente / Código |
| **Observer** | `PublicadorDeEventosDeAutenticacao`, `ObservadorDeLogDeAutenticacao`, `ObservadorDeEstatisticasDeAutenticacao` | Componente / Código |
| **Memento** | `UnidadeBasicaSaude`, `MementoUnidadeBasicaSaude`, `HistoricoDeUnidade` | Componente / Código |
| **Abstract Factory / Factory Method** | `FabricaRepositorio`, `FabricaRepositorioEmMemoria`, `FabricaRepositorioBancoDeDados`, `SeletorFabrica` | Componente / Código |
| **Repository / Adapter** | `RepositorioUsuario`, `RepositorioUnidadeBasicaSaude`, `AdaptadorArquivoDeLog` | Componente / Código |
| **Template Method** | `RelatorioDeAcessos`, `RelatorioDeAcessosTexto`, `RelatorioDeAcessosCsv` | Componente / Código |

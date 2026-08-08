# App de Apoio à Triagem Médica

**Repositório GitHub:** [https://github.com/jonatahpfg/Trabalho-app-apoio-saude](https://github.com/jonatahpfg/Trabalho-app-apoio-saude)

Aplicativo de apoio à triagem clínica na atenção primária, desenvolvido como projeto acadêmico da disciplina de Engenharia de Software / Métodos de Desenvolvimento de Software.

O sistema contempla o gerenciamento de unidades básicas de saúde, gestores, médicos e demais informações necessárias ao fluxo de atendimento, estruturado com **Arquitetura Hexagonal (Ports & Adapters)**, **Modelo de Arquitetura C4** e **Padrões de Projeto GoF**.

> O sistema possui caráter experimental e não substitui avaliação médica, diagnóstico profissional ou protocolos institucionais de atendimento.

---

## 🏗️ Arquitetura e Padrões

O projeto adota a **Arquitetura Hexagonal** desacoplando domínio, aplicação, portas e adaptadores, aliada aos seguintes padrões de projeto:

- **Criacionais:** Singleton, Factory Method, Abstract Factory.
- **Estruturais:** Facade, Proxy, Adapter, Repository.
- **Comportamentais:** Command, Memento, Observer, Template Method.

A documentação arquitetural segue o **Modelo C4** em 4 níveis:
1. **Contexto (Level 1):** Usuários, atores (Administrador, Gestor, Médico) e interação com o sistema.
2. **Contêineres (Level 2):** Aplicativo Mobile (React Native), Backend Python, Banco SQLite e Logs.
3. **Componentes (Level 3):** Fachada, Executores de Comandos, Proxies RBAC, Gerenciadores, Publicador Observer, Fábricas e Repositórios.
4. **Código / Classes (Level 4):** Diagrama detalhado de classes com identificação visual dos padrões por código de cores.

---

## 📁 Estrutura do projeto

```text
backend/   Serviço Python organizado segundo Arquitetura Hexagonal
           (domínio, portas, aplicação e adaptadores), testado via Pytest.

mobile/    Aplicativo React Native previsto para evolução do produto.

docs/      Documento de requisitos, casos de uso, registros de decisões (ADRs)
           e diagramas C4 em Mermaid e PlantUML com padrões coloridos.
```

---

## 🚀 Como Executar os Testes

Para rodar toda a suíte de testes unitários e de integração do backend:

```powershell
cd backend
pytest
```
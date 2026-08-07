# Architecture Decision Records (ADR)

Este diretório registra as principais decisões arquiteturais do projeto.

Cada decisão relevante é documentada em um arquivo no formato
`ADR-NNN-titulo.md`, permitindo registrar o contexto da decisão,
a solução adotada e suas consequências para o sistema.

Conforme definido no `CONTRIBUTING.md`, alterações relevantes em
contratos públicos, interfaces ou decisões arquiteturais devem ser
registradas por meio de um novo ADR.

| ADR | Título | Status |
|-----|--------|--------|
| [ADR-001](ADR-001-arquitetura-hexagonal.md) | Adotar Arquitetura Hexagonal (Ports & Adapters) | Aceito |
| [ADR-002](ADR-002-stack-tecnologica.md) | Stack tecnológica — Python (backend) + React Native (mobile) | Aceito |
| [ADR-003](ADR-003-autenticacao-por-login.md) | Adotar login como identificador de autenticação | Aceito |
| [ADR-004](ADR-004-exclusao-logica-de-usuarios.md) | Exclusão lógica de usuários e ampliação da porta `RepositorioUsuario` | Aceito |

## Evolução das decisões

Os ADRs são preservados no repositório como histórico das decisões
arquiteturais do projeto.

Uma decisão posterior pode complementar ou modificar uma decisão
anterior sem apagar o registro histórico da solução inicialmente adotada.
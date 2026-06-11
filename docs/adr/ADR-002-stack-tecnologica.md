# ADR-002: Stack tecnológica — Python (backend) + React Native (mobile)

- **Status:** Aceito
- **Data:** 2026-06-10
- **Decisores:** Equipe do projeto
- **Relacionado:** [ADR-001 — Arquitetura Hexagonal](ADR-001-arquitetura-hexagonal.md) (deixou a stack pendente)

---

## Contexto

O ADR-001 adotou a arquitetura hexagonal, mas deixou explicitamente pendente a escolha de
linguagem e frameworks. Os requisitos pedem um aplicativo móvel Android-first (NF012) e uma
solução distribuída com separação clara entre interface, regras de negócio, persistência e
serviços externos (NF010).

É preciso fixar a stack antes de iniciar a implementação da Sprint 1 (gerenciamento de
usuários), para definir a divisão de pacotes e as ferramentas de build e teste.

## Decisão

- **Backend:** **Python 3.12**, organizado segundo a arquitetura hexagonal do ADR-001
  (domínio, portas, aplicação/casos de uso, adaptadores).
- **Mobile:** **React Native** (sprints futuras), cobrindo Android (NF012) e abrindo caminho
  para iOS sem reescrita.
- **Persistência na Sprint 1:** adaptador **em memória (RAM)** da porta `RepositorioUsuario`.
  Bancos reais entram em sprint posterior, trocando apenas o adaptador.
- **Ferramentas (backend):** `pytest` + `pytest-cov` para testes e cobertura; `ruff` para lint.
- **Organização do repositório (monorepo):**
  - `backend/` — serviço Python.
  - `mobile/` — aplicativo React Native (reservado, fora do escopo da Sprint 1).

## Consequências

### Positivas
- Python dá um núcleo de domínio simples, legível e rápido de testar — adequado ao foco da
  Sprint 1 e à didática do projeto.
- React Native atende ao alvo Android (NF012) e permite expansão para iOS.
- A porta `RepositorioUsuario` isola a decisão de persistência: memória agora, banco depois,
  sem tocar no núcleo (coerente com ADR-001).

### Negativas / custos
- Duas linguagens no repositório (Python e JS/TS) — exige disciplina de organização (monorepo
  com `backend/` e `mobile/` separados).
- O contrato entre app e backend (porta primária HTTP/API) ainda não existe; será objeto de
  um ADR próprio quando a comunicação mobile↔backend for implementada.

### Pendências
- Definir a porta primária (API HTTP) e seu contrato em ADR futuro.
- Definir o banco de dados real e seu adaptador em ADR/sprint posterior.

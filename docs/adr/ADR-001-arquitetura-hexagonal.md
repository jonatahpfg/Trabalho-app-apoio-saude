# ADR-001: Adotar Arquitetura Hexagonal (Ports & Adapters)

- **Status:** Aceito
- **Data:** 2026-06-10
- **Decisores:** Equipe do projeto (Jonata, Esdras, Flávio, Gabriel, Mateus)
- **Referência:** Cockburn, A. "Hexagonal (Ports & Adapters) Architecture", HaT Technical Report 2005.02

---

## Contexto

O App Experimental de Triagem em Saúde precisa integrar quatro mundos externos distintos:

1. **Atores que dirigem o sistema** — Administrador, Gestor e Médico, por meio de UI Android.
2. **Persistência** — servidor central, com necessidade de operação offline e sincronização posterior (RF10, NF005).
3. **Serviços externos de IA** — triagem de dengue, lesão cutânea, laudos e saúde mental, via APIs em nuvem que podem ficar indisponíveis (NF004, NF006) e que exigem minimização de dados sensíveis (NF009).
4. **Testes automatizados** — necessários para validar a lógica clínica sem depender de emulador Android nem de IA real.

O documento de requisitos já impõe **separação de responsabilidades entre interface, regras de negócio, persistência e processamento externo** (NF010) e **modularidade dos módulos clínicos** (NF013). O diagrama de classes de análise já segue o padrão ECB (Entity, Control, Boundary).

Uma arquitetura em camadas tradicional (UI → serviço → banco) tende a vazar lógica de negócio para a UI ou para os clientes de API externa, justamente o problema central que o artigo de Cockburn descreve. Também não modela bem as quatro conversas externas com tecnologias substituíveis.

## Decisão

Adotar a **Arquitetura Hexagonal (Ports & Adapters)** como estilo arquitetural do sistema.

- O **núcleo da aplicação** (regras de gestão hierárquica e lógica dos módulos de triagem) é isolado e ignorante de qual UI, banco ou IA está do outro lado.
- A comunicação com o mundo externo ocorre por **portas** (interfaces que definem uma conversa com propósito), com **adaptadores** intercambiáveis.
- A dependência aponta sempre **para dentro** (Dependency Inversion): adaptadores dependem do núcleo, nunca o contrário. Adaptadores concretos são injetados de fora.

### Mapeamento das portas

**Portas primárias (driving) — dirigem a aplicação:**

| Porta | Adaptadores previstos |
|-------|-----------------------|
| Operação clínica e de gestão | UI Android (Admin/Gestor/Médico), harness de teste automatizado, eventual API programa-a-programa |

**Portas secundárias (driven) — dirigidas pela aplicação:**

| Porta | Adaptadores previstos |
|-------|-----------------------|
| Persistência | servidor central, store local offline, mock em memória |
| Triagem por IA (dengue, lesão cutânea, laudo, saúde mental) | API em nuvem real, mock, fallback de indisponibilidade |

### Correspondência com o padrão ECB já adotado

| ECB (diagrama de análise) | Hexagonal |
|---------------------------|-----------|
| Boundary (`TelaAdmin`, `TelaGestor`, `TelaMedico`) | Adaptadores primários |
| Control (`ControleSistemaGlobal`, `ControleGestaoUnidade`, `ControleMedico`) | Núcleo / casos de uso na fronteira do hexágono |
| Entity (`UnidadeBasicaSaude`, `Medico`, `Paciente`, ...) | Domínio interno |

### Estrutura de pastas proposta (a confirmar quando a linguagem for definida)

> Estrutura conceitual, agnóstica de linguagem. Será materializada em um ADR ou PR posterior, junto da escolha de stack.

```
nucleo/          # domínio + casos de uso (Entity + Control). Sem dependência externa.
  dominio/       # entidades: UBS, Gestor, Medico, Paciente, Atendimento, Triagem...
  casos_de_uso/  # orquestração dos fluxos (UC001..UC003)
  portas/
    primarias/   # interfaces que a UI/testes chamam
    secundarias/ # interfaces de persistencia e de IA que o nucleo invoca
adaptadores/
  primarios/     # UI Android, harness de teste
  secundarios/   # repositorios (real/local/mock), clientes de IA (real/mock/fallback)
```

## Consequências

### Positivas

- **NF010** (funcionamento distribuído) atendido por construção: interface, regras, persistência e IA ficam em lados distintos do hexágono.
- **NF013** (modularidade clínica): cada módulo de triagem fica atrás da própria porta/adaptador, podendo evoluir ou ser removido isoladamente.
- **NF004 / NF006** (falha de IA externa): o adaptador da porta de IA concentra retry e fallback; um adaptador mock mantém a consulta funcionando quando a API cai.
- **NF009** (minimização de dados): o adaptador da porta de IA é o único ponto que desacopla/remove dado identificável antes do envio — o núcleo nunca trata disso.
- **RF10 / NF005** (offline e sincronização): adaptador de persistência local e adaptador do servidor central são intercambiáveis sob a mesma porta.
- **Testabilidade**: a lógica clínica roda isolada com mocks, sem emulador Android nem IA real.
- Casos de uso (UC001–UC003) escritos na fronteira do hexágono interno: mais curtos, estáveis e independentes de tecnologia.

### Negativas / custos

- Mais indireção e código de fronteira (interfaces + injeção de dependência) que uma abordagem em camadas direta.
- Exige disciplina para **não vazar regra de negócio** para os adaptadores (UI Android ou cliente de IA) — risco principal apontado pelo artigo.
- Definição do número exato de portas é questão de bom senso; pode ser revista conforme o sistema evolui.

### Pendências

- A estrutura de pastas final depende da escolha de linguagem/stack, ainda não decidida — será objeto de ADR próprio.
- Contratos públicos das portas devem ser registrados antes da implementação (ver CONTRIBUTING, seção 6: não alterar contratos públicos sem novo ADR).

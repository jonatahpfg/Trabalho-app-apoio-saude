# App de Apoio à Triagem Médica

Aplicativo de apoio à triagem clínica na atenção primária, desenvolvido
como projeto acadêmico da disciplina de Engenharia de Software.

O sistema contempla o gerenciamento de unidades de saúde, gestores,
médicos e demais informações necessárias ao fluxo de atendimento, além
da evolução planejada de módulos de triagem assistida por inteligência
artificial.

> O sistema possui caráter experimental e não substitui avaliação
> médica, diagnóstico profissional ou protocolos institucionais de
> atendimento.

## Estrutura do projeto

```text
backend/   Serviço Python organizado segundo Arquitetura Hexagonal
           (domínio, portas, aplicação e adaptadores).

mobile/    Aplicativo React Native previsto para evolução do projeto.

docs/      Documento de requisitos, casos de uso, diagramas,
           histórico e registros de decisões arquiteturais.
# ADR-004: Exclusão lógica de usuários e ampliação da porta RepositorioUsuario

- **Status:** Aceito
- **Decisores:** Equipe do projeto
- **Relacionado:** [ADR-001](ADR-001-arquitetura-hexagonal.md),
  [ADR-003](ADR-003-autenticacao-por-login.md), CRUD de usuários (Sprint 7)

---

## Contexto

Até a Sprint 6 o gerenciamento de usuários oferecia apenas o cadastro,
a listagem e a autenticação. O CRUD estava incompleto: não era possível
consultar um usuário específico, corrigir seus dados cadastrais nem
retirar o seu acesso ao sistema.

Duas questões precisavam ser decididas antes de completar o CRUD:

1. **Como remover um usuário.** O sistema registra tentativas de acesso
   por login (`RegistroDeAcesso`) e gera relatórios de estatísticas a
   partir desses registros. Apagar fisicamente um usuário deixaria os
   registros de acesso órfãos e comprometeria a auditoria.

2. **Como localizar um usuário para atualizar ou desativar.** A porta
   `RepositorioUsuario` só oferecia buscas por CPF, e-mail e login —
   todos dados cadastrais que podem ser alterados pela própria operação
   de atualização, o que os torna inadequados como referência estável.

O CRUD de `UnidadeBasicaSaude`, implementado na Sprint 3, já havia
resolvido as duas questões: remoção lógica e busca por identificador.

## Decisão

**1. A exclusão de usuário é sempre lógica.**

`GerenciadorDeUsuarios.desativar_usuario(id)` marca o usuário como
inativo e persiste a alteração. O registro nunca é apagado. A
autenticação, que já verificava o atributo `ativo`, passa a recusar o
usuário desativado com `UsuarioInativo`. A operação inversa é oferecida
por `reativar_usuario(id)`.

**2. A porta `RepositorioUsuario` passa a declarar `buscar_por_id`.**

O identificador é o único dado do usuário que nunca muda, sendo portanto
a referência correta para atualizar ou desativar um cadastro. A operação
é implementada pelos dois adaptadores de persistência
(`RepositorioUsuarioEmMemoria` e `RepositorioUsuarioBancoDeDados`).

**3. Ausência de registro é sinalizada por exceção na camada de aplicação.**

Os repositórios continuam devolvendo `None` quando não encontram o
registro, pois essa é a linguagem da persistência. Os casos de uso
`buscar_usuario_por_id` e `buscar_usuario_por_login` traduzem esse
`None` em `UsuarioNaoEncontrado`, mantendo o chamador livre de
verificações de nulo e coerente com `UnidadeNaoEncontrada`.

## Alterações decorrentes

- inclusão de `buscar_por_id()` na porta `RepositorioUsuario` e nos dois
  adaptadores de persistência;
- inclusão da exceção de domínio `UsuarioNaoEncontrado`;
- inclusão das operações `atualizar_dados`, `alterar_senha`, `desativar`
  e `ativar` na entidade `Usuario`, todas devolvendo uma nova instância;
- inclusão dos casos de uso `buscar_usuario_por_id`,
  `buscar_usuario_por_login`, `atualizar_usuario`, `desativar_usuario` e
  `reativar_usuario` em `GerenciadorDeUsuarios`;
- inclusão do filtro `apenas_ativos` na listagem de usuários;
- inclusão dos comandos concretos correspondentes (padrão Command) e da
  sua exposição em `FacadeSingletonController`;
- atualização dos testes, dos diagramas e da documentação do sistema.

## Consequências

### Positivas

- o histórico de acessos permanece íntegro e auditável após a saída de
  um usuário do sistema;
- a operação é reversível: um usuário desativado por engano pode ser
  reativado sem novo cadastro;
- o CRUD de usuários passa a seguir exatamente o mesmo modelo já adotado
  para Unidades Básicas de Saúde, reduzindo a carga cognitiva;
- a atualização usa uma referência estável, sem depender de dados que a
  própria operação pode alterar;
- o núcleo continua isolado da infraestrutura: só a porta foi ampliada.

### Custos

- alteração do contrato público `RepositorioUsuario`: qualquer novo
  adaptador precisa implementar `buscar_por_id`;
- a base cresce indefinidamente, já que nenhum registro é removido;
- consultas que devem considerar apenas usuários habilitados precisam
  filtrar explicitamente por `ativo` — motivo do parâmetro
  `apenas_ativos` na listagem;
- login e CPF de um usuário desativado continuam ocupados, impedindo o
  reaproveitamento em um novo cadastro.

## Alternativas consideradas

- **Exclusão física (`DELETE`).** Descartada: quebraria a rastreabilidade
  dos registros de acesso e tornaria a operação irreversível.
- **Buscar por login para atualizar.** Descartada: o login é um dos
  campos que a atualização pode alterar, o que o torna uma referência
  instável.

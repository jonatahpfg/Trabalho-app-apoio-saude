# ADR-003: Adotar login como identificador de autenticação

- **Status:** Aceito
- **Decisores:** Equipe do projeto
- **Relacionado:** gerenciamento e autenticação de usuários

---

## Contexto

A implementação inicial do contexto de gerenciamento de usuários
utilizava o endereço de e-mail como identificador para autenticação.

Durante a revisão do projeto foi identificado que o requisito definido
para o sistema previa a existência de um campo específico de login.

O login possui regras próprias de negócio e não deve ser confundido
com o e-mail cadastral do usuário.

Além disso, a alteração afeta diferentes componentes do sistema,
incluindo a entidade `Usuario`, os repositórios, o caso de uso de
autenticação, os registros de acesso e os relatórios de estatísticas.

## Decisão

Adotar o atributo `login` como identificador utilizado no processo
de autenticação.

A autenticação passa a utilizar:

- login;
- senha.

O endereço de e-mail permanece como dado cadastral, mas deixa de ser
utilizado como identificador de autenticação.

### Regras do login

O login:

1. é obrigatório;
2. deve possuir no máximo 12 caracteres;
3. deve ser único no sistema.

## Alterações decorrentes

A decisão implica as seguintes alterações no sistema:

- inclusão do atributo `login` na entidade `Usuario`;
- inclusão da operação `buscar_por_login()` na porta
  `RepositorioUsuario`;
- implementação da busca por login nos adaptadores de persistência;
- alteração do caso de uso de autenticação para receber login e senha;
- inclusão da exceção `LoginDuplicado`;
- alteração de `RegistroDeAcesso` para registrar login;
- alteração dos relatórios de acesso para agrupar estatísticas por login;
- atualização dos testes automatizados;
- atualização dos diagramas e da documentação do sistema.

## Consequências

### Positivas

- a implementação passa a corresponder ao requisito definido;
- autenticação e endereço de e-mail passam a possuir responsabilidades
  distintas;
- as regras específicas de login ficam explícitas;
- o identificador utilizado nos registros de acesso passa a ser o mesmo
  utilizado na autenticação;
- facilita futuras alterações relacionadas ao cadastro e autenticação.

### Custos

- alteração do contrato da entidade `Usuario`;
- alteração da interface `RepositorioUsuario`;
- atualização dos adaptadores de persistência;
- atualização dos testes;
- atualização dos registros, relatórios e documentação.

## Validações

As regras relacionadas ao login são implementadas por
`ValidadorLogin`.

As demais validações de usuário também foram separadas em componentes
específicos:

- `ValidadorEmail`;
- `ValidadorSenha`;
- `ValidadorPerfil`;
- `ValidadorTextoObrigatorio`.

Essa separação reduz o acoplamento da entidade `Usuario` e facilita a
manutenção das regras de negócio.
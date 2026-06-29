# README da pasta `src`

## O que esta pasta contém

A pasta `src/` contém o código-fonte principal do projeto.

Aqui fica o pacote Python `ise26`, que reúne:

- as implementações corretas;
- as implementações defeituosas;
- os metadados do experimento;
- o módulo de roteamento dinâmico usado pelos testes gerados por LLM;
- a nova camada `llm/`, responsável pela infraestrutura de geração rastreável.

## O que é a pasta `ise26`

`ise26` é o pacote principal do projeto. É por meio dele que os módulos são importados nos testes internos e na infraestrutura experimental.

Exemplo:

```python
from ise26.targets import clean_customer_names
```

## Por que o código fica dentro de `src`

Usar `src/` ajuda a separar:

- código-fonte real;
- testes;
- scripts;
- documentação;
- resultados experimentais.

Isso reduz o risco de imports inconsistentes a partir da raiz do projeto.

## Como os módulos são importados

Nos testes internos, o projeto usa `pythonpath = src` em `pytest.ini`.

Nos scripts que precisam importar `ise26` diretamente, o caminho `src/` é adicionado explicitamente quando necessário para manter o comando simples no terminal.

## O que uma pessoa iniciante precisa saber antes de mexer aqui

- Nem todo arquivo em `src/` representa regra de negócio; parte dele existe para sustentar o experimento.
- Alterar `implementations/` ou `metadata/` pode exigir atualização de testes, protocolo e documentação.
- Alterar `llm/` afeta a rastreabilidade das gerações com DeepSeek.
- Se você estiver começando, leia primeiro:
  - `src/ise26/README.md`
  - `src/ise26/implementations/README.md`
  - `src/ise26/metadata/README.md`

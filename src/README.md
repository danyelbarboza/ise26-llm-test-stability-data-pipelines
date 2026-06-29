# README da pasta `src`

## O que esta pasta contém

A pasta `src/` contém o código-fonte principal do projeto.

Aqui fica o pacote Python `ise26`, que reúne:

- as implementações corretas;
- as implementações defeituosas;
- os metadados do experimento;
- o módulo de roteamento dinâmico usado pelos testes gerados por LLM.

## O que é a pasta `ise26`

`ise26` é o pacote principal do projeto. É por meio dele que os módulos são importados nos testes e nos scripts.

Exemplo:

```python
from ise26.targets import clean_customer_names
```

## Por que o código fica dentro de `src`

Usar `src/` é uma prática comum em projetos Python porque ajuda a separar:

- o código-fonte real;
- arquivos de teste;
- documentação;
- scripts auxiliares;
- resultados experimentais.

Isso também reduz o risco de importações acidentais a partir da raiz do projeto de forma inconsistente.

## Como os módulos são importados

O projeto usa `pythonpath = src` no `pytest.ini`. Isso permite que imports como os abaixo funcionem:

```python
from ise26.implementations.correct import validate_schema
from ise26.targets import classify_payment_status
```

## O que uma pessoa iniciante precisa saber antes de mexer aqui

- Nem todo arquivo em `src/` representa “lógica de negócio”; parte dele existe para apoiar o experimento.
- Alterar comportamento em `src/ise26/implementations/` pode exigir atualização de testes, metadados e documentação.
- O arquivo `targets.py` é importante para o experimento porque ele permite trocar a implementação testada sem alterar o teste gerado.
- Se você estiver começando, leia primeiro:
  - `src/ise26/README.md`
  - `src/ise26/implementations/README.md`
  - `src/ise26/metadata/README.md`

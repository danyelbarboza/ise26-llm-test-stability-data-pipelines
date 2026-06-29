# README da pasta `results`

## O que esta pasta contém

Esta pasta concentra os arquivos produzidos pelos scripts experimentais.

Ela é dividida em:

- `raw/`
- `summary/`

## Diferença entre `raw` e `summary`

### `raw`

Contém os resultados brutos, isto é, registros detalhados de execução.

### `summary`

Contém arquivos resumidos e agregados a partir dos resultados brutos.

## Aviso importante sobre placeholders

Se os testes gerados por LLM ainda não existirem e as pastas de `generated_tests/` ainda estiverem com placeholders, os CSVs produzidos aqui não representam resultados experimentais reais.

No estado atual do repositório, os arquivos existentes em `results/` devem ser entendidos dessa forma: são saídas de validação da infraestrutura, não resultados do estudo.

## Como interpretar depois da execução real

Depois que testes reais forem executados:

- `raw/` mostrará cada execução individual;
- `summary/` ajudará a analisar comportamento por função, por execução e no geral.

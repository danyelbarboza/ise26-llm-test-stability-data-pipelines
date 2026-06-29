# Protocolo experimental do ISE26

## Objetivo

Este protocolo descreve como o experimento deve ser conduzido para avaliar testes gerados por LLMs para funções de transformação de dados em Python.

O objetivo é manter:

- consistência entre execuções;
- rastreabilidade dos artefatos;
- clareza sobre o que é dado real e o que é apenas placeholder;
- reprodutibilidade mínima para análise acadêmica posterior.

## Estado atual do repositório

No momento da redação deste protocolo:

- a infraestrutura experimental já existe;
- a organização das pastas já foi preparada;
- os testes internos já validam a base do projeto;
- os testes gerados reais por LLM ainda não fazem parte do repositório.

## Escopo

- Quantidade de funções-alvo: `6`
- Quantidade de execuções previstas por função: `5`
- Quantidade de alvos por execução: `4`
  - `1` implementação correta
  - `3` versões defeituosas

## Funções usadas

As funções oficiais do experimento são:

- `clean_customer_names`
- `deduplicate_events`
- `calculate_monthly_revenue`
- `join_customers_orders`
- `validate_schema`
- `classify_payment_status`

## Modelo de LLM

- LLM usada: `A definir`
- Versão do modelo: `A definir`
- Data da geração: `A preencher`
- Responsável pela geração: `A preencher`

## Prompt padrão

- Arquivo do prompt: `experiments/prompts/test_generation_prompt_template.md`
- O mesmo prompt deve ser usado em todas as execuções oficiais da mesma rodada experimental.
- Se o prompt mudar, a mudança deve ser registrada explicitamente antes de continuar a coleta.

## Regra sobre edição dos testes gerados

- O teste gerado pela LLM não deve ser editado manualmente por padrão.
- A resposta bruta da LLM deve ser salva antes de qualquer extração.
- A extração do código para `test_generated.py` deve preservar a lógica produzida pela LLM.
- Se houver necessidade excepcional de intervenção manual, isso deve ser registrado como limitação.

## Estrutura de salvamento

### Resposta bruta da LLM

Salvar em:

```text
experiments/raw_responses/FXX_run_YY_response.txt
```

ou

```text
experiments/raw_responses/FXX_run_YY_response.md
```

### Teste extraído

Salvar em:

```text
experiments/generated_tests/FXX/run_YY/test_generated.py
```

### Resultados brutos

Salvar em:

```text
results/raw/generated_tests_results.csv
```

### Resultados resumidos

Salvar em:

```text
results/summary/summary_by_function.csv
results/summary/summary_by_run.csv
results/summary/summary_overall.csv
```

## Critérios de execução

### Execução válida

Uma execução pode ser considerada válida para análise quando:

- existe resposta bruta rastreável da LLM;
- existe `test_generated.py` correspondente;
- o teste foi executado pelo runner;
- o registro da execução aparece no CSV bruto;
- o status não é apenas placeholder estrutural.

### Execução inválida

Uma execução deve ser tratada como inválida quando:

- o arquivo do teste está corrompido;
- o código não representa de fato a resposta gerada;
- houve intervenção manual não documentada;
- a rastreabilidade entre resposta bruta e teste foi perdida.

### Execução placeholder

Uma execução é placeholder quando:

- a pasta existe apenas para manter a estrutura;
- o arquivo ainda não contém uma suíte real gerada pela LLM;
- o runner registra o caso, mas isso não vale como dado experimental real.

## Procedimento experimental recomendado

1. Rodar `python -m pytest` para confirmar que a base está estável.
2. Ler o README principal e este protocolo.
3. Gerar o teste com a LLM usando o prompt oficial.
4. Salvar a resposta bruta da LLM.
5. Extrair o código Python para `test_generated.py`.
6. Rodar `python scripts/run_generated_tests.py`.
7. Rodar `python scripts/summarize_results.py`.
8. Revisar os CSVs produzidos.
9. Registrar observações e limitações.

## Métricas registradas

As métricas principais do experimento incluem:

- executabilidade;
- taxa de aprovação na implementação correta;
- taxa de detecção de defeitos;
- número de testes coletados;
- número de `asserts` (quando medido);
- variação entre execuções;
- quantidade de falhas por função;
- observações qualitativas.

## Limitações que devem ser registradas

- teste ausente;
- teste vazio;
- placeholder;
- extração manual necessária;
- erro de ambiente;
- ambiguidade do prompt;
- ambiguidade na interpretação da função;
- incompatibilidade de dependência ou versão.

## Integridade dos dados

- Não inventar testes gerados por LLM.
- Não inventar resultados experimentais.
- Não tratar placeholder como resultado real.
- Não apagar arquivos de resultado sem registrar.
- Preservar `stdout` e `stderr` das execuções.
- Manter coerência entre resposta bruta, teste salvo e linha do CSV bruto.

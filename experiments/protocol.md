# Protocolo experimental do ISE26

## Objetivo

Este protocolo descreve como conduzir a geração e a execução de testes automatizados produzidos por LLM para as funções de transformação de dados do projeto ISE26.

O foco é garantir:

- rastreabilidade;
- reprodutibilidade;
- comparabilidade entre execuções;
- separação clara entre placeholder estrutural e dado experimental real.

## Escopo

- Quantidade de funções-alvo: `6`
- Quantidade de execuções planejadas por função: `5`
- Quantidade total planejada de chamadas reais à LLM: `30`
- Quantidade de alvos de execução por suíte gerada: `4`
  - `1` implementação correta
  - `3` versões defeituosas

## Observação sobre dados sintéticos internos

O repositório possui `DataFrame`s sintéticos em `tests/fixtures.py` para apoiar apenas a validação interna da base.

Esses dados:

- não fazem parte dos resultados experimentais;
- não devem ser tratados como material gerado por LLM;
- não substituem os dados criados dentro dos testes gerados pela LLM.

Salvo mudança metodológica futura devidamente registrada, cada teste gerado por LLM deve definir seus próprios dados no próprio arquivo de teste.

O prompt oficial também deve reforçar que a LLM não deve importar `tests/fixtures.py`.

## Funções usadas

As funções oficiais do experimento são:

- `clean_customer_names`
- `deduplicate_events`
- `calculate_monthly_revenue`
- `join_customers_orders`
- `validate_schema`
- `classify_payment_status`

## Provedor e modelo oficiais

- Provedor: `DeepSeek`
- Modelo: `deepseek-v4-flash`
- Base URL: `https://api.deepseek.com`
- Formato da API: compatível com OpenAI
- Chave: variável de ambiente `DEEPSEEK_API_KEY`

## Parâmetros oficiais da geração

- `temperature = 0.7`
- `top_p = 1.0`
- `max_tokens = 4096`
- `stream = false`
- política de histórico: `sem histórico entre chamadas`
- política de edição manual: `salvar resposta bruta; extrair código mecanicamente; não corrigir manualmente o teste gerado`

## Arquivo oficial de configuração

O arquivo congelado para a rodada atual é:

```text
experiments/config/deepseek_v4_flash.json
```

Se esse arquivo mudar antes ou durante a coleta oficial, a mudança precisa ser registrada explicitamente.

## Prompt padrão

- Arquivo do prompt: `experiments/prompts/test_generation_prompt_template.md`
- O mesmo prompt-base deve ser usado em todas as execuções oficiais da mesma rodada.
- Cada chamada deve ser independente.
- O modelo não deve receber histórico de chamadas anteriores.

## Regra sobre edição dos testes gerados

- O teste gerado não deve ser editado manualmente durante a coleta oficial.
- A resposta bruta da LLM deve ser salva antes de qualquer extração.
- A extração do código para `test_generated.py` deve ser mecânica.
- Não é permitido “consertar” logicamente um teste gerado para fazê-lo passar ou executar.

## Estrutura oficial de salvamento por execução

Cada execução real deve salvar artefatos em:

```text
experiments/generated_tests/FXX/run_YY/
```

Arquivos obrigatórios:

- `system_prompt.txt`
- `prompt.txt`
- `request.json`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `status.json`

## Manifesto geral de geração

Cada tentativa de geração real deve registrar uma linha em:

```text
experiments/generated_tests/manifest.csv
```

Campos esperados:

- `function_id`
- `function_name`
- `run_id`
- `provider`
- `model`
- `temperature`
- `top_p`
- `max_tokens`
- `timestamp_utc`
- `status`
- `syntax_valid`
- `prompt_hash`
- `response_hash`
- `output_path`
- `error_summary`
- `input_tokens`
- `output_tokens`
- `total_tokens`

## Critérios para classificar uma tentativa de geração

### Execução válida

Uma tentativa é válida para análise quando:

- a chamada real foi feita com a configuração oficial;
- existe `raw_response.txt`;
- existe `test_generated.py` correspondente;
- existe `metadata.json` com hashes e parâmetros;
- o status não é placeholder nem erro estrutural.

### Execução inválida

Uma tentativa deve ser tratada como inválida quando:

- houve edição manual não documentada;
- o vínculo entre resposta bruta e teste salvo foi perdido;
- a configuração usada não corresponde à rodada oficial;
- o código salvo não representa a resposta recebida.

### Execução placeholder

Uma execução é apenas placeholder quando:

- a pasta existe só para manter a estrutura;
- ainda não houve chamada real à LLM;
- o `test_generated.py` ainda contém apenas marcador estrutural.

### Status registrados em `status.json`

Os estados oficiais são:

- `not_generated`
- `generated_syntax_valid`
- `generated_syntax_invalid`
- `api_error`

O estado `generated_syntax_valid` significa apenas que o código extraído passou na validação sintática. Ele não implica aprovação na implementação correta nem detecção confiável de defeito.

## Runner experimental

O script:

```bash
python scripts/run_generated_tests.py
```

deve executar cada suíte real contra:

- a implementação correta;
- `BUG01`;
- `BUG02`;
- `BUG03`.

O runner não deve tratar placeholder como dado real e deve registrar de forma controlada:

- teste ausente;
- teste placeholder;
- teste com sintaxe inválida;
- erro de API em geração anterior.

Na leitura metodológica do CSV bruto:

- `bug_failure` indica falha contra a versão defeituosa;
- `correct_passed_for_same_suite` indica que a mesma suíte passou na correta;
- `reliable_defect_detection` indica falha no bug e aprovação na correta;
- `false_positive` indica falha na correta;
- `contaminated_bug_failure` indica falha no bug com contaminação pela falha na correta.

## Resultados experimentais

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

## Métricas registradas

As métricas principais incluem:

- executabilidade;
- taxa de aprovação na implementação correta;
- falha bruta em versão defeituosa (`defect_detection_rate_raw`);
- detecção confiável de defeito (`reliable_defect_detection_rate`);
- taxa de falso positivo (`false_positive_rate`);
- contagem de falhas contaminadas (`contaminated_bug_failure_count`);
- número de testes coletados;
- número de `asserts`, quando medido;
- número de linhas do teste;
- número de funções `test_*`;
- indicação de importação de `tests.fixtures`;
- indicação de importação apenas de `ise26.targets`;
- variação entre execuções;
- quantidade de falhas por função;
- observações qualitativas.

## Limitações que devem ser registradas

- teste ausente;
- placeholder;
- erro de API;
- sintaxe inválida;
- extração mecânica sem teste executável;
- incompatibilidade de ambiente;
- ambiguidade do prompt;
- alteração indevida de configuração;
- edição manual indevida.
- placeholder estrutural;
- suíte que falha na correta e, por isso, não deve ser contada como detecção confiável.

## Procedimento experimental recomendado

1. Rodar `python -m pytest`.
2. Revisar este protocolo.
3. Configurar `.env` local com `DEEPSEEK_API_KEY`.
4. Rodar `python scripts/generate_llm_tests.py --dry-run`.
5. Confirmar função, execução e quantidade de chamadas planejadas.
6. Rodar `python scripts/generate_llm_tests.py --execute` apenas quando a rodada oficial começar, sem combinar `--dry-run` e `--execute`.
7. Rodar `python scripts/run_generated_tests.py`.
8. Rodar `python scripts/summarize_results.py`.
9. Registrar observações e limitações.

## Integridade dos dados

- Não inventar testes gerados por LLM.
- Não inventar resultados experimentais.
- Não misturar testes internos com testes gerados.
- Não mudar o prompt no meio da rodada oficial.
- Não mudar a configuração do modelo no meio da rodada oficial.
- Não apagar artefatos sem registrar.
- Não registrar a chave da API em arquivos do repositório.

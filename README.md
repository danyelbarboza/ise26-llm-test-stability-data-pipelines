# ISE26 - Avaliação de Testes Gerados por LLMs para Pipelines de Dados

## Visão geral

O repositório `ise26-llm-test-stability-data-pipelines` apoia um experimento acadêmico sobre a estabilidade de testes automatizados gerados por LLMs para funções de transformação de dados em Python.

O projeto tem duas trilhas experimentais:

- **`exp_6_functions`**: baseline histórica com 6 funções, já executada oficialmente para `deepseek-v4-flash` e `deepseek-v4-pro`;
- **`exp_10_functions`**: expansão com 10 funções, já executada oficialmente para `deepseek-v4-flash` e `deepseek-v4-pro` sem sobrescrever os resultados antigos.

Na expansão `exp_10_functions`, cada modelo terá 50 suítes planejadas e 200 execuções-alvo.

Os artefatos oficiais do experimento histórico ficam em `results/by_model/`. Os artefatos oficiais da expansão de 10 funções ficam em `results/by_experiment/exp_10_functions/`.

## Objetivo do projeto

O objetivo é observar como suítes de teste geradas por LLM se comportam quando executadas contra:

- a implementação correta de cada função;
- três versões defeituosas intencionais da mesma função.

A métrica principal de detecção de defeitos é `reliable_defect_detection_rate`, porque ela só conta quando a mesma suíte passa na implementação correta e falha no bug.

## Como o experimento funciona

Fluxo resumido:

1. validar a base com `python -m pytest`;
2. montar o prompt padrão;
3. gerar uma suíte por função e por execução planejada;
4. salvar prompt, resposta bruta, código extraído, metadados e status;
5. executar a suíte contra a implementação correta e contra os bugs;
6. resumir os resultados por função, por run e no geral;
7. comparar modelos apenas quando ambos tiverem resultados oficiais reais do mesmo `experiment_id`.

Para evitar mistura de resultados:

- os artefatos de `deepseek-v4-flash` e `deepseek-v4-pro` ficam em pastas diferentes;
- `exp_6_functions` e `exp_10_functions` também ficam separados;
- placeholders não devem ser tratados como resultado experimental.

## Estrutura do repositório

```text
README.md
src/
  ise26/
    implementations/
    llm/
    metadata/
    targets.py
    experiment_paths.py
experiments/
  config/
    deepseek_v4_flash.json
    deepseek_v4_pro.json
    deepseek_v4_flash_10_functions.json
    deepseek_v4_pro_10_functions.json
  generated_tests/
    deepseek_v4_flash/
    deepseek_v4_pro/
    exp_10_functions/
  prompts/
  protocol.md
results/
  by_model/
  by_experiment/
paper_assets/
  tables/
  model_comparison/
  exp_10_functions/
scripts/
tests/
```

## Funções corretas

As funções corretas oficiais ficam em `src/ise26/implementations/correct.py`.

| ID | Função | Papel |
|---|---|---|
| F01 | `clean_customer_names` | Padroniza nomes de clientes |
| F02 | `deduplicate_events` | Remove eventos duplicados mantendo o mais recente |
| F03 | `calculate_monthly_revenue` | Calcula receita mensal |
| F04 | `join_customers_orders` | Faz junção entre clientes e pedidos |
| F05 | `validate_schema` | Valida schema lógico de um `DataFrame` |
| F06 | `classify_payment_status` | Classifica status de pagamento |
| F07 | `parse_order_items_json` | Expande itens de pedidos codificados em JSON |
| F08 | `calculate_conversion_rate` | Calcula taxa de conversão por canal |
| F09 | `cap_outliers_iqr` | Limita outliers com base em IQR |
| F10 | `standardize_currency_values` | Padroniza valores monetários textuais |

## Versões defeituosas

Cada função correta tem 3 versões defeituosas intencionais, totalizando 30 bugs.

| Função | Bugs intencionais |
|---|---|
| F01 | não tratar nulos; não remover acentos; não remover espaços extras |
| F02 | manter o primeiro evento; remover `event_id` nulo; ordenar timestamp como string |
| F03 | somar cancelados; não tratar valores inválidos como zero; agrupar por dia |
| F04 | usar `inner join`; não criar `record_status`; classificar incorretamente chaves nulas |
| F05 | ignorar ausências; ignorar erros de tipo; reprovar colunas extras |
| F06 | tratar vencimento como atraso; tratar `amount` zero como pendente; tratar `paid_date` inválido como ausência |
| F07 | manter só o primeiro item; somar em vez de multiplicar; emitir linha para JSON inválido |
| F08 | inverter a fórmula; não proteger divisão por zero; calcular taxa antes de agregar |
| F09 | usar média/desvio; trocar nulos por zero; sobrescrever a coluna original |
| F10 | interpretar separadores brasileiros errado; usar zero para inválidos; não tratar `R$` |

## Testes internos

Os testes internos ficam em `tests/` e servem para:

- validar as funções corretas;
- confirmar que os bugs continuam diferentes da referência;
- checar `ise26.targets`;
- validar o runner e os summaries em cenários sintéticos;
- garantir que a infraestrutura multi-modelo e multi-experimento não misture caminhos.

## Testes gerados por LLM

Os testes gerados pela LLM devem:

- importar apenas `ise26.targets`;
- criar seus próprios `DataFrame`s sintéticos dentro de `test_generated.py`;
- não usar `tests/fixtures.py`;
- não importar `ise26.implementations` diretamente.

`tests/fixtures.py` é exclusivo dos testes internos.

## Resultados

Há dois tipos de organização de saída:

- `results/by_model/<modelo>/...`: baseline histórica de 6 funções;
- `results/by_experiment/exp_10_functions/by_model/<modelo>/...`: resultados oficiais da expansão de 10 funções.

Os resultados comparativos ficam em:

- `paper_assets/model_comparison/`: comparação histórica da baseline de 6 funções;
- `paper_assets/exp_10_functions/model_comparison/`: comparação oficial da expansão de 10 funções entre Flash e Pro.

## Como instalar

```bash
pip install -r requirements.txt
```

## Como rodar os testes

```bash
python -m pytest
```

No Windows, este é o comando recomendado.

## Como rodar o experimento

### Baseline histórica de 6 funções

Geração em modo seguro:

```bash
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_flash.json
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_pro.json
```

Runner e summaries:

```bash
python scripts/run_generated_tests.py --model deepseek_v4_flash
python scripts/summarize_results.py --model deepseek_v4_flash
python scripts/run_generated_tests.py --model deepseek_v4_pro
python scripts/summarize_results.py --model deepseek_v4_pro
python scripts/compare_model_results.py
```

### Expansão de 10 funções

Geração em modo seguro:

```bash
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_10_functions --config experiments/config/deepseek_v4_flash_10_functions.json
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_10_functions --config experiments/config/deepseek_v4_pro_10_functions.json
```

Execução e resumo da expansão:

```bash
python scripts/run_generated_tests.py --experiment-id exp_10_functions --model deepseek_v4_flash
python scripts/summarize_results.py --experiment-id exp_10_functions --model deepseek_v4_flash
python scripts/run_generated_tests.py --experiment-id exp_10_functions --model deepseek_v4_pro
python scripts/summarize_results.py --experiment-id exp_10_functions --model deepseek_v4_pro
python scripts/compare_model_results.py --experiment-id exp_10_functions
```

O comando de geração real só deve ser usado com `--execute` e confirmação explícita.

## Como interpretar os arquivos gerados

- `raw/`: linhas detalhadas de cada execução-alvo;
- `summary/`: agregações por função, por run e no geral;
- `reports/`: relatórios em Markdown para leitura humana;
- `paper_assets/`: tabelas e resumos prontos para o artigo.

Em especial:

- `bug_failure_rate` mostra falha bruta contra o bug;
- `reliable_defect_detection_rate` mostra detecção confiável;
- `false_positive_rate` mostra quando a suíte falha na correta;
- `contaminated_bug_failure_rate` mostra quando a falha no bug veio contaminada por falha na correta;
- `defect_detection_rate_raw` é auxiliar e não deve ser usada sozinha.

## O que não fazer

- não inventar teste gerado por LLM;
- não inventar resultado experimental;
- não alterar função correta sem atualizar testes, metadados e documentação;
- não corrigir bugs intencionais;
- não mudar o prompt oficial no meio de uma rodada;
- não apagar CSVs sem registrar;
- não misturar teste manual com teste gerado por LLM;
- não comparar modelos usando placeholders.

## Guia rápido para quem está começando

- Python é a linguagem principal do projeto;
- Pandas é a biblioteca usada para trabalhar com `DataFrames`;
- Pytest executa os testes do repositório;
- função correta é a implementação de referência;
- função defeituosa é uma variante intencionalmente errada;
- teste gerado por LLM é a suíte produzida pela IA para avaliar as funções;
- se você está começando, leia o protocolo e rode `python -m pytest` antes de mexer nos scripts;
- evite alterar `src/ise26/implementations/`, `src/ise26/metadata/`, `experiments/protocol.md` e os diretórios oficiais de resultado sem orientação.

## Fluxo recomendado de trabalho

1. instalar dependências;
2. rodar os testes internos;
3. ler o protocolo experimental;
4. gerar testes com a LLM usando o prompt padrão;
5. salvar cada execução na pasta correta do modelo e do experimento;
6. rodar o runner;
7. gerar os resumos;
8. analisar os resultados;
9. comparar modelos apenas quando ambos estiverem completos e no mesmo `experiment_id`.

## Próximos passos

O próximo passo é analisar os resultados oficiais da expansão `exp_10_functions` com Flash e Pro, sem misturar com a baseline histórica de 6 funções.

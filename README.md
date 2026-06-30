# ISE26 - Avaliacao de Testes Gerados por LLMs para Pipelines de Dados

## Visao geral

O repositorio `ise26-llm-test-stability-data-pipelines` apoia um experimento academico sobre a estabilidade de testes automatizados gerados por LLMs para funcoes de transformacao de dados em Python.

O projeto tem tres recortes historicos:

- `exp_6_functions`: baseline historica usada como validacao interna;
- `exp_10_functions`: expansao intermediaria usada como validacao interna e hoje tratada como `deprecated`;
- `exp_final_10_functions`: experimento final do artigo, baseado na base corrigida das 10 funcoes.

Os resultados antigos continuam versionados para rastreabilidade, mas nao devem ser usados como resultado principal do artigo.

## Objetivo do projeto

O objetivo e observar como suites de teste geradas por LLM se comportam quando executadas contra:

- a implementacao correta de cada funcao;
- tres versoes defeituosas intencionais da mesma funcao.

A metrica principal e `reliable_defect_detection_rate`, porque ela so conta quando a mesma suite passa na implementacao correta e falha no bug.

## Como o experimento funciona

A rodada final usa 10 funcoes, 2 modelos e 5 execucoes por funcao.

- 10 funcoes corretas;
- 30 bugs intencionais;
- 5 runs por funcao;
- 50 chamadas por modelo;
- 100 chamadas planejadas no total;
- 200 execucoes-alvo por modelo;
- 400 execucoes-alvo no total;
- 50 placeholders por modelo no estado inicial;
- 100 placeholders no total antes da execucao oficial.

Os testes gerados pela LLM devem importar apenas `ise26.targets`. O modulo `ise26.targets` usa a variavel de ambiente `ISE26_TARGET_MODULE` para escolher a implementacao alvo sem alterar o arquivo do teste.

## Estrutura do repositorio

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
  generated_tests/
  prompts/
  protocol.md
results/
  by_model/
  by_experiment/
paper_assets/
  tables/
  model_comparison/
  exp_final_10_functions/
scripts/
tests/
```

## Funcoes corretas

As 10 funcoes corretas oficiais ficam em `src/ise26/implementations/correct.py`.

| ID | Funcao | Papel |
|---|---|---|
| F01 | `clean_customer_names` | Padroniza nomes de clientes |
| F02 | `deduplicate_events` | Remove eventos duplicados mantendo o mais recente |
| F03 | `calculate_monthly_revenue` | Calcula receita mensal |
| F04 | `join_customers_orders` | Faz jun??o deterministica entre clientes e pedidos |
| F05 | `validate_schema` | Valida schema logico de um `DataFrame` |
| F06 | `classify_payment_status` | Classifica status de pagamento |
| F07 | `parse_order_items_json` | Expande itens de pedidos codificados em JSON |
| F08 | `calculate_conversion_rate` | Calcula taxa de conversao por canal |
| F09 | `cap_outliers_iqr` | Limita outliers com base em IQR |
| F10 | `standardize_currency_values` | Padroniza valores monetarios textuais |

## Versoes defeituosas

Cada funcao correta tem 3 versoes defeituosas intencionais, totalizando 30 bugs.

| Funcao | Bugs intencionais |
|---|---|
| F01 | nao tratar nulos; nao remover acentos; nao remover espacos extras |
| F02 | manter o primeiro evento; remover `event_id` nulo; ordenar timestamp como string |
| F03 | somar cancelados; nao tratar invalidos como zero; agrupar por dia |
| F04 | usar `inner join`; nao criar `record_status`; classificar incorretamente chaves nulas |
| F05 | ignorar ausencias; ignorar erros de tipo; reprovar colunas extras |
| F06 | tratar vencimento como atraso; tratar `amount` zero como pendente; tratar `paid_date` invalido como ausente |
| F07 | manter so o primeiro item; somar em vez de multiplicar; emitir linha para JSON invalido |
| F08 | inverter a formula; nao proteger divisao por zero; calcular antes de agregar |
| F09 | usar media/desvio; trocar nulos por zero; sobrescrever a coluna original |
| F10 | interpretar separadores brasileiros errado; usar zero para invalidos; nao remover `R$` e espacos |

## Testes internos

Os testes internos ficam em `tests/` e servem para:

- validar as funcoes corretas;
- confirmar que os bugs continuam diferentes da referencia;
- checar `ise26.targets`;
- validar runner, summaries e comparador em cenarios sinteticos;
- garantir que a infraestrutura nao misture modelos nem experimentos.

## Testes gerados por LLM

Os testes gerados pela LLM devem:

- importar apenas `ise26.targets`;
- criar seus proprios `DataFrame`s sinteticos dentro de `test_generated.py`;
- nao usar `tests/fixtures.py`;
- nao importar `ise26.implementations` diretamente;
- nao editar manualmente o codigo gerado.

`tests/fixtures.py` e exclusivo dos testes internos.

## Resultados

Existem tres trilhas de resultado:

- `results/by_model/`: baseline historica de 6 funcoes, mantida apenas para rastreabilidade;
- `results/by_experiment/exp_10_functions/`: expansao intermediaria, hoje tratada como `deprecated`;
- `results/by_experiment/exp_final_10_functions/`: resultados oficiais do artigo.

Os resultados comparativos oficiais da rodada final ficam em `paper_assets/exp_final_10_functions/model_comparison/`.

## Como instalar

```bash
pip install -r requirements.txt
```

## Como rodar os testes

```bash
python -m pytest
```

No Windows, este e o comando recomendado.

## Como rodar a preparacao e o experimento final

### Preparacao segura

```bash
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_flash_final_10_functions.json
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_pro_final_10_functions.json
python scripts/run_generated_tests.py --experiment-id exp_final_10_functions --model deepseek_v4_flash
python scripts/run_generated_tests.py --experiment-id exp_final_10_functions --model deepseek_v4_pro
python scripts/summarize_results.py --experiment-id exp_final_10_functions --model deepseek_v4_flash
python scripts/summarize_results.py --experiment-id exp_final_10_functions --model deepseek_v4_pro
python scripts/compare_model_results.py --experiment-id exp_final_10_functions
```

### Execucao oficial

A execucao oficial so deve ser feita com `--execute` e confirmacao explicita.

## Como interpretar os arquivos gerados

- `raw/`: linhas detalhadas de cada execucao-alvo;
- `summary/`: agregacoes por funcao, por run e no geral;
- `reports/`: relatorios em Markdown para leitura humana;
- `paper_assets/`: tabelas, resumos e comparacao final para o artigo.

Em especial:

- `bug_failure_rate` mostra falha bruta contra o bug;
- `reliable_defect_detection_rate` mostra detecao confiavel;
- `false_positive_rate` mostra quando a suite falha na correta;
- `contaminated_bug_failure_rate` mostra quando a falha no bug veio contaminada por falha na correta;
- `defect_detection_rate_raw` e auxiliar e nao deve ser usada sozinha.

## Guia rapido para quem esta comecando

- Python e a linguagem principal do projeto;
- Pandas e a biblioteca usada para trabalhar com `DataFrames`;
- Pytest executa os testes do repositorio;
- funcao correta e a implementacao de referencia;
- funcao defeituosa e uma variante intencionalmente errada;
- teste gerado por LLM e a suite produzida pela IA para avaliar as funcoes;
- se voce esta comecando, leia o protocolo e rode `python -m pytest` antes de mexer nos scripts;
- evite alterar `src/ise26/implementations/`, `src/ise26/metadata/`, `experiments/protocol.md` e os diretorios oficiais de resultado sem orientacao.

## Fluxo recomendado de trabalho

1. instalar dependencias;
2. rodar os testes internos;
3. ler o protocolo experimental;
4. gerar testes com a LLM usando o prompt padrao;
5. salvar cada execucao na pasta correta do modelo e do experimento;
6. rodar o runner;
7. gerar os resumos;
8. analisar os resultados;
9. comparar modelos apenas quando ambos estiverem completos e no mesmo `experiment_id`.

## O que nao fazer

- nao inventar teste gerado por LLM;
- nao inventar resultado experimental;
- nao alterar funcao correta sem atualizar testes, metadados e documentacao;
- nao corrigir bugs intencionais;
- nao mudar o prompt oficial no meio de uma rodada;
- nao apagar CSVs sem registrar;
- nao misturar teste manual com teste gerado por LLM;
- nao comparar modelos usando placeholders;
- nao misturar resultados historicos com o experimento final.

## Proximos passos

O proximo passo e executar a rodada final `exp_final_10_functions` com Flash e Pro, sem misturar com os resultados historicos nem com os experimentos de validacao interna.

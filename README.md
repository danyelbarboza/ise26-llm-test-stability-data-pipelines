# ISE26 - Avaliacao de Testes Gerados por LLMs para Pipelines de Dados

## Visao geral

O repositório `ise26-llm-test-stability-data-pipelines` apoia um estudo acadêmico sobre a estabilidade de testes automatizados gerados por LLMs para funções de transformação de dados em Python.

O projeto agora está organizado para comparar mais de um modelo de geração. A execução oficial concluída com `deepseek-v4-flash` já está preservada em pastas próprias. A preparação para `deepseek-v4-pro` também já existe, mas ainda sem execução oficial.

## Objetivo do projeto

O objetivo é observar como suítes de teste geradas por LLM se comportam quando executadas contra:

- a implementação correta de cada função;
- três versões defeituosas intencionais da mesma função.

A métrica principal para detecção de defeitos é `reliable_defect_detection_rate`, porque ela exige que a mesma suíte passe na implementação correta e falhe no bug.

## Como o experimento funciona

O fluxo oficial é:

1. validar a base com `python -m pytest`;
2. montar o prompt padrão;
3. gerar uma suíte por função e por execução planejada;
4. salvar prompt, resposta bruta, código extraído, metadados e status;
5. executar a suíte contra a implementação correta e contra os bugs;
6. resumir os resultados por função, por run e no geral;
7. analisar apenas resultados oficiais, sem misturar placeholders nem rascunhos.

## Estrutura do repositório

```text
README.md
src/
  ise26/
    implementations/
    llm/
    metadata/
    targets.py
experiments/
  config/
  generated_tests/
    deepseek_v4_flash/
    deepseek_v4_pro/
  prompts/
  protocol.md
results/
  by_model/
paper_assets/
  tables/
  model_comparison/
scripts/
tests/
```

## Funções corretas

As 6 funções corretas oficiais ficam em `src/ise26/implementations/correct.py`:

| ID | Função | Papel |
|---|---|---|
| F01 | `clean_customer_names` | Padroniza nomes de clientes |
| F02 | `deduplicate_events` | Remove eventos duplicados mantendo o mais recente |
| F03 | `calculate_monthly_revenue` | Calcula receita mensal |
| F04 | `join_customers_orders` | Faz junção entre clientes e pedidos |
| F05 | `validate_schema` | Valida schema lógico de um `DataFrame` |
| F06 | `classify_payment_status` | Classifica status de pagamento |

## Versoes defeituosas

Cada função correta tem 3 versões defeituosas intencionais, totalizando 18 bugs.

| Função | Bugs |
|---|---|
| F01 | não tratar nulos; não remover acentos; não remover espaços extras |
| F02 | manter o primeiro registro; remover `event_id` nulo; ordenar timestamp como string |
| F03 | somar cancelados; não tratar valores inválidos como zero; agrupar por dia |
| F04 | usar `inner join`; não criar `record_status`; classificar incorretamente chaves nulas |
| F05 | ignorar ausências; ignorar erros de tipo; reprovar colunas extras |
| F06 | tratar vencimento como atraso; tratar `amount` zero como pendente; tratar `paid_date` inválido como pendente/ausente |

## Multi-modelo

O repositório agora separa os artefatos por modelo:

- Flash oficial: `experiments/generated_tests/deepseek_v4_flash/` e `results/by_model/deepseek_v4_flash/`
- Pro preparado: `experiments/generated_tests/deepseek_v4_pro/` e `results/by_model/deepseek_v4_pro/`

Os resultados comparativos entre modelos devem ser colocados em `paper_assets/model_comparison/` depois que ambos tiverem execução oficial.
O comparador oficial fica em `scripts/compare_model_results.py` e só deve produzir saída quando Flash e Pro tiverem resultados oficiais reais.

## Testes internos

Os testes internos ficam em `tests/` e servem para validar a base do repositório, os helpers da infraestrutura e a lógica metodológica dos resumos.

Eles não substituem os testes gerados por LLM e não devem ser tratados como dado experimental.

## Testes gerados por LLM

Os testes gerados pela LLM devem importar apenas `ise26.targets` e devem criar seus próprios dados sintéticos dentro de `test_generated.py`.

Não use `tests/fixtures.py` nos testes gerados. As fixtures são exclusivas dos testes internos.

## Resultados

Os resultados oficiais do Flash ficam em:

- `results/by_model/deepseek_v4_flash/raw/`
- `results/by_model/deepseek_v4_flash/summary/`
- `results/by_model/deepseek_v4_flash/reports/`

Os resultados do Pro, quando existirem, ficarão nas pastas equivalentes.

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

Geração em modo seguro:

```bash
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_flash.json
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_pro.json
```

Execução do runner e dos resumos por modelo:

```bash
python scripts/run_generated_tests.py --model deepseek_v4_flash
python scripts/summarize_results.py --model deepseek_v4_flash
```

Quando o Pro tiver execução oficial, use `--model deepseek_v4_pro` nas mesmas etapas.
Depois que Flash e Pro estiverem prontos, rode `python scripts/compare_model_results.py` para gerar os arquivos comparativos.

## Como interpretar os arquivos gerados

- `raw/`: linhas detalhadas de cada execução-alvo;
- `summary/`: agregações por função, run e geral;
- `reports/`: relatórios em texto com leitura humana;
- `paper_assets/`: tabelas e resumos prontos para uso acadêmico.
- `paper_assets/model_comparison/`: comparação entre Flash e Pro, quando válida.

## Guia rapido para quem esta comecando

- Python aqui é a linguagem usada para implementar funções, scripts e testes.
- Pandas é a biblioteca usada para criar e analisar `DataFrames`.
- Pytest é a ferramenta que executa os testes.
- Função correta é a implementação oficial de referência.
- Função defeituosa é uma variante intencionalmente errada para medir detecção de bugs.
- Teste gerado por LLM é uma suíte escrita pela IA para avaliar as funções.
- Mesmo sem programar muito, você pode ler o protocolo, executar `python -m pytest` e revisar os CSVs de resultados.
- Evite mexer em `src/ise26/implementations/`, `src/ise26/metadata/`, `experiments/protocol.md` e nos diretórios oficiais de resultados sem orientação.

## Fluxo recomendado de trabalho

1. instalar dependências;
2. rodar os testes internos;
3. ler o protocolo experimental;
4. gerar testes com a LLM usando o prompt padrão;
5. salvar cada execução na pasta correta do modelo;
6. rodar o runner;
7. gerar os resumos;
8. analisar os resultados;
9. comparar modelos apenas quando ambos estiverem completos.

## O que nao fazer

- não inventar testes gerados por LLM;
- não inventar resultados;
- não alterar função correta depois que a execução oficial já começou;
- não corrigir bugs intencionais;
- não mudar o prompt oficial no meio da geração;
- não apagar CSVs sem registrar;
- não misturar teste manual com teste gerado por LLM;
- não comparar Pro com Flash usando placeholders.

## Proximos passos

O próximo passo metodológico é executar o fluxo oficial do Pro com a mesma configuração do Flash, preservando o isolamento por modelo e comparando apenas resultados oficiais.

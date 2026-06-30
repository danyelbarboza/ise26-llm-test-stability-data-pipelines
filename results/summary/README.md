# Pasta `results/summary`

Esta pasta raiz existe por compatibilidade e documentacao. Os resumos oficiais agora ficam nas pastas especificas de modelo e de experimento.

## Arquivos esperados

- `summary_by_function.csv`
- `summary_by_run.csv`
- `summary_overall.csv`

## Onde ficam os arquivos oficiais

- baseline historica de 6 funcoes:
  - `results/by_model/deepseek_v4_flash/summary/`
  - `results/by_model/deepseek_v4_pro/summary/`
- expansao intermediaria de 10 funcoes:
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_flash/summary/`
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_pro/summary/`
- rodada final do artigo:
  - `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_flash/summary/`
  - `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_pro/summary/`

## O que os resumos mostram

- `summary_by_function.csv`: visao consolidada por funcao;
- `summary_by_run.csv`: visao consolidada por funcao e execucao;
- `summary_overall.csv`: visao geral do modelo e do experimento.

## Metricas principais

- `reliable_defect_detection_rate` e a metrica principal;
- `defect_detection_rate_raw` e auxiliar e nao deve ser usada sozinha;
- `false_positive_rate` e `contaminated_bug_failure_rate` ajudam a interpretar o resultado.

## Atencao

Os resumos so tem valor experimental quando sao derivados de suites reais e nao de placeholders. Na rodada final, os resumos oficiais devem refletir apenas os resultados reais do Flash e do Pro.

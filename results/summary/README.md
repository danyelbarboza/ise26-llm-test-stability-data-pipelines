# Pasta `results/summary`

Esta pasta raiz existe por compatibilidade e documentação. Os resumos oficiais agora ficam nas pastas específicas de modelo e de experimento.

## Arquivos esperados

- `summary_by_function.csv`
- `summary_by_run.csv`
- `summary_overall.csv`

## Onde ficam os arquivos oficiais

- baseline histórica de 6 funções:
  - `results/by_model/deepseek_v4_flash/summary/`
  - `results/by_model/deepseek_v4_pro/summary/`
- expansão de 10 funções:
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_flash/summary/`
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_pro/summary/`

## O que os resumos mostram

- `summary_by_function.csv`: visão consolidada por função;
- `summary_by_run.csv`: visão consolidada por função e execução;
- `summary_overall.csv`: visão geral do modelo e do experimento.

## Métricas principais

- `reliable_defect_detection_rate` é a métrica principal;
- `defect_detection_rate_raw` é auxiliar e não deve ser usada sozinha;
- `false_positive_rate` e `contaminated_bug_failure_rate` ajudam a interpretar o resultado.

## Atenção

Os resumos só têm valor experimental quando são derivados de suítes reais e não de placeholders. Na expansão `exp_10_functions`, os resumos oficiais já refletem os resultados reais do Flash e do Pro.

# Pasta `results/summary`

Esta pasta raiz é mantida apenas para compatibilidade e documentação. Os resumos oficiais agora ficam em `results/by_model/<modelo>/summary/`.

## Arquivos esperados

- `summary_by_function.csv`
- `summary_by_run.csv`
- `summary_overall.csv`

## O que os resumos mostram

- `summary_by_function.csv`: visão consolidada por função;
- `summary_by_run.csv`: visão consolidada por função e execução;
- `summary_overall.csv`: visão geral do modelo.

## Métricas principais

- `reliable_defect_detection_rate` é a métrica principal;
- `defect_detection_rate_raw` é auxiliar e não deve ser usada sozinha;
- `false_positive_rate` e `contaminated_bug_failure_rate` ajudam a interpretar o resultado.

## Atenção

Os resumos só têm valor experimental quando são derivados de suítes reais e não de placeholders.

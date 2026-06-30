# Relat?rio t?cnico oficial - deepseek_v4_flash

Este relat?rio foi gerado apenas a partir dos CSVs oficiais da expans?o `exp_10_functions`.

## Metadados

| Campo | Valor |
|---|---:|
| Provedor | DeepSeek |
| Modelo | deepseek_v4_flash |
| Intervalo UTC da gera??o | 2026-06-30T12:05:14Z a 2026-06-30T12:21:05Z |
| Temperatura | 0.7 |
| Top-p | 1 |
| Max tokens | 4096 |
| Total de fun??es | 10 |
| Runs por fun??o | 5 |
| Su?tes planejadas | 50 |
| Su?tes geradas | 50 |
| Su?tes execut?veis | 45 |
| Placeholders restantes | 0 |
| API errors | 0 |
| Sintaxe v?lida | 45 |
| Sintaxe inv?lida | 4 |
| Runs vazios | 1 |
| Execu??es-alvo | 200 |
| Execu??es reais | 180 |
| Execu??es puladas | 20 |
| Total de testes coletados | 2668 |
| Total de asserts aproximados | 2588 |

## M?tricas principais

| M?trica | Valor |
|---|---:|
| correct_pass_rate | 0.266667 |
| false_positive_rate | 0.733333 |
| bug_failure_rate | 0.992593 |
| defect_detection_rate_raw | 0.992593 |
| reliable_defect_detection_rate | 0.259259 |
| contaminated_bug_failure_rate | 0.733333 |

## M?tricas de c?digo gerado

| M?trica | Valor |
|---|---:|
| M?dia de linhas geradas | 183.044444 |
| M?dia de fun??es de teste | 14.244444 |
| M?dia de asserts | 14.377778 |
| Total de linhas geradas | 32948 |
| Total de fun??es de teste geradas | 2564 |
| Rate de importa??o de `tests.fixtures` | 0 |
| Rate de importa??o apenas de `ise26.targets` | 0.9 |

## Melhores fun??es

| function_id | function_name | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate | real_suite_count |
|---|---|---:|---:|---:|---:|---:|
| F08 | calculate_conversion_rate | 0.6 | 0.6 | 0.4 | 0.4 | 5 |
| F04 | join_customers_orders | 0.5 | 0.5 | 0.5 | 0.5 | 4 |
| F05 | validate_schema | 0.5 | 0.5 | 0.5 | 0.5 | 4 |

## Piores fun??es

| function_id | function_name | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate | real_suite_count |
|---|---|---:|---:|---:|---:|---:|
| F03 | calculate_monthly_revenue | 0 | 0 | 1 | 1 | 5 |
| F07 | parse_order_items_json | 0 | 0 | 1 | 1 | 5 |
| F09 | cap_outliers_iqr | 0 | 0 | 1 | 1 | 5 |

## Runs problem?ticas

| function_id | function_name | run_id | suite_generation_status | real_target_executions | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| F04 | join_customers_orders | run_02 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F05 | validate_schema | run_02 | empty | 0 | 0 | 0 | 0 | 0 |
| F06 | classify_payment_status | run_04 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F10 | standardize_currency_values | run_02 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F10 | standardize_currency_values | run_04 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |

## Observa??es metodol?gicas

- `reliable_defect_detection_rate` ? a m?trica principal para interpretar a detec??o de defeitos neste modelo.
- `defect_detection_rate_raw` ? auxiliar e, sozinha, pode superestimar a qualidade porque n?o separa falsos positivos.
- Nenhum teste gerado por este modelo importou `tests.fixtures`; a taxa observada foi 0.
- A taxa de importa??o apenas de `ise26.targets` foi 1.
- Su?tes com `suite_generation_status` diferente de `ready` foram tratadas separadamente como casos problem?ticos.
- Os n?meros aqui foram derivados dos CSVs oficiais e n?o foram inventados manualmente.

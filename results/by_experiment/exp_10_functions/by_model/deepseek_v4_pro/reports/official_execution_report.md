# Relat?rio t?cnico oficial - deepseek_v4_pro

Este relat?rio foi gerado apenas a partir dos CSVs oficiais da expans?o `exp_10_functions`.

## Metadados

| Campo | Valor |
|---|---:|
| Provedor | DeepSeek |
| Modelo | deepseek_v4_pro |
| Intervalo UTC da gera??o | 2026-06-30T12:26:13Z a 2026-06-30T12:58:27Z |
| Temperatura | 0.7 |
| Top-p | 1 |
| Max tokens | 4096 |
| Total de fun??es | 10 |
| Runs por fun??o | 5 |
| Su?tes planejadas | 50 |
| Su?tes geradas | 50 |
| Su?tes execut?veis | 44 |
| Placeholders restantes | 0 |
| API errors | 0 |
| Sintaxe v?lida | 44 |
| Sintaxe inv?lida | 6 |
| Runs vazios | 0 |
| Execu??es-alvo | 200 |
| Execu??es reais | 176 |
| Execu??es puladas | 24 |
| Total de testes coletados | 2604 |
| Total de asserts aproximados | 3344 |

## M?tricas principais

| M?trica | Valor |
|---|---:|
| correct_pass_rate | 0.272727 |
| false_positive_rate | 0.727273 |
| bug_failure_rate | 1 |
| defect_detection_rate_raw | 1 |
| reliable_defect_detection_rate | 0.272727 |
| contaminated_bug_failure_rate | 0.727273 |

## M?tricas de c?digo gerado

| M?trica | Valor |
|---|---:|
| M?dia de linhas geradas | 184.727273 |
| M?dia de fun??es de teste | 14.590909 |
| M?dia de asserts | 19 |
| Total de linhas geradas | 32512 |
| Total de fun??es de teste geradas | 2568 |
| Rate de importa??o de `tests.fixtures` | 0 |
| Rate de importa??o apenas de `ise26.targets` | 0.88 |

## Melhores fun??es

| function_id | function_name | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate | real_suite_count |
|---|---|---:|---:|---:|---:|---:|
| F02 | deduplicate_events | 0.75 | 0.75 | 0.25 | 0.25 | 4 |
| F04 | join_customers_orders | 0.666667 | 0.666667 | 0.333333 | 0.333333 | 3 |
| F06 | classify_payment_status | 0.4 | 0.4 | 0.6 | 0.6 | 5 |

## Piores fun??es

| function_id | function_name | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate | real_suite_count |
|---|---|---:|---:|---:|---:|---:|
| F07 | parse_order_items_json | 0 | 0 | 1 | 1 | 5 |
| F08 | calculate_conversion_rate | 0 | 0 | 1 | 1 | 5 |
| F09 | cap_outliers_iqr | 0 | 0 | 1 | 1 | 4 |

## Runs problem?ticas

| function_id | function_name | run_id | suite_generation_status | real_target_executions | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate |
|---|---|---|---|---:|---:|---:|---:|---:|
| F02 | deduplicate_events | run_03 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F04 | join_customers_orders | run_01 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F04 | join_customers_orders | run_02 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F05 | validate_schema | run_03 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F05 | validate_schema | run_04 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |
| F09 | cap_outliers_iqr | run_03 | syntax_invalid | 0 | 0 | 0 | 0 | 0 |

## Observa??es metodol?gicas

- `reliable_defect_detection_rate` ? a m?trica principal para interpretar a detec??o de defeitos neste modelo.
- `defect_detection_rate_raw` ? auxiliar e, sozinha, pode superestimar a qualidade porque n?o separa falsos positivos.
- Nenhum teste gerado por este modelo importou `tests.fixtures`; a taxa observada foi 0.
- A taxa de importa??o apenas de `ise26.targets` foi 1.
- Su?tes com `suite_generation_status` diferente de `ready` foram tratadas separadamente como casos problem?ticos.
- Os n?meros aqui foram derivados dos CSVs oficiais e n?o foram inventados manualmente.

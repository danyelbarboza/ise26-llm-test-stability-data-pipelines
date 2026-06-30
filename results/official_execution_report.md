# Relat?rio t?cnico da execu??o oficial DeepSeek

## Metadados da execu??o

- In?cio: `2026-06-30T01:41:20Z`
- Fim: `2026-06-30T01:53:19Z`
- Provedor: `DeepSeek`
- Modelo: `deepseek-v4-flash`
- Temperatura: `0.7`
- Top-p: `1.0`
- Max tokens: `4096`
- Fun??es: `6`
- Execu??es por fun??o: `5`
- Su?tes planejadas: `30`
- Su?tes geradas: `30`
- Su?tes reais execut?veis: `29`
- Placeholders restantes: `0`
- `api_error`: `0`
- Sintaxe v?lida: `29`
- Sintaxe inv?lida: `1`
- Execu??es-alvo: `120`
- Execu??es reais: `116`
- Execu??es puladas por sintaxe inv?lida: `4`
- Execu??es puladas por placeholder: `0`

## M?tricas principais

- `correct_pass_rate`: `41.38%`
- `false_positive_rate`: `58.62%`
- `bug_failure_rate`: `100.00%`
- `defect_detection_rate_raw`: `100.00%`
- `reliable_defect_detection_rate`: `41.38%`
- `contaminated_bug_failure_rate`: `58.62%`
- `failure_count`: `104`
- `bug_failure_count`: `87`
- `reliable_defect_detection_count`: `36`
- `false_positive_count`: `17`
- `contaminated_bug_failure_count`: `51`
- `correct_passed_for_same_suite_count`: `12`

## Contagem est?tica aproximada dos testes gerados

- Fun??es de teste geradas nas su?tes reais execut?veis: `1716`
- `asserts` aproximados nas su?tes reais execut?veis: `2428`
- Total de linhas de c?digo gerado nas su?tes reais execut?veis: `21560`
- `tests/fixtures.py` importado: `n?o`
- Importa apenas de `ise26.targets`: `sim`

## Interpreta??o metodol?gica

A m?trica principal para inferir detec??o de defeitos ? `reliable_defect_detection_rate`, porque ela exige que a mesma su?te passe na implementa??o correta e falhe em pelo menos um bug. A m?trica `defect_detection_rate_raw` fica registrada apenas como refer?ncia bruta, porque uma falha no bug sem passagem na correta pode representar falso positivo ou resultado contaminado.

## Melhores e piores fun??es

- Melhor fun??o em detec??o confi?vel: `F05` com `reliable_defect_detection_rate=0.80`
- Pior fun??o em detec??o confi?vel: `F03` com `reliable_defect_detection_rate=0.00`

### Resumo por fun??o

| Fun??o | Passagem correta | Detec??o confi?vel | Falso positivo | Falha contaminada |
| --- | ---: | ---: | ---: | ---: |
| F01 | 0.40 | 0.40 | 0.60 | 0.60 |
| F02 | 0.60 | 0.60 | 0.40 | 0.40 |
| F03 | 0.00 | 0.00 | 1.00 | 1.00 |
| F04 | 0.50 | 0.50 | 0.50 | 0.50 |
| F05 | 0.80 | 0.80 | 0.20 | 0.20 |
| F06 | 0.20 | 0.20 | 0.80 | 0.80 |

## Runs problem?ticas

- F01/run_01: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F01/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F01/run_04: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F02/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F02/run_04: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F03/run_01: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F03/run_02: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F03/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F03/run_04: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F03/run_05: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F04/run_02: status=syntax_invalid, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=0.00
- F04/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F04/run_05: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F05/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F06/run_01: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F06/run_02: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F06/run_03: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00
- F06/run_04: status=ready, correct_pass_rate=0.00, reliable_defect_detection_rate=0.00, false_positive_rate=1.00

## Observa??es metodol?gicas

- Nenhuma su?te oficial permaneceu como placeholder no conjunto gerado final.
- A execu??o oficial produziu 1 su?te com sintaxe inv?lida e 29 su?tes reais execut?veis.
- `reliable_defect_detection_rate` deve ser usada como m?trica principal na an?lise do artigo.
- A presen?a de falha em bug sem passagem na correta continua sendo classificada como falso positivo ou falha contaminada, n?o como detec??o confi?vel.
- N?o houve importa??o indevida de `tests.fixtures` nem de m?dulos fora de `ise26.targets`.

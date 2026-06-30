# Relatorio tecnico da execucao oficial DeepSeek

## Metadados da execucao

- Inicio: `2026-06-30T01:41:20Z`
- Fim: `2026-06-30T01:53:19Z`
- Provedor: `DeepSeek`
- Modelo: `deepseek-v4-flash`
- Temperatura: `0.7`
- Top-p: `1.0`
- Max tokens: `4096`
- Funcoes: `6`
- Execucoes por funcao: `5`
- Suites planejadas: `30`
- Suites geradas: `30`
- Suites reais executaveis: `29`
- Placeholders restantes: `0`
- `api_error`: `0`
- Sintaxe valida: `29`
- Sintaxe invalida: `1`
- Execucoes-alvo: `120`
- Execucoes reais: `116`
- Execucoes puladas por sintaxe invalida: `4`
- Execucoes puladas por placeholder: `0`

## Metricas principais

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

## Contagem estatica aproximada dos testes gerados

- Funcoes de teste geradas nas suites reais executaveis: `1716`
- `asserts` aproximados nas suites reais executaveis: `2428`
- Total de linhas de codigo gerado nas suites reais executaveis: `21560`
- `tests/fixtures.py` importado: `nao`
- Importa apenas de `ise26.targets`: `sim`

## Interpretacao metodologica

A metrica principal para inferir deteccao de defeitos e `reliable_defect_detection_rate`, porque ela exige que a mesma suite passe na implementacao correta e falhe em pelo menos um bug. A metrica `defect_detection_rate_raw` fica registrada apenas como referencia auxiliar, pois uma falha no bug sem passagem na correta pode representar falso positivo ou resultado contaminado.

## Melhores e piores funcoes

- Melhor funcao em deteccao confiavel: `F05` com `reliable_defect_detection_rate=0.80`
- Pior funcao em deteccao confiavel: `F03` com `reliable_defect_detection_rate=0.00`

### Resumo por funcao

| Funcao | Passagem correta | Deteccao confiavel | Falso positivo | Falha contaminada |
| --- | ---: | ---: | ---: | ---: |
| F01 | 0.40 | 0.40 | 0.60 | 0.60 |
| F02 | 0.60 | 0.60 | 0.40 | 0.40 |
| F03 | 0.00 | 0.00 | 1.00 | 1.00 |
| F04 | 0.50 | 0.50 | 0.50 | 0.50 |
| F05 | 0.80 | 0.80 | 0.20 | 0.20 |
| F06 | 0.20 | 0.20 | 0.80 | 0.80 |

## Runs problematicas

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

## Observacoes metodologicas

- Nenhuma suite oficial permaneceu como placeholder no conjunto gerado final.
- A execucao oficial produziu 1 suite com sintaxe invalida e 29 suites reais executaveis.
- `reliable_defect_detection_rate` deve ser usada como metrica principal na analise do artigo.
- A presenca de falha em bug sem passagem na correta continua sendo classificada como falso positivo ou falha contaminada, nao como deteccao confiavel.
- Nao houve importacao indevida de `tests.fixtures` nem de modulos fora de `ise26.targets`.

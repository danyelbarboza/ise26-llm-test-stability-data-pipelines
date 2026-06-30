# Relatorio oficial de execucao - deepseek_v4_flash

## Resumo executivo
O modelo `deepseek-v4-flash` foi executado no experimento final `exp_final_10_functions` como parte da rodada oficial do artigo. A geracao produziu 50 suites planejadas, com 49 suites reais e 1 suites com sintaxe invalida. A metrica principal continua sendo `reliable_defect_detection_rate`, e neste modelo ela ficou em 24.49%.

## Configuracao experimental
- Provedor: DeepSeek
- Modelo: `deepseek-v4-flash`
- Temperatura: 0.7
- Top-p: 1.0
- Max tokens: 4096
- Runs por função: 5
- Funções: 10
- Experimento: `exp_final_10_functions`
- Janela UTC da geração: 2026-06-30T18:07:13Z a 2026-06-30T18:24:29Z

## Resultado geral
- Chamadas planejadas: 50
- Chamadas executadas: 50
- Chamadas com sucesso: 50
- `api_error`: 0
- Suítes planejadas: 50
- Suítes geradas: 50
- Suítes executáveis: 49
- Sintaxe inválida: 1
- Runs vazios: 0
- Placeholders restantes: 0
- Execuções-alvo: 200
- Execuções reais: 196
- Execuções puladas: 4
- `correct_pass_rate`: 24.49%
- `false_positive_rate`: 75.51%
- `bug_failure_rate`: 100.00%
- `defect_detection_rate_raw`: 100.00%
- `reliable_defect_detection_rate`: 24.49%
- `contaminated_bug_failure_rate`: 75.51%
- `generated_line_count` total (runs ready): 9464
- `generated_test_function_count` total (runs ready): 776
- `generated_assert_count` total aproximado (runs ready): 975
- `imports_tests_fixtures_rate`: 0.00%
- `imports_only_ise26_targets_rate`: 100.00%

## Desempenho por funcao
| Funcao | Suites reais | Correct pass | Reliable defect detection | False positive | Contaminated bug failure |
| --- | --- | --- | --- | --- | --- |
| F01 | 5 | 0.00% | 0.00% | 100.00% | 100.00% |
| F02 | 5 | 20.00% | 20.00% | 80.00% | 80.00% |
| F03 | 5 | 80.00% | 80.00% | 20.00% | 20.00% |
| F04 | 5 | 0.00% | 0.00% | 100.00% | 100.00% |
| F05 | 5 | 40.00% | 40.00% | 60.00% | 60.00% |
| F06 | 4 | 75.00% | 75.00% | 25.00% | 25.00% |
| F07 | 5 | 20.00% | 20.00% | 80.00% | 80.00% |
| F08 | 5 | 20.00% | 20.00% | 80.00% | 80.00% |
| F09 | 5 | 0.00% | 0.00% | 100.00% | 100.00% |
| F10 | 5 | 0.00% | 0.00% | 100.00% | 100.00% |

## Runs problem?ticos
| Funcao | Run | Status | Linhas | Funcoes de teste | Asserts |
| --- | --- | --- | --- | --- | --- |
| F06 | run_05 | syntax_invalid | 0 | 0 | 0 |

## Funcoes com melhor e pior desempenho
- Melhor funcao por `reliable_defect_detection_rate`: F03 (80.00%)
- Pior funcao por `reliable_defect_detection_rate`: F01 (0.00%)

## Observacoes metodologicas
- `defect_detection_rate_raw` permaneceu em 100%, mas isso nao basta para afirmar detecao confiavel de defeito.
- A leitura principal deve continuar sendo `reliable_defect_detection_rate`, porque ela exige que a mesma suite passe na implementacao correta e falhe no bug.
- A taxa de uso de `tests.fixtures` permaneceu em 0%, e os testes gerados importaram apenas `ise26.targets`.
- As funcoes com `suite_generation_status` diferente de `ready` devem ser tratadas como dados experimentais invalidos para execucao de testes, nao como desempenho semantico dos modelos.

## Conclusao
O resultado oficial deste modelo e util para comparacao, mas deve ser interpretado junto com a taxa de sintaxe invalida e com a metrica principal de deteccao confiavel. Neste modelo, deepseek_v4_flash ficou com `reliable_defect_detection_rate` de 24.49%.

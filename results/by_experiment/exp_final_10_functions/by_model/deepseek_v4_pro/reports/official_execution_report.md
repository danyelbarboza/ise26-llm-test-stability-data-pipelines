# Relatorio oficial de execucao - deepseek_v4_pro

## Resumo executivo
O modelo `deepseek-v4-pro` foi executado no experimento final `exp_final_10_functions` como parte da rodada oficial do artigo. A geracao produziu 50 suites planejadas, com 30 suites reais e 15 suites com sintaxe invalida. A metrica principal continua sendo `reliable_defect_detection_rate`, e neste modelo ela ficou em 20.00%.

## Configuracao experimental
- Provedor: DeepSeek
- Modelo: `deepseek-v4-pro`
- Temperatura: 0.7
- Top-p: 1.0
- Max tokens: 4096
- Runs por função: 5
- Funções: 10
- Experimento: `exp_final_10_functions`
- Janela UTC da geração: 2026-06-30T18:32:12Z a 2026-06-30T18:59:28Z

## Resultado geral
- Chamadas planejadas: 50
- Chamadas executadas: 50
- Chamadas com sucesso: 50
- `api_error`: 0
- Suítes planejadas: 50
- Suítes geradas: 50
- Suítes executáveis: 30
- Sintaxe inválida: 15
- Runs vazios: 5
- Placeholders restantes: 0
- Execuções-alvo: 200
- Execuções reais: 120
- Execuções puladas: 80
- `correct_pass_rate`: 20.00%
- `false_positive_rate`: 80.00%
- `bug_failure_rate`: 100.00%
- `defect_detection_rate_raw`: 100.00%
- `reliable_defect_detection_rate`: 20.00%
- `contaminated_bug_failure_rate`: 80.00%
- `generated_line_count` total (runs ready): 4936
- `generated_test_function_count` total (runs ready): 439
- `generated_assert_count` total aproximado (runs ready): 752
- `imports_tests_fixtures_rate`: 0.00%
- `imports_only_ise26_targets_rate`: 100.00%

## Desempenho por funcao
| Funcao | Suites reais | Correct pass | Reliable defect detection | False positive | Contaminated bug failure |
| --- | --- | --- | --- | --- | --- |
| F01 | 3 | 0.00% | 0.00% | 100.00% | 100.00% |
| F02 | 4 | 0.00% | 0.00% | 100.00% | 100.00% |
| F03 | 3 | 33.33% | 33.33% | 66.67% | 66.67% |
| F04 | 0 | 0.00% | 0.00% | 0.00% | 0.00% |
| F05 | 4 | 75.00% | 75.00% | 25.00% | 25.00% |
| F06 | 2 | 0.00% | 0.00% | 100.00% | 100.00% |
| F07 | 2 | 0.00% | 0.00% | 100.00% | 100.00% |
| F08 | 5 | 40.00% | 40.00% | 60.00% | 60.00% |
| F09 | 3 | 0.00% | 0.00% | 100.00% | 100.00% |
| F10 | 4 | 0.00% | 0.00% | 100.00% | 100.00% |

## Runs problem?ticos
| Funcao | Run | Status | Linhas | Funcoes de teste | Asserts |
| --- | --- | --- | --- | --- | --- |
| F01 | run_02 | syntax_invalid | 0 | 0 | 0 |
| F01 | run_04 | syntax_invalid | 0 | 0 | 0 |
| F02 | run_04 | syntax_invalid | 0 | 0 | 0 |
| F03 | run_02 | syntax_invalid | 0 | 0 | 0 |
| F03 | run_05 | syntax_invalid | 0 | 0 | 0 |
| F04 | run_01 | syntax_invalid | 0 | 0 | 0 |
| F04 | run_02 | syntax_invalid | 0 | 0 | 0 |
| F04 | run_03 | syntax_invalid | 0 | 0 | 0 |
| F04 | run_04 | syntax_invalid | 0 | 0 | 0 |
| F04 | run_05 | empty | 0 | 0 | 0 |
| F05 | run_05 | syntax_invalid | 0 | 0 | 0 |
| F06 | run_03 | empty | 0 | 0 | 0 |
| F06 | run_04 | syntax_invalid | 0 | 0 | 0 |
| F06 | run_05 | empty | 0 | 0 | 0 |
| F07 | run_01 | empty | 0 | 0 | 0 |
| F07 | run_02 | syntax_invalid | 0 | 0 | 0 |
| F07 | run_05 | empty | 0 | 0 | 0 |
| F09 | run_04 | syntax_invalid | 0 | 0 | 0 |
| F09 | run_05 | syntax_invalid | 0 | 0 | 0 |
| F10 | run_03 | syntax_invalid | 0 | 0 | 0 |

## Funcoes com melhor e pior desempenho
- Melhor funcao por `reliable_defect_detection_rate`: F05 (75.00%)
- Pior funcao por `reliable_defect_detection_rate`: F01 (0.00%)

## Observacoes metodologicas
- `defect_detection_rate_raw` permaneceu em 100%, mas isso nao basta para afirmar detecao confiavel de defeito.
- A leitura principal deve continuar sendo `reliable_defect_detection_rate`, porque ela exige que a mesma suite passe na implementacao correta e falhe no bug.
- A taxa de uso de `tests.fixtures` permaneceu em 0%, e os testes gerados importaram apenas `ise26.targets`.
- As funcoes com `suite_generation_status` diferente de `ready` devem ser tratadas como dados experimentais invalidos para execucao de testes, nao como desempenho semantico dos modelos.

## Conclusao
O resultado oficial deste modelo e util para comparacao, mas deve ser interpretado junto com a taxa de sintaxe invalida e com a metrica principal de deteccao confiavel. Neste modelo, deepseek_v4_pro ficou com `reliable_defect_detection_rate` de 20.00%.

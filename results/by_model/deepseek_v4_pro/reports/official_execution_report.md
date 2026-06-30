# DeepSeek V4-Pro official execution report

## Execution metadata

| Field | Value |
| --- | --- |
| Execution window UTC | 2026-06-30T03:48:26Z to 2026-06-30T04:10:42Z |
| Latest generation timestamp UTC | 2026-06-30T04:10:42Z |
| Provider | DeepSeek |
| Model | deepseek-v4-pro |
| Temperature | 0.7 |
| Top-p | 1.0 |
| Max tokens | 4096 |
| Functions | 6 |
| Runs per function | 5 |
| Planned suites | 30 |
| Generated suites | 30 |
| Real suites | 22 |
| Syntax-invalid suites | 6 |
| Empty suites | 2 |
| Placeholders remaining | 0 |
| API errors | 0 |
| Target executions | 120 |
| Real target executions | 88 |

## Overall metrics

| Metric | Value |
| --- | --- |
| executability_rate | 100.00% |
| correct_pass_rate | 45.45% |
| false_positive_rate | 54.55% |
| bug_failure_rate | 95.45% |
| defect_detection_rate_raw | 95.45% |
| reliable_defect_detection_rate | 40.91% |
| contaminated_bug_failure_rate | 54.55% |
| failure_count | 75 |
| bug_failure_count | 63 |
| reliable_defect_detection_count | 27 |
| false_positive_count | 12 |
| contaminated_bug_failure_count | 36 |
| correct_passed_for_same_suite_count | 10 |
| suite_count | 30 |
| real_suite_count | 22 |
| placeholder_suite_count | 0 |
| target_executions | 120 |
| real_target_executions | 88 |
| placeholder_target_executions | 0 |
| correct_target_executions | 22 |
| bug_target_executions | 66 |

## Code generation metrics

| Metric | Value |
| --- | --- |
| generated_line_count_mean | 176.86 |
| generated_test_function_count_mean | 13.55 |
| generated_assert_count_mean | 17.77 |
| imports_tests_fixtures_rate | 0.00% |
| imports_only_ise26_targets_rate | 100.00% |

## Result by function

| function_id | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate | contaminated_bug_failure_rate | real_suite_count |
| --- | --- | --- | --- | --- | --- |
| F03 | 80.00% | 66.67% | 20.00% | 20.00% | 5 |
| F06 | 66.67% | 55.56% | 33.33% | 33.33% | 3 |
| F01 | 50.00% | 50.00% | 50.00% | 50.00% | 4 |
| F02 | 50.00% | 50.00% | 50.00% | 50.00% | 4 |
| F04 | 0.00% | 0.00% | 100.00% | 100.00% | 2 |
| F05 | 0.00% | 0.00% | 100.00% | 100.00% | 4 |

## Best and worst functions

- Best function by reliable_defect_detection_rate: `F03` with 66.67%.
- Worst functions by reliable_defect_detection_rate: `F04`, `F05` with 0.00%.

## Problematic runs

| function_id | run_id | correct_pass_rate | reliable_defect_detection_rate | false_positive_rate |
| --- | --- | --- | --- | --- |
| F01 | run_02 | 0.00% | 0.00% | 100.00% |
| F01 | run_05 | 0.00% | 0.00% | 100.00% |
| F02 | run_02 | 0.00% | 0.00% | 100.00% |
| F02 | run_03 | 0.00% | 0.00% | 100.00% |
| F03 | run_01 | 0.00% | 0.00% | 100.00% |
| F04 | run_01 | 0.00% | 0.00% | 100.00% |
| F04 | run_02 | 0.00% | 0.00% | 100.00% |
| F05 | run_01 | 0.00% | 0.00% | 100.00% |
| F05 | run_02 | 0.00% | 0.00% | 100.00% |
| F05 | run_03 | 0.00% | 0.00% | 100.00% |
| F05 | run_05 | 0.00% | 0.00% | 100.00% |
| F06 | run_01 | 0.00% | 0.00% | 100.00% |

## Empty generated suites

| function_id | run_id | suite_generation_status | generated_line_count | generated_test_function_count | generated_assert_count |
| --- | --- | --- | --- | --- | --- |
| F06 | run_02 | empty | 0 | 0 | 0 |
| F06 | run_05 | empty | 0 | 0 | 0 |

## Methodological notes

- `reliable_defect_detection_rate` is the main metric for defect detection; `defect_detection_rate_raw` is auxiliary.
- The official Pro execution produced 30 suites in the manifest, with 24 `generated_syntax_valid` and 6 `generated_syntax_invalid` records.
- Two suites were recorded as `empty` in the run summary (`F06/run_02` and `F06/run_05`); they produced zero-byte `raw_response.txt` and `test_generated.py` files and did not yield usable target executions.
- `imports_tests_fixtures_rate` stayed at 0.00% and `imports_only_ise26_targets_rate` stayed at 100.00%.
- No API errors were recorded in the official Pro manifest.
- The comparison artifacts against Flash are stored separately in `paper_assets/model_comparison/`.

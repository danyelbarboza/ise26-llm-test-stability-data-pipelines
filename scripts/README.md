# Pasta `scripts`

Esta pasta contem os scripts usados para gerar, executar, resumir e comparar os testes do experimento.

## `generate_llm_tests.py`

Gera testes a partir do prompt oficial e da configuracao do modelo.

### Uso seguro na rodada final

```bash
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_flash_final_10_functions.json
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_pro_final_10_functions.json
```

### Execucao real

```bash
python scripts/generate_llm_tests.py --execute --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_flash_final_10_functions.json
python scripts/generate_llm_tests.py --execute --experiment-id exp_final_10_functions --config experiments/config/deepseek_v4_pro_final_10_functions.json
```

Use `--execute` somente com confirmacao explicita.

### O que ele salva

- `prompt.txt`
- `system_prompt.txt`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `request.json`
- `status.json`
- `manifest.csv`

## `run_generated_tests.py`

Executa os testes gerados contra a implementacao correta e contra os bugs.

### Uso na rodada final

```bash
python scripts/run_generated_tests.py --experiment-id exp_final_10_functions --model deepseek_v4_flash
python scripts/run_generated_tests.py --experiment-id exp_final_10_functions --model deepseek_v4_pro
```

Tambem e possivel usar `--config` para inferir o modelo e, quando presente, o `experiment_id` do arquivo JSON correspondente.

### Saida

Cria o CSV bruto na pasta correta do modelo ou do experimento.

## `summarize_results.py`

Le o CSV bruto selecionado e gera os resumos agregados.

### Uso na rodada final

```bash
python scripts/summarize_results.py --experiment-id exp_final_10_functions --model deepseek_v4_flash
python scripts/summarize_results.py --experiment-id exp_final_10_functions --model deepseek_v4_pro
```

### Saida

Gera os arquivos de resumo na pasta correta do modelo ou do experimento.

## `compare_model_results.py`

Compara Flash e Pro quando ambos tiverem resultados oficiais reais.

### Uso na rodada final

```bash
python scripts/compare_model_results.py --experiment-id exp_final_10_functions
```

Na rodada final, cada modelo gera 50 suites planejadas e 200 execucoes-alvo.

### Saida

- `model_overall_comparison.csv`
- `model_overall_comparison.md`
- `model_by_function_comparison.csv`
- `model_by_function_comparison.md`
- `model_comparison_summary.md`

Se o modelo informado ainda estiver sem resultados oficiais, o script termina de forma controlada e nao inventa comparacao.

## Diagnostico rapido

- se o dry-run falhar, revise o arquivo de configuracao e o `experiment_id`;
- se o runner nao encontrar suites reais, confira se a arvore do modelo/experimento esta correta;
- se os resumos sairem vazios, verifique se o CSV bruto existe naquela pasta;
- se houver mistura entre Flash e Pro, revise o argumento `--model`;
- se houver mistura entre recortes historicos e a rodada final, revise o `--experiment-id`.

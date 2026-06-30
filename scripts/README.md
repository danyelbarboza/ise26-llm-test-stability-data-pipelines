# Pasta `scripts`

Esta pasta contém os scripts usados para gerar, executar, resumir e comparar os testes do experimento.

## `generate_llm_tests.py`

Gera testes a partir do prompt oficial e da configuração do modelo.

### Uso seguro

```bash
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_flash.json
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_pro.json
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_10_functions --config experiments/config/deepseek_v4_flash_10_functions.json
python scripts/generate_llm_tests.py --dry-run --experiment-id exp_10_functions --config experiments/config/deepseek_v4_pro_10_functions.json
```

### Execução real

```bash
python scripts/generate_llm_tests.py --execute --config experiments/config/deepseek_v4_pro.json
python scripts/generate_llm_tests.py --execute --experiment-id exp_10_functions --config experiments/config/deepseek_v4_pro_10_functions.json
```

Use `--execute` somente com confirmação explícita.

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

Executa os testes gerados contra a implementação correta e contra os bugs.

### Uso

```bash
python scripts/run_generated_tests.py --model deepseek_v4_flash
python scripts/run_generated_tests.py --model deepseek_v4_pro
python scripts/run_generated_tests.py --experiment-id exp_10_functions --model deepseek_v4_flash
python scripts/run_generated_tests.py --experiment-id exp_10_functions --model deepseek_v4_pro
```

Também é possível usar `--config` para inferir o modelo e, quando presente, o `experiment_id` do arquivo JSON correspondente.

### Saída

Cria o CSV bruto na pasta correta do modelo ou do experimento.

## `summarize_results.py`

Lê o CSV bruto selecionado e gera os resumos agregados.

### Uso

```bash
python scripts/summarize_results.py --model deepseek_v4_flash
python scripts/summarize_results.py --model deepseek_v4_pro
python scripts/summarize_results.py --experiment-id exp_10_functions --model deepseek_v4_flash
python scripts/summarize_results.py --experiment-id exp_10_functions --model deepseek_v4_pro
```

### Saída

Gera os arquivos de resumo na pasta correta do modelo ou do experimento.

## `compare_model_results.py`

Compara Flash e Pro quando ambos tiverem resultados oficiais reais.

### Uso

```bash
python scripts/compare_model_results.py
python scripts/compare_model_results.py --experiment-id exp_10_functions
```

Na expansão `exp_10_functions`, cada modelo gera 50 suítes planejadas e 200 execuções-alvo.

### Saída

- `model_overall_comparison.csv`
- `model_overall_comparison.md`
- `model_by_function_comparison.csv`
- `model_by_function_comparison.md`
- `model_comparison_summary.md`

Se o modelo informado ainda estiver sem resultados oficiais, o script termina de forma controlada e não inventa comparação.

## Diagnóstico rápido

- se o dry-run falhar, revise o arquivo de configuração e o `experiment_id`;
- se o runner não encontrar suítes reais, confira se a árvore do modelo/experimento está correta;
- se os resumos saírem vazios, verifique se o CSV bruto existe naquela pasta;
- se houver mistura entre Flash e Pro, revise o argumento `--model`;
- se houver mistura entre `exp_6_functions` e `exp_10_functions`, revise o `--experiment-id`.

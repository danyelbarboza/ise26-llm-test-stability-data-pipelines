# Pasta `scripts`

Esta pasta contém os scripts usados para gerar, executar e resumir os testes do experimento.

## `generate_llm_tests.py`

Gera testes a partir do prompt oficial e da configuração do modelo.

### Uso

```bash
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_flash.json
python scripts/generate_llm_tests.py --dry-run --config experiments/config/deepseek_v4_pro.json
```

### Execução real

```bash
python scripts/generate_llm_tests.py --execute --config experiments/config/deepseek_v4_flash.json
```

Esse comando só deve ser usado com confirmação explícita.

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
```

Também é possível usar `--config` para inferir o modelo a partir do arquivo JSON correspondente.

### Saída

Cria o CSV bruto em `results/by_model/<modelo>/raw/generated_tests_results.csv`.

## `summarize_results.py`

Lê o CSV bruto do modelo selecionado e gera os resumos agregados.

### Uso

```bash
python scripts/summarize_results.py --model deepseek_v4_flash
python scripts/summarize_results.py --model deepseek_v4_pro
```

Também é possível usar `--config` para inferir o modelo a partir do arquivo JSON correspondente.

### Saída

Gera os arquivos em `results/by_model/<modelo>/summary/`.

## `compare_model_results.py`

Compara Flash e Pro quando ambos tiverem resultados oficiais reais.

### Uso

```bash
python scripts/compare_model_results.py
```

### Saída futura

- `paper_assets/model_comparison/model_overall_comparison.csv`
- `paper_assets/model_comparison/model_overall_comparison.md`
- `paper_assets/model_comparison/model_by_function_comparison.csv`
- `paper_assets/model_comparison/model_by_function_comparison.md`
- `paper_assets/model_comparison/model_comparison_summary.md`

Se o modelo informado ainda estiver sem resultados oficiais, o script termina de forma controlada e não inventa comparação.

## Diagnóstico rápido

- se o dry-run falhar, revise o arquivo de configuração informado;
- se o runner não encontrar suítes reais, confira se o caminho do modelo está correto;
- se os resumos saírem vazios, verifique se o CSV bruto existe para aquele modelo;
- se houver mistura entre Flash e Pro, revise o argumento `--model` usado em cada etapa.

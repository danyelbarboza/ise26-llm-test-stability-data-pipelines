# README da pasta `scripts`

## O que esta pasta contém

Esta pasta contém os scripts operacionais do experimento.

## Papel de `run_generated_tests.py`

Esse script percorre a estrutura de `experiments/generated_tests/` e executa cada suíte contra:

- a implementação correta;
- os três bugs da função correspondente.

### Comando

```bash
python scripts/run_generated_tests.py
```

### O que ele gera

- `results/raw/generated_tests_results.csv`

## Papel de `summarize_results.py`

Esse script lê o CSV bruto e produz arquivos de resumo.

### Comando

```bash
python scripts/summarize_results.py
```

### O que ele gera

- `results/summary/summary_by_function.csv`
- `results/summary/summary_by_run.csv`
- `results/summary/summary_overall.csv`

## Como diagnosticar erros comuns

### O script rodou, mas só há placeholders

Isso normalmente significa que os arquivos `test_generated.py` ainda não contêm suítes reais.

No estado atual do repositório, esse comportamento é esperado.

### O teste gerado não executa

Verifique:

- se ele está no caminho certo;
- se importa de `ise26.targets`;
- se o arquivo contém código Python válido;
- se a resposta bruta da LLM foi extraída corretamente.

### O resumo saiu vazio

Isso pode acontecer quando:

- não houve execuções reais;
- o CSV bruto está vazio;
- tudo ainda é placeholder.

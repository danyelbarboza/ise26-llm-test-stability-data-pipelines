# README da pasta `scripts`

## O que esta pasta contém

Esta pasta contém os scripts operacionais do experimento.

## Papel de `generate_llm_tests.py`

Esse é o script oficial para gerar testes com a DeepSeek.

### O que ele faz

- lê a configuração oficial em `experiments/config/deepseek_v4_flash.json`;
- monta o prompt final a partir do template padrão;
- salva `system_prompt.txt`, `prompt.txt` e `request.json`;
- salva a resposta bruta em `raw_response.txt`;
- extrai mecanicamente o código para `test_generated.py`;
- salva `metadata.json` e `status.json`;
- atualiza `experiments/generated_tests/manifest.csv`.

### Comandos principais

```bash
python scripts/generate_llm_tests.py --dry-run
```

```bash
python scripts/generate_llm_tests.py --dry-run --function-id F01 --run-id run_01
```

```bash
python scripts/generate_llm_tests.py --execute
```

### Diagnóstico rápido

- Se o modo for `dry-run`, nenhuma chamada real é feita.
- Se faltar `DEEPSEEK_API_KEY`, a execução real deve falhar com erro claro.
- Se os artefatos já existirem, use `--overwrite` apenas quando a substituição estiver decidida.

## Papel de `run_generated_tests.py`

Esse script percorre a estrutura de `experiments/generated_tests/` e executa cada suíte real contra:

- a implementação correta;
- os três bugs da função correspondente.

Ele também distingue:

- placeholder;
- teste ausente;
- erro de API anterior;
- sintaxe inválida;
- teste pronto para execução.

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

### O script de geração rodou em `dry-run`

Isso é o comportamento seguro esperado. Nenhuma chamada real foi feita.

### O runner encontrou apenas placeholders

Isso significa que ainda não há suítes reais prontas para execução.

### O teste existe, mas não executa

Verifique:

- se o arquivo importa a função a partir de `ise26.targets`;
- se o código tem sintaxe Python válida;
- se o `status.json` não registra `api_error` ou `not_generated`.

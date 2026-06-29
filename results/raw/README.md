# README da pasta `results/raw`

## O que são resultados brutos

Resultados brutos são os registros diretos produzidos pelo script `run_generated_tests.py`.

## O que é registrado por execução

Em geral, cada linha representa a tentativa de executar uma suíte gerada contra uma implementação específica.

Isso inclui, por exemplo:

- função;
- execução;
- módulo alvo;
- tipo de alvo (`correct` ou `buggy`);
- `bug_id`, quando existir;
- código de saída;
- `stdout`;
- `stderr`;
- duração;
- status de executabilidade;
- informação sobre placeholder ou ausência de teste.

## Campos esperados

O CSV bruto pode conter campos como:

- `function_id`
- `run_id`
- `test_file`
- `test_file_status`
- `target_module`
- `target_type`
- `bug_id`
- `exit_code`
- `passed`
- `stdout`
- `stderr`
- `duration_seconds`
- `executable`
- `collected_tests`
- `failure_detected`

## Cuidado com placeholders

Se a suíte ainda for placeholder, a linha registrada é apenas uma saída técnica da infraestrutura. Ela não deve ser tratada como observação experimental real.

Atualmente, este é o cenário vigente do repositório.

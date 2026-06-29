# README da pasta `generated_tests`

## O que entra aqui

Esta pasta recebe os testes gerados por LLM que serão usados no experimento.

## Estrutura esperada por função

Cada função tem sua própria pasta:

- `F01/`
- `F02/`
- `F03/`
- `F04/`
- `F05/`
- `F06/`

## Estrutura esperada por execução

Dentro de cada função, deve existir uma pasta por execução:

- `run_01/`
- `run_02/`
- `run_03/`
- `run_04/`
- `run_05/`

## Exemplo de organização

```text
experiments/generated_tests/F01/run_01/test_generated.py
experiments/generated_tests/F01/run_02/test_generated.py
experiments/generated_tests/F02/run_01/test_generated.py
```

## Regra fundamental

Os arquivos desta pasta devem conter apenas testes realmente gerados pela LLM.

Não se deve:

- inventar testes para preencher pasta;
- copiar testes internos para fingir geração;
- misturar testes manuais com testes gerados.

## Observação sobre placeholders

O repositório pode conter placeholders apenas para preservar a estrutura.

Esses placeholders não são dados experimentais reais.

No estado atual do projeto, as pastas estão prontas, mas os testes gerados reais ainda precisam ser adicionados.

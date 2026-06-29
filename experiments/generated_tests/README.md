# README da pasta `generated_tests`

## O que entra aqui

Esta pasta recebe os testes realmente gerados pela LLM e os artefatos de rastreabilidade de cada execução.

## Estrutura esperada por função

Cada função tem sua própria pasta:

- `F01/`
- `F02/`
- `F03/`
- `F04/`
- `F05/`
- `F06/`

## Estrutura esperada por execução

Dentro de cada função, existe uma pasta por execução:

- `run_01/`
- `run_02/`
- `run_03/`
- `run_04/`
- `run_05/`

## Exemplo de organização

```text
experiments/generated_tests/F01/run_01/
experiments/generated_tests/F01/run_02/
experiments/generated_tests/F06/run_05/
```

## Arquivos esperados por execução real

Quando a geração real ocorrer, cada pasta deve conter:

- `system_prompt.txt`
- `prompt.txt`
- `request.json`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `status.json`

## Manifesto geral

As tentativas reais de geração também devem ser registradas em:

```text
experiments/generated_tests/manifest.csv
```

Cada linha representa uma tentativa de geração feita pelo script oficial.

## Regra fundamental

Os arquivos desta pasta devem conter apenas testes realmente gerados pela LLM.

Não se deve:

- inventar testes para preencher pasta;
- copiar testes internos para simular geração;
- editar manualmente um teste gerado na coleta oficial;
- misturar teste manual com teste gerado.

Cada arquivo `test_generated.py` deve construir os próprios dados sintéticos necessários no próprio arquivo.

Os testes gerados não devem importar `tests/fixtures.py`, porque essas fixtures existem apenas para a validação interna do repositório.

## Placeholders

O repositório mantém placeholders para preservar a estrutura antes da geração real.

Esses placeholders:

- não são dados experimentais;
- não contam como chamadas reais;
- não contam como testes gerados pela LLM.

## Observação sobre sintaxe inválida

Se a LLM retornar um código com sintaxe inválida:

- a resposta bruta continua valendo como artefato de rastreabilidade;
- o código extraído deve ser salvo mesmo assim;
- `metadata.json` deve registrar `syntax_valid = false`;
- `status.json` deve registrar `generated_syntax_invalid`.

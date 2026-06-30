# Pasta `experiments/generated_tests`

Esta pasta guarda os testes gerados por LLM, organizados por modelo, função e execução.

## Estrutura esperada

```text
experiments/generated_tests/
  deepseek_v4_flash/
    F01/run_01/test_generated.py
    F01/run_01/prompt.txt
    F01/run_01/raw_response.txt
    F01/run_01/metadata.json
    F01/run_01/request.json
    F01/run_01/status.json
  deepseek_v4_pro/
    F01/run_01/test_generated.py
```

## Como ler a estrutura

- cada modelo tem sua própria raiz;
- cada função tem sua subpasta `F01` a `F06`;
- cada execução tem sua subpasta `run_01` a `run_05`;
- o arquivo principal do teste é `test_generated.py`.

## Regras

- os arquivos aqui devem conter apenas testes realmente gerados pela LLM;
- não invente arquivos para “completar” a pasta;
- não misture Flash e Pro no mesmo diretório;
- não use `tests/fixtures.py` nos testes gerados;
- os testes precisam importar a função alvo a partir de `ise26.targets`.

## Sobre placeholders

Quando ainda não houver execução real, a pasta pode conter placeholders preparados para a próxima rodada do modelo. Esses placeholders não são resultados experimentais.

## Caminho do Flash oficial

A rodada oficial concluída com DeepSeek V4-Flash está preservada em `deepseek_v4_flash/`.

# Pasta `experiments/generated_tests`

Esta pasta guarda os testes gerados por LLM, organizados por `experiment_id`, por modelo, por função e por execução.

## Estrutura esperada

```text
experiments/generated_tests/
  deepseek_v4_flash/
    F01/run_01/test_generated.py
  deepseek_v4_pro/
    F01/run_01/test_generated.py
  exp_10_functions/
    deepseek_v4_flash/
      F01/run_01/test_generated.py
    deepseek_v4_pro/
      F01/run_01/test_generated.py
```

## Como ler a estrutura

- cada experimento tem sua própria raiz;
- cada modelo tem sua própria subpasta dentro do experimento;
- cada função tem sua subpasta `F01` a `F10` na expansão nova;
- cada execução tem sua subpasta `run_01` a `run_05`;
- o arquivo principal do teste é `test_generated.py`.

## Regras

- os arquivos aqui devem conter apenas testes realmente gerados pela LLM;
- não invente arquivos para “completar” a pasta;
- não misture Flash e Pro no mesmo diretório;
- não misture `exp_6_functions` com `exp_10_functions` no mesmo resultado;
- não use `tests/fixtures.py` nos testes gerados;
- os testes precisam importar a função-alvo a partir de `ise26.targets`.

## Sobre placeholders

Antes da execução oficial, a pasta pode conter placeholders preparados para a próxima rodada do modelo. Esses placeholders não são resultados experimentais e não fazem parte dos resultados oficiais já registrados para `exp_10_functions`.

## Baseline histórica e expansão nova

- a rodada histórica de 6 funções já está preservada;
- a expansão `exp_10_functions` já possui resultados oficiais para Flash e Pro;
- a expansão nova usa `exp_10_functions`, com 50 suítes planejadas por modelo e 200 execuções-alvo por modelo;
- placeholders só fazem sentido em etapas anteriores de preparação ou em novas rodadas ainda não executadas;
- resultados reais entram apenas quando a geração oficial for executada.

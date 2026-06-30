# Pasta `experiments/generated_tests`

Esta pasta guarda os testes gerados por LLM, organizados por `experiment_id`, por modelo, por funcao e por execucao.

## Estrutura esperada

```text
experiments/generated_tests/
  exp_final_10_functions/
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

- cada experimento tem sua propria raiz;
- cada modelo tem sua propria subpasta dentro do experimento;
- cada funcao tem sua subpasta `F01` a `F10` na rodada final;
- cada execucao tem sua subpasta `run_01` a `run_05`;
- o arquivo principal do teste e `test_generated.py`.

## Regras

- os arquivos aqui devem conter apenas testes realmente gerados pela LLM;
- nao invente arquivos para "completar" a pasta;
- nao misture Flash e Pro no mesmo diretorio;
- nao misture `exp_6_functions`, `exp_10_functions` e `exp_final_10_functions` no mesmo resultado;
- nao use `tests/fixtures.py` nos testes gerados;
- os testes precisam importar a funcao-alvo a partir de `ise26.targets`;
- os testes devem criar seus proprios `DataFrame`s sinteticos dentro do proprio arquivo.

## Sobre placeholders

Antes da execucao oficial, a pasta final pode conter placeholders preparados para a rodada do modelo. Esses placeholders nao sao resultados experimentais reais.

Na rodada final, o estado inicial esperado e:

- 50 placeholders por modelo;
- 100 placeholders no total;
- 0 suites reais;
- 0 chamadas reais.

## Baseline historica e experimento final

- a rodada historica de 6 funcoes continua preservada;
- a expansao intermediaria de 10 funcoes continua disponivel, mas e `deprecated`;
- a rodada final `exp_final_10_functions` e a referencia principal do artigo;
- resultados reais entram apenas quando a geracao oficial for executada.

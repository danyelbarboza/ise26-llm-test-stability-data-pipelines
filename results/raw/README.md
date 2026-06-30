# Pasta `results/raw`

Esta pasta raiz existe por compatibilidade e documentacao. Os CSVs oficiais agora ficam nas pastas especificas de modelo e de experimento.

## Arquivos esperados

- `generated_tests_results.csv`

## Onde ficam os arquivos oficiais

- baseline historica de 6 funcoes:
  - `results/by_model/deepseek_v4_flash/raw/`
  - `results/by_model/deepseek_v4_pro/raw/`
- expansao intermediaria de 10 funcoes:
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_flash/raw/`
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_pro/raw/`
- rodada final do artigo:
  - `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_flash/raw/`
  - `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_pro/raw/`

## O que cada linha representa

Cada linha do CSV bruto representa uma tentativa de execucao de uma suite gerada contra um alvo especifico:

- implementacao correta;
- `BUG01`;
- `BUG02`;
- `BUG03`.

## Atencao

- `exp_10_functions` e historico e nao e a referencia principal;
- `exp_final_10_functions` e o experimento principal do artigo;
- CSV criado apenas para validacao interna ou antes da execucao oficial nao deve ser tratado como resultado final.

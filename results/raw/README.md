# Pasta `results/raw`

Esta pasta raiz existe por compatibilidade e documentação. Os CSVs oficiais agora ficam nas pastas específicas de modelo e de experimento.

## Onde ficam os arquivos oficiais

- baseline histórica de 6 funções:
  - `results/by_model/deepseek_v4_flash/raw/`
  - `results/by_model/deepseek_v4_pro/raw/`
- expansão de 10 funções:
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_flash/raw/`
  - `results/by_experiment/exp_10_functions/by_model/deepseek_v4_pro/raw/`

## O que o CSV bruto registra

Cada linha representa uma execução-alvo de uma suíte gerada contra:

- a implementação correta;
- BUG01;
- BUG02;
- BUG03.

## Campos esperados

- identificadores da função, da execução e do modelo/experimento;
- tipo de alvo;
- estado da suíte;
- código de saída;
- sucesso ou falha;
- métricas derivadas como `bug_failure`, `correct_passed_for_same_suite`, `reliable_defect_detection`, `false_positive` e `contaminated_bug_failure`;
- contagens estáticas do arquivo gerado, quando disponíveis.

## Atenção

- placeholders não são resultado experimental real;
- falhas de sintaxe são registradas separadamente;
- nunca misture Flash e Pro no mesmo CSV bruto;
- nunca misture a baseline histórica de 6 funções com a expansão de 10 funções no mesmo arquivo.

# Pasta `results/raw`

Esta pasta raiz é mantida apenas para compatibilidade e documentação. Os CSVs oficiais agora ficam em `results/by_model/<modelo>/raw/`.

## O que o CSV bruto registra

Cada linha representa uma execução-alvo de uma suíte gerada contra:

- a implementação correta;
- BUG01;
- BUG02;
- BUG03.

## Campos esperados

- identificadores da função e da execução;
- tipo de alvo;
- estado da suíte;
- código de saída;
- sucesso ou falha;
- métricas derivadas como `bug_failure`, `correct_passed_for_same_suite`, `reliable_defect_detection`, `false_positive` e `contaminated_bug_failure`;
- contagens estáticas do arquivo gerado, quando disponíveis.

## Atenção

- placeholders não são resultado experimental real;
- falhas de sintaxe são registradas separadamente;
- nunca misture Flash e Pro no mesmo CSV bruto.

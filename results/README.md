# Pasta `results`

Esta pasta guarda os resultados oficiais e os resultados preparados para os experimentos do repositório.

## Estrutura principal

```text
results/
  by_model/
    deepseek_v4_flash/
    deepseek_v4_pro/
  by_experiment/
    exp_10_functions/
      by_model/
        deepseek_v4_flash/
        deepseek_v4_pro/
```

## Como interpretar a estrutura

- `results/by_model/` mantém a baseline histórica de 6 funções;
- `results/by_experiment/exp_10_functions/` isola a expansão nova de 10 funções, com 50 suítes planejadas por modelo e 200 execuções-alvo por modelo;
- Flash e Pro nunca devem compartilhar o mesmo CSV bruto;
- resultados de experimentos diferentes nunca devem ser misturados.

## O que cada pasta guarda

- `raw/`: CSV detalhado com cada execução-alvo;
- `summary/`: CSVs agregados por função, por run e no geral;
- `reports/`: relatórios em Markdown para leitura humana.

## Estado atual

- a execução oficial histórica de Flash existe em `results/by_model/deepseek_v4_flash/`;
- a execução oficial histórica de Pro existe em `results/by_model/deepseek_v4_pro/`;
- a expansão `exp_10_functions` tem estrutura separada em `results/by_experiment/exp_10_functions/`;
- a expansão nova usa 50 suítes por modelo e 200 execuções-alvo por modelo;
- os arquivos preparados para a expansão nova não devem ser confundidos com resultados oficiais finais até a geração real ser concluída.

## Métricas

- `reliable_defect_detection_rate` é a métrica principal;
- `defect_detection_rate_raw` é auxiliar;
- `false_positive_rate` e `contaminated_bug_failure_rate` ajudam na leitura metodológica.

## Atenção

CSV gerado sem testes reais, ou produzido antes da execução oficial, não deve ser tratado como resultado experimental final.

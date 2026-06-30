# Pasta `results`

Esta pasta guarda os resultados oficiais e os artefatos de apoio dos experimentos do repositorio.

## Estrutura principal

```text
results/
  by_model/
    deepseek_v4_flash/
    deepseek_v4_pro/
  by_experiment/
    exp_10_functions/
    exp_final_10_functions/
```

## Como interpretar a estrutura

- `results/by_model/` preserva a baseline historica de 6 funcoes;
- `results/by_experiment/exp_10_functions/` preserva a expansao intermediaria, hoje tratada como `deprecated`;
- `results/by_experiment/exp_final_10_functions/` guarda os resultados oficiais do artigo;
- Flash e Pro nunca devem compartilhar o mesmo CSV bruto;
- resultados de experimentos diferentes nunca devem ser misturados.

## O que cada pasta guarda

- `raw/`: CSV detalhado com cada execucao-alvo;
- `summary/`: CSVs agregados por funcao, por run e no geral;
- `reports/`: relatorios em Markdown para leitura humana.

## Estado atual

- a baseline historica de 6 funcoes continua preservada em `results/by_model/`;
- a expansao intermediaria `exp_10_functions` continua disponivel, mas e historica e nao e a referencia principal;
- a rodada final `exp_final_10_functions` e a referencia principal do artigo;
- os artefatos oficiais finais devem ficar separados dos artefatos historicos e dos artefatos de validacao;
- placeholders e CSVs de preparacao nao devem ser tratados como resultado experimental final.

## Metricas

- `reliable_defect_detection_rate` e a metrica principal;
- `defect_detection_rate_raw` e auxiliar;
- `false_positive_rate` e `contaminated_bug_failure_rate` ajudam na leitura metodologica.

## Atencao

CSV gerado sem testes reais, ou produzido antes da execucao oficial, nao deve ser tratado como resultado experimental final.

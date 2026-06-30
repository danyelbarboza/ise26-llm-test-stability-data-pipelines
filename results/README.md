# Pasta `results`

Esta pasta guarda os resultados oficiais do experimento, organizados por modelo.

## Estrutura

```text
results/
  by_model/
    deepseek_v4_flash/
      raw/
      summary/
      reports/
    deepseek_v4_pro/
      raw/
      summary/
      reports/
```

## O que cada subpasta guarda

- `raw/`: CSV detalhado com cada execução-alvo;
- `summary/`: CSVs agregados por função, por run e no geral;
- `reports/`: relatórios em Markdown para leitura humana.

## Estado atual

- a execução oficial do Flash já existe e fica em `results/by_model/deepseek_v4_flash/`;
- o Pro já tem execução oficial e fica em `results/by_model/deepseek_v4_pro/`;
- não misture CSVs de modelos diferentes no mesmo arquivo.

## Resultados oficiais e comparação

Os resultados comparativos entre Flash e Pro ficam em `paper_assets/model_comparison/` e só são válidos quando os dois modelos têm resumos oficiais reais.
O script `scripts/compare_model_results.py` gera os arquivos comparativos a partir desses resumos oficiais.

## Atenção

CSV gerado sem testes reais, ou produzido antes da execução oficial, não deve ser tratado como resultado experimental final.

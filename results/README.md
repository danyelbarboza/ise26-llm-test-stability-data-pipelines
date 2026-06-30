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
- o Pro ainda está apenas preparado estruturalmente;
- não misture CSVs de modelos diferentes no mesmo arquivo.

## Resultados oficiais e comparação

Os resultados comparativos entre Flash e Pro devem ser preparados em `paper_assets/model_comparison/` apenas depois que as duas execuções oficiais existirem.
O script `scripts/compare_model_results.py` só deve produzir saída quando os dois modelos tiverem resumos oficiais reais; se o Pro ainda estiver apenas com placeholders, ele termina sem gerar números.

## Atenção

CSV gerado sem testes reais, ou produzido antes da execução oficial, não deve ser tratado como resultado experimental final.

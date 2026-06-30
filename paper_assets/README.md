# Pasta `paper_assets`

Esta pasta reúne materiais preparados para o artigo acadêmico.

## O que vai aqui

- tabelas extraídas dos resultados oficiais;
- resumos interpretativos;
- comparação entre modelos;
- artefatos de apoio para a redação final.

## Estrutura atual

- `tables/`: tabelas já derivadas dos resultados oficiais;
- `model_comparison/`: comparação entre Flash e Pro, quando ambos existirem;
- `results_summary.md`: síntese interpretativa dos resultados oficiais.

O comparador oficial do repositório é `scripts/compare_model_results.py`, e ele só deve gerar arquivos em `model_comparison/` quando os dois modelos tiverem resultados oficiais reais.

## Regra importante

Não use esta pasta para inventar números novos. Tudo aqui deve ser derivado dos CSVs oficiais já existentes.

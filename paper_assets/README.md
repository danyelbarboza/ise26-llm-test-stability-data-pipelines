# Pasta `paper_assets`

Esta pasta reúne materiais preparados para o artigo acadêmico.

## O que vai aqui

- tabelas extraídas dos resultados oficiais;
- resumos interpretativos;
- comparação entre modelos;
- artefatos de apoio para a redação final.

## Estrutura atual

- `tables/`: tabelas derivadas dos resultados oficiais;
- `model_comparison/`: comparação histórica entre Flash e Pro para a baseline de 6 funções;
- `exp_10_functions/`: materiais da expansão nova de 10 funções;
- `results_summary.md`: síntese interpretativa dos resultados oficiais.

O comparador oficial do repositório é `scripts/compare_model_results.py`, e ele só deve gerar arquivos em uma pasta comparativa quando os dois modelos tiverem resultados oficiais reais do mesmo `experiment_id`.

## Regra importante

Não use esta pasta para inventar números novos. Tudo aqui deve ser derivado dos CSVs oficiais já existentes.

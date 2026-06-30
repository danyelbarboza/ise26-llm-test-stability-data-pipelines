# Pasta `paper_assets`

Esta pasta reune materiais preparados para o artigo academico.

## O que vai aqui

- tabelas extraidas dos resultados oficiais;
- resumos interpretativos;
- comparacao entre modelos;
- artefatos de apoio para a redacao final.

## Estrutura atual

- `tables/`: tabelas derivadas dos resultados oficiais;
- `model_comparison/`: comparacao historica entre Flash e Pro para os recortes antigos;
- `exp_10_functions/`: materiais da expansao intermediaria, mantida apenas para rastreabilidade historica;
- `exp_final_10_functions/`: materiais da rodada final, que e a referencia principal do artigo;
- `results_summary.md`: sintese interpretativa dos resultados oficiais.

O comparador oficial do repositorio e `scripts/compare_model_results.py`, e ele so deve gerar arquivos em uma pasta comparativa quando os dois modelos tiverem resultados oficiais reais do mesmo `experiment_id`.

## Regra importante

Nao use esta pasta para inventar numeros novos. Tudo aqui deve ser derivado dos CSVs oficiais reais.

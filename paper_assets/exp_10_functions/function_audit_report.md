# Auditoria metodologica das funcoes do `exp_10_functions`

## Resumo executivo

O experimento expandido `exp_10_functions` foi auditado como evidencia historica e de validacao interna, com base nos resultados oficiais dos dois modelos (`deepseek-v4-flash` e `deepseek-v4-pro`), nos metadados do repositorio, nas implementacoes corretas, nos bugs intencionais, nos testes internos e nas suites realmente geradas.

A conclusao central e que `exp_10_functions` nao e robusto o bastante para ser o resultado principal do artigo. Os pontos mais fragilizados sao F07 e F09, que ficaram com `reliable_defect_detection_rate = 0.0` nos dois modelos. F01 e F03 tambem sao problematicas por combinarem baixa deteccao confiavel com alta taxa de falso positivo. F02 e a funcao mais consistente. F04, F05, F06, F08 e F10 sao interpretaveis, mas continuam com limitacoes relevantes.

O principal ganho metodologico do recorte e mostrar que `defect_detection_rate_raw` superestima a qualidade quando a mesma suite falha na implementacao correta. Isso aparece com muita clareza em F07 e F09: o bug e detectado bruscamente, mas nao de forma confiavel.

## Visao quantitativa geral

### Flash

- suites reais: 45 de 50
- runs com sintaxe invalida: 4
- runs vazias: 1
- execucoes reais: 180
- `correct_pass_rate`: 0.266667
- `bug_failure_rate`: 0.992593
- `defect_detection_rate_raw`: 0.992593
- `reliable_defect_detection_rate`: 0.259259
- `false_positive_rate`: 0.733333
- `contaminated_bug_failure_rate`: 0.733333

### Pro

- suites reais: 44 de 50
- runs com sintaxe invalida: 6
- runs vazias: 0
- execucoes reais: 176
- `correct_pass_rate`: 0.272727
- `bug_failure_rate`: 1.000000
- `defect_detection_rate_raw`: 1.000000
- `reliable_defect_detection_rate`: 0.272727
- `false_positive_rate`: 0.727273
- `contaminated_bug_failure_rate`: 0.727273

## Desempenho por funcao

| Funcao | Flash reliable | Pro reliable | Flash false positive | Pro false positive | Categoria | Recomendacao |
|---|---:|---:|---:|---:|---|---|
| F01 | 20.0% | 20.0% | 80.0% | 80.0% | problematica | manter como historico e discutir limitacao |
| F02 | 20.0% | 75.0% | 80.0% | 25.0% | boa | manter como evidencia historica |
| F03 | 0.0% | 20.0% | 100.0% | 80.0% | problematica | manter como historico e discutir limitacao |
| F04 | 50.0% | 66.7% | 50.0% | 33.3% | aceitavel | manter como historico |
| F05 | 50.0% | 33.3% | 50.0% | 66.7% | aceitavel | manter como historico |
| F06 | 41.7% | 40.0% | 50.0% | 60.0% | aceitavel | manter como historico |
| F07 | 0.0% | 0.0% | 100.0% | 100.0% | critica | revisar e rodar nova versao experimental |
| F08 | 60.0% | 0.0% | 40.0% | 100.0% | aceitavel | manter como historico e monitorar diferenca entre modelos |
| F09 | 0.0% | 0.0% | 100.0% | 100.0% | critica | revisar e rodar nova versao experimental |
| F10 | 33.3% | 40.0% | 66.7% | 60.0% | aceitavel | manter como historico e discutir limitacao |
## Leitura metodologica por bloco

### F07 - parse_order_items_json

F07 e a funcao mais critica. Os dois modelos tiveram reliable detection zero. O problema principal e de contrato: o comportamento esperado fala em lista JSON de itens, mas a implementacao e os testes ainda deixam espaco para interpretar JSON nao-lista, item sem sku e dtypes de quantity/unit_price de forma diferente.

### F09 - cap_outliers_iqr

F09 tambem e critica. O contrato nao explicita o metodo de quartil/interpolacao com suficiente precisao. A implementacao usa a convenicao padrao do pandas, mas a LLM variou a expectativa de quartis e limites em varios testes, o que levou a falso positivo alto e reliable detection zero nos dois modelos.

### F01 e F03

Essas funcoes sao problematicas, mas ainda interpretaveis. O que mais pesa e a sensibilidade a dtype, `pd.NA` e comparacoes estritas de `DataFrame` vazio.

### F08

F08 e clara no contrato, mas mostra uma assimetria importante entre os modelos: Flash ainda teve deteccao confiavel moderada, enquanto Pro caiu para zero. Isso aponta mais para sensibilidade do modelo do que para ambiguidade do contrato.

## Bugs auditados

Os 30 bugs continuam adequados do ponto de vista estrutural:

- sobrescrevem apenas a funcao-alvo;
- preservam a assinatura da funcao correta;
- sao plausiveis e simples;
- sao detectaveis por teste unitario;
- nao criam falha estrutural que invalide a comparacao.

## Recomendacao metodologica

Recomendacao por funcao:

- F01: manter como historico e discutir limitacao
- F02: manter como evidencia historica
- F03: manter como historico e discutir limitacao
- F04: manter como historico
- F05: manter como historico
- F06: manter como historico
- F07: revisar e rodar nova versao experimental
- F08: manter como historico e monitorar diferenca entre modelos
- F09: revisar e rodar nova versao experimental
- F10: manter como historico e discutir limitacao

### Decisao sugerida para o artigo

`exp_10_functions` deve ser tratado como historico/de validacao interna. O resultado principal do artigo deve vir da rodada final `exp_final_10_functions`, que foi criada justamente para registrar a base corrigida das 10 funcoes.

Se o artigo ainda quiser usar `exp_10_functions` em alguma parte, o uso mais seguro e como evidencia comparativa historica, com destaque especial para as limitacoes de F07 e F09.

## Ameacas a validade

- detalhes de pandas como `StringDtype`, `Float64` e `pd.NA` afetam fortemente a passagem dos testes;
- comparacoes estritas em `DataFrame` vazio podem gerar falsos negativos;
- a convencao de quartil em F09 nao esta especificada de forma suficientemente forte;
- F07 mistura semantica de JSON de lista versus JSON de objeto;
- `bug_failure_rate` sozinho superestima a qualidade quando a suite falha tambem na implementacao correta;
- `reliable_defect_detection_rate` deve continuar sendo a metrica principal.

## Decisao final sugerida

O experimento e util como validacao interna e como historico metodologico, mas nao deve ser vendido como a melhor versao do benchmark. F07 e F09 sao os maiores riscos; F01 e F03 tambem merecem cautela; F02 e o melhor ponto de apoio do conjunto.

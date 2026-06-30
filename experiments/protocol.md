# Protocolo experimental ISE26

## Objetivo

Avaliar a estabilidade de testes automatizados gerados por LLM para funcoes de transformacao de dados em Python.

## Escopo

O repositorio mantem tres recortes historicos:

- `exp_6_functions`: baseline historica usada so para validacao interna;
- `exp_10_functions`: expansao intermediaria usada para validacao interna e tratada como `deprecated`;
- `exp_final_10_functions`: experimento final do artigo.

Para a rodada final `exp_final_10_functions`:

- 10 funcoes corretas;
- 30 versoes defeituosas intencionais;
- 5 execucoes por funcao;
- 50 suites planejadas por modelo;
- 100 chamadas planejadas no total;
- 200 execucoes-alvo por modelo;
- 400 execucoes-alvo no total;
- 100 placeholders iniciais no total;
- 50 placeholders por modelo no estado inicial.

## Modelos oficiais

- DeepSeek V4-Flash;
- DeepSeek V4-Pro.

Cada modelo deve ter sua propria arvore de artefatos. Nunca misture Flash e Pro no mesmo diretorio, CSV ou comparacao.

## Configuracao oficial

- Provedor: DeepSeek;
- Base URL: `https://api.deepseek.com`;
- Modelo Flash da rodada final: `deepseek-v4-flash`;
- Modelo Pro da rodada final: `deepseek-v4-pro`;
- Temperatura: `0.7`;
- Top-p: `1.0`;
- Max tokens: `4096`;
- Historico entre chamadas: desativado;
- Estado padrao do gerador: `dry-run`.

## Prompts oficiais

O prompt padrao deve:

- pedir saida somente em codigo Python;
- pedir testes em `pytest`;
- importar a funcao alvo somente de `ise26.targets`;
- pedir que cada teste crie seus proprios dados sinteticos;
- cobrir casos comuns e casos de borda;
- considerar nulos, datas, schema, duplicatas, dtype, ordenacao, arredondamento e regras de negocio quando aplicavel;
- nao mencionar nem incentivar `tests/fixtures.py`.

Se o prompt mudar, a alteracao precisa ser registrada no protocolo e na documentacao.

## Regra sobre edicao dos testes

- testes gerados por LLM nao devem ser editados manualmente;
- correcoes tecnicas so podem acontecer se forem registradas como parte do protocolo;
- `tests/fixtures.py` e exclusivo dos testes internos;
- testes gerados devem criar seus proprios dados dentro do proprio `test_generated.py`.

## Estrutura de salvamento

### Rodada final `exp_final_10_functions`

- `experiments/generated_tests/exp_final_10_functions/deepseek_v4_flash/`
- `experiments/generated_tests/exp_final_10_functions/deepseek_v4_pro/`
- `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_flash/`
- `results/by_experiment/exp_final_10_functions/by_model/deepseek_v4_pro/`
- `paper_assets/exp_final_10_functions/model_comparison/`

### Estruturas historicas

- `exp_6_functions` continua preservada para rastreabilidade;
- `exp_10_functions` continua preservada, mas nao e a referencia principal do artigo.

Cada execucao deve salvar:

- `prompt.txt`
- `system_prompt.txt`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `request.json`
- `status.json`
- `manifest.csv`

## Criterios de validade

### Execucao valida

Uma suite e considerada valida quando:

- existe `test_generated.py`;
- o arquivo tem sintaxe Python valida;
- a resposta bruta foi salva;
- o codigo extraido foi salvo;
- os metadados foram registrados;
- o status foi registrado.

### Execucao invalida

Uma suite e invalida quando:

- a chamada a API falha (`api_error`);
- o arquivo final tem sintaxe invalida;
- o arquivo nao define uma suite executavel;
- o teste depende de um recurso externo proibido pelo protocolo.

### Placeholder

Placeholder nao e resultado experimental real. Ele serve apenas para preparar a estrutura antes da geracao oficial.

## Metricas registradas

- executabilidade;
- passagem na implementacao correta;
- falha bruta contra bug (`bug_failure_rate`);
- deteccao confiavel (`reliable_defect_detection_rate`);
- falso positivo (`false_positive_rate`);
- falha contaminada (`contaminated_bug_failure_rate`);
- numero de linhas do teste gerado;
- numero aproximado de funcoes de teste;
- numero aproximado de asserts;
- contagem de imports para `tests.fixtures`;
- contagem de imports limitados a `ise26.targets`.

## Interpretacao metodologica

- falhar contra o bug nao basta para contar deteccao de defeito;
- a mesma suite precisa passar na correta para a deteccao ser confiavel;
- falha na correta deve ser tratada como falso positivo;
- falha contra bug com falha na correta e resultado contaminado;
- `reliable_defect_detection_rate` e a metrica principal;
- `defect_detection_rate_raw` e auxiliar e nao deve ser usada sozinha.

## Comparacao entre modelos

A comparacao entre Flash e Pro so e valida quando ambos tiverem resultados oficiais reais do mesmo `experiment_id`.

Nao compare Flash e Pro usando placeholders, nem compare resultados de `exp_6_functions`, `exp_10_functions` e `exp_final_10_functions` entre si.

## Limitacoes

- os testes gerados por LLM podem variar entre execucoes;
- testes com sintaxe invalida nao entram como execucao real;
- placeholders ajudam a preparar a estrutura em etapas anteriores, mas nao contam como resultado oficial;
- a rodada final `exp_final_10_functions` deve ser analisada separadamente das rodadas historicas.

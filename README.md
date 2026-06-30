# ISE26 — Avaliação de Testes Gerados por LLMs para Pipelines de Dados

## Visão geral

O repositório `ise26-llm-test-stability-data-pipelines` apoia um estudo acadêmico sobre estabilidade de testes automatizados gerados por LLMs para funções de transformação de dados em Python.

O foco não é criar um produto final. O foco é manter uma base experimental simples, reprodutível, rastreável e fácil de revisar por quem está entrando agora no projeto.

## Objetivo do projeto

O objetivo do estudo é observar como suítes de teste geradas por LLM se comportam quando executadas contra:

- a implementação correta de cada função;
- três versões defeituosas intencionais da mesma função.

Com isso, o grupo pode analisar:

- executabilidade;
- passagem na implementação correta;
- detecção confiável de defeitos;
- variação entre execuções repetidas do mesmo modelo.

## Contexto acadêmico

O desenho experimental do repositório foi organizado para separar claramente:

- funções corretas;
- versões defeituosas;
- testes internos escritos manualmente;
- testes gerados por LLM;
- artefatos de geração;
- resultados brutos;
- resultados resumidos;
- protocolo experimental.

## Resumo do experimento

O desenho experimental oficial atualmente prevê:

- `6` funções corretas oficiais;
- `18` versões defeituosas intencionais;
- `5` execuções planejadas por função para geração de testes;
- `30` chamadas reais planejadas à LLM na rodada completa;
- `1` módulo de roteamento dinâmico (`ise26.targets`) para trocar a implementação testada sem alterar o arquivo do teste;
- `1` provedor oficial de geração configurado: DeepSeek;
- `1` modelo oficial configurado: `deepseek-v4-flash`.

No estado atual do repositório:

- a infraestrutura de geração já existe;
- o modo padrão da geração é `dry-run`;
- nenhuma chamada real à API é feita sem `--execute`;
- os placeholders de `generated_tests/` continuam existindo para manter a estrutura;
- qualquer CSV gerado sem testes reais continua sendo apenas saída técnica da infraestrutura, não resultado experimental.

## Leitura metodológica dos resultados

Nesta base, uma suíte só conta como detecção confiável de defeito quando duas coisas acontecem ao mesmo tempo:

- a suíte passa na implementação correta da função;
- a mesma suíte falha na versão defeituosa testada.

Por isso, os arquivos de resultados passam a separar claramente:

- `bug_failure`: a suíte falhou contra um bug;
- `correct_passed_for_same_suite`: a mesma suíte passou na implementação correta;
- `reliable_defect_detection`: houve falha no bug e aprovação na correta;
- `false_positive`: a suíte falhou na correta;
- `contaminated_bug_failure`: houve falha no bug, mas a correta também falhou.

Os arquivos `results/summary/*.csv` também registram métricas derivadas como:

- `defect_detection_rate_raw`;
- `reliable_defect_detection_rate`;
- `false_positive_rate`;
- `contaminated_bug_failure_rate`.

Placeholders continuam fora da contagem experimental principal e devem ser lidos apenas como infraestrutura.

## Como o experimento funciona

O fluxo recomendado é:

1. validar a base interna com `python -m pytest`;
2. revisar `experiments/protocol.md`;
3. configurar a chave da DeepSeek em um arquivo `.env` local, fora do versionamento;
4. executar `python scripts/generate_llm_tests.py --dry-run`;
5. executar `python scripts/generate_llm_tests.py --execute` somente com confirmação explícita;
6. salvar, para cada execução, prompt, resposta bruta, código extraído, metadados e status;
7. rodar `python scripts/run_generated_tests.py`;
8. rodar `python scripts/summarize_results.py`;
9. analisar apenas resultados provenientes de testes realmente gerados pela LLM;
10. conferir se as suítes reais passaram na correta antes de interpretar qualquer falha em bug como detecção confiável.

## Estrutura do repositório

```text
ISE26/
├── README.md
├── .env.example
├── requirements.txt
├── pytest.ini
├── src/
│   ├── README.md
│   └── ise26/
│       ├── README.md
│       ├── targets.py
│       ├── llm/
│       ├── implementations/
│       └── metadata/
├── tests/
├── experiments/
│   ├── README.md
│   ├── protocol.md
│   ├── config/
│   ├── prompts/
│   ├── generated_tests/
│   └── raw_responses/
├── results/
└── scripts/
```

## Tecnologias usadas

- Python 3.11+
- Pandas
- Pytest
- OpenAI SDK em modo compatível com a API da DeepSeek
- JSON
- CSV

## Funções corretas

As funções corretas oficiais estão em `src/ise26/implementations/correct.py`.

| ID | Função | Papel no experimento |
|---|---|---|
| F01 | `clean_customer_names` | Padroniza nomes de clientes sem alterar o `DataFrame` original |
| F02 | `deduplicate_events` | Remove duplicatas mantendo o evento mais recente |
| F03 | `calculate_monthly_revenue` | Calcula receita mensal ignorando cancelamentos |
| F04 | `join_customers_orders` | Faz junção completa entre clientes e pedidos com `record_status` |
| F05 | `validate_schema` | Valida colunas e tipos lógicos esperados |
| F06 | `classify_payment_status` | Classifica pagamentos como válidos, atrasados, pendentes ou inválidos |

## Versões defeituosas

Cada função correta possui três variantes defeituosas intencionais, totalizando `18` bugs.

| Função | Bug | Arquivo | Descrição resumida |
|---|---|---|---|
| F01 | BUG01 | `f01_bug01.py` | Não trata nulos corretamente |
| F01 | BUG02 | `f01_bug02.py` | Não remove acentos |
| F01 | BUG03 | `f01_bug03.py` | Não remove espaços extras |
| F02 | BUG01 | `f02_bug01.py` | Mantém o primeiro evento em vez do mais recente |
| F02 | BUG02 | `f02_bug02.py` | Remove linhas com `event_id` nulo |
| F02 | BUG03 | `f02_bug03.py` | Ordena timestamp como string |
| F03 | BUG01 | `f03_bug01.py` | Soma pedidos cancelados |
| F03 | BUG02 | `f03_bug02.py` | Não trata `amount` inválido ou nulo como zero |
| F03 | BUG03 | `f03_bug03.py` | Agrupa por dia em vez de mês |
| F04 | BUG01 | `f04_bug01.py` | Usa `inner join` em vez de `full outer join` |
| F04 | BUG02 | `f04_bug02.py` | Não cria `record_status` |
| F04 | BUG03 | `f04_bug03.py` | Classifica incorretamente registros sem correspondência ou com chave nula |
| F05 | BUG01 | `f05_bug01.py` | Ignora colunas ausentes |
| F05 | BUG02 | `f05_bug02.py` | Ignora erros de tipo |
| F05 | BUG03 | `f05_bug03.py` | Reprova `DataFrame` com colunas extras |
| F06 | BUG01 | `f06_bug01.py` | Marca pagamento no vencimento como atraso |
| F06 | BUG02 | `f06_bug02.py` | Trata `amount` zero como pendente |
| F06 | BUG03 | `f06_bug03.py` | Trata `paid_date` inválido como ausência de pagamento |

## Diferença entre os componentes do experimento

### Funções corretas

São as implementações oficiais usadas como referência de comportamento.

### Versões defeituosas

São variantes intencionais usadas para verificar se os testes conseguem detectar falhas plausíveis.

### Testes internos

São testes manuais do próprio repositório. Eles servem para manter a base estável e não substituem os dados experimentais principais.

### Testes gerados por LLM

São os testes produzidos pela DeepSeek para cada função e execução planejada. Eles devem ser salvos em `experiments/generated_tests/FXX/run_YY/`.

### Resultados brutos

São os registros detalhados da execução dos testes gerados contra a implementação correta e contra os bugs.

### Resultados resumidos

São agregações dos resultados brutos para facilitar leitura e análise.

## Integração DeepSeek

### Configuração oficial

- Provedor: `DeepSeek`
- Modelo: `deepseek-v4-flash`
- Base URL: `https://api.deepseek.com`
- Temperatura: `0.7`
- Top-p: `1.0`
- Max tokens: `4096`
- Stream: `false`
- Histórico entre chamadas: `não usar`

### Arquivo de configuração

O arquivo oficial fica em:

```text
experiments/config/deepseek_v4_flash.json
```

### Variáveis de ambiente

Crie um arquivo `.env` local a partir de `.env.example`:

```env
DEEPSEEK_API_KEY=coloque_sua_chave_aqui
ISE26_LLM_MODEL=deepseek-v4-flash
ISE26_LLM_TEMPERATURE=0.7
ISE26_LLM_TOP_P=1.0
ISE26_LLM_MAX_TOKENS=4096
```

A chave da API:

- não deve ser salva em arquivo versionado;
- não deve ser registrada em `request.json`;
- não deve aparecer em logs ou metadados.

## Uso de `ISE26_TARGET_MODULE`

O módulo `src/ise26/targets.py` permite que o mesmo teste importe sempre do mesmo lugar:

```python
from ise26.targets import clean_customer_names
```

Na execução, a implementação real é selecionada pela variável de ambiente `ISE26_TARGET_MODULE`.

Exemplo com a implementação correta:

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.correct"
python -m pytest experiments/generated_tests/F01/run_01/test_generated.py
```

Exemplo com um bug:

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.buggy.f01_bug01"
python -m pytest experiments/generated_tests/F01/run_01/test_generated.py
```

## Testes internos

Os testes internos ficam em `tests/` e cobrem:

- comportamento das 6 funções corretas;
- diferença comportamental dos 18 bugs;
- integridade estrutural do repositório;
- roteamento dinâmico em `ise26.targets`;
- infraestrutura da integração DeepSeek sem chamada real.

O arquivo `tests/fixtures.py` concentra `DataFrame`s pequenos, sintéticos e controlados para apoiar essa validação interna. Esses dados não são dados reais, não são resultados experimentais e não substituem os testes gerados por LLM.

### Como rodar os testes internos

No Windows, o comando recomendado é:

```bash
python -m pytest
```

## Testes gerados por LLM

O script oficial de geração é:

```bash
python scripts/generate_llm_tests.py --dry-run
```

O modo padrão é seguro. Sem `--execute`, nenhuma chamada real é feita.

Os testes gerados por LLM não devem depender de `tests/fixtures.py`. Cada arquivo gerado deve construir seus próprios dados de teste, salvo decisão metodológica posterior registrada no protocolo.

Isso vale também para o prompt oficial de geração: ele deve orientar a LLM a criar os próprios `DataFrame`s sintéticos dentro de `test_generated.py`, sem importar fixtures internas do repositório.

### Gerar todas as funções em modo seguro

```bash
python scripts/generate_llm_tests.py --dry-run
```

### Gerar apenas uma função em modo seguro

```bash
python scripts/generate_llm_tests.py --dry-run --function-id F01
```

### Gerar apenas uma execução em modo seguro

```bash
python scripts/generate_llm_tests.py --dry-run --function-id F01 --run-id run_01
```

### Executar chamadas reais

Somente com confirmação explícita:

```bash
python scripts/generate_llm_tests.py --execute
```

### Sobrescrever artefatos já gerados

```bash
python scripts/generate_llm_tests.py --execute --function-id F01 --run-id run_01 --overwrite
```

## Artefatos salvos por execução

Cada chamada real salva arquivos em uma pasta como:

```text
experiments/generated_tests/F01/run_01/
```

Arquivos esperados:

- `system_prompt.txt`
- `prompt.txt`
- `request.json`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `status.json`

Além disso, o script atualiza:

```text
experiments/generated_tests/manifest.csv
```

## Como os hashes ajudam na reprodutibilidade

O fluxo de geração registra hashes SHA-256 de:

- prompt final;
- código da função correta;
- configuração do modelo;
- resposta textual da LLM.

Isso ajuda a verificar:

- se a mesma configuração foi usada;
- se o prompt-base mudou;
- se o código da função-alvo mudou;
- se a resposta salva corresponde exatamente ao que foi recebido.

## Resultados

A pasta `results/` guarda as saídas do runner experimental.

### Resultados brutos

Ficam em `results/raw/` e registram cada tentativa de executar uma suíte gerada contra uma implementação específica.

### Resultados resumidos

Ficam em `results/summary/` e agregam métricas por função, por execução e no geral.

### Atenção sobre placeholders

Enquanto os diretórios de `generated_tests/` ainda contiverem placeholders ou execuções sem geração real:

- os CSVs não representam resultado experimental real;
- os CSVs servem apenas para validar a infraestrutura;
- nenhum número deve ser apresentado como conclusão do estudo.

## Como instalar

Se quiser, crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como rodar o experimento

Fluxo mínimo recomendado:

1. instalar dependências;
2. rodar `python -m pytest`;
3. configurar `.env`;
4. revisar `experiments/protocol.md`;
5. rodar `python scripts/generate_llm_tests.py --dry-run`;
6. rodar `python scripts/generate_llm_tests.py --execute` somente quando a rodada oficial começar;
7. rodar `python scripts/run_generated_tests.py`;
8. rodar `python scripts/summarize_results.py`;
9. analisar os artefatos gerados.

## Guia rápido para quem está começando

### O que é Python neste projeto?

É a linguagem usada nas funções, nos testes e nos scripts experimentais.

### O que é Pandas?

É a biblioteca usada para trabalhar com tabelas em forma de `DataFrame`.

### O que é Pytest?

É a ferramenta usada para executar os testes automatizados.

### O que é uma função correta?

É a implementação oficial que representa o comportamento esperado.

### O que é uma função defeituosa?

É uma versão intencionalmente errada da mesma função, usada para o experimento.

### O que é um teste gerado por LLM?

É um arquivo de teste produzido pela DeepSeek a partir do prompt oficial congelado do estudo.

### O que uma pessoa iniciante pode fazer aqui?

Mesmo sem muita experiência, a pessoa pode:

- rodar os testes internos;
- revisar a estrutura de pastas;
- conferir se os arquivos gerados estão no lugar correto;
- verificar se há `status.json`, `metadata.json` e `raw_response.txt` para cada execução real;
- ajudar a manter a documentação consistente.

### Quais arquivos devem ser evitados sem orientação?

Sem alinhamento com o grupo, evite alterar:

- `src/ise26/implementations/correct.py`
- `src/ise26/implementations/buggy/`
- `src/ise26/metadata/functions.json`
- `src/ise26/metadata/bugs.json`
- `experiments/prompts/test_generation_prompt_template.md`
- `experiments/config/deepseek_v4_flash.json`
- `experiments/protocol.md`

## Fluxo recomendado de trabalho

1. instalar dependências;
2. rodar testes internos;
3. ler o protocolo;
4. configurar a chave local da DeepSeek;
5. executar `generate_llm_tests.py` em `dry-run`;
6. executar a geração real somente com `--execute`;
7. rodar o runner experimental;
8. gerar os resumos;
9. analisar apenas resultados de execuções reais.

## O que não fazer

- não inventar teste gerado por LLM;
- não inventar resultado experimental;
- não misturar teste manual com teste gerado por LLM;
- não editar manualmente o teste gerado depois da coleta oficial começar;
- não mudar o prompt no meio da rodada oficial;
- não mudar a configuração do modelo no meio da rodada oficial;
- não expor a chave `DEEPSEEK_API_KEY`;
- não tratar placeholder como dado real;
- não corrigir bugs intencionais;
- não alterar função correta depois que a coleta oficial começar.

## Comandos úteis

```bash
python -m pytest
```

```bash
python scripts/generate_llm_tests.py --dry-run
```

```bash
python scripts/generate_llm_tests.py --execute --function-id F01 --run-id run_01
```

```bash
python scripts/run_generated_tests.py
```

```bash
python scripts/summarize_results.py
```

## Próximos passos

Os próximos passos naturais do projeto são:

1. usar a configuração DeepSeek já congelada;
2. executar as `30` chamadas reais planejadas com rastreabilidade completa;
3. rodar o runner contra correta e bugs;
4. gerar os CSVs de resumo;
5. analisar estabilidade, executabilidade e detecção de defeitos com base em dados reais.

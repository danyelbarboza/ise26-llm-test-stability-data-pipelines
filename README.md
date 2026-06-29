# ISE26 — Avaliação de Testes Gerados por LLMs para Pipelines de Dados

## Visão geral

O repositório ISE26 foi criado para apoiar um experimento acadêmico em Engenharia de Software.

O foco do estudo é avaliar a estabilidade de testes automatizados gerados por LLMs para funções de transformação de dados em Python. Em vez de analisar exercícios simples, o projeto trabalha com funções que fazem limpeza, deduplicação, agregação, junção, validação de esquema e classificação de status.

Este repositório não existe para “mostrar um produto final”. Ele existe para dar suporte a uma coleta experimental controlada, rastreável e reproduzível.

## Objetivo do projeto

O objetivo do estudo é observar como suítes de teste geradas por LLMs se comportam quando executadas contra:

- a implementação correta de uma função;  
- três versões defeituosas dessa mesma função.

Com isso, o grupo pode analisar se os testes gerados:

- executam sem erro;
- passam quando a implementação está correta;
- detectam defeitos simples e plausíveis;
- variam muito entre execuções diferentes da mesma geração.

## Contexto acadêmico

O projeto foi organizado para um fluxo experimental típico de pesquisa:

1. definir funções-alvo com comportamento conhecido;
2. criar variantes defeituosas controladas;
3. gerar testes com uma LLM usando um prompt padronizado;
4. executar esses testes de forma sistemática;
5. registrar resultados brutos;
6. gerar resumos para análise posterior.

Por isso, o repositório separa claramente:

- código-fonte;
- metadados;
- testes internos;
- testes gerados por LLM;
- resultados brutos;
- resultados resumidos;
- scripts experimentais;
- protocolo do experimento.

## Resumo do experimento

O desenho experimental atual prevê:

- 6 funções corretas oficiais;
- 18 versões defeituosas intencionais;
- 5 execuções previstas por função para testes gerados por LLM;
- 1 módulo de roteamento dinâmico (`ise26.targets`) para trocar a implementação testada sem alterar o arquivo do teste.

No estado atual do repositório:

- a infraestrutura para essas 5 execuções já está pronta;
- as pastas de `generated_tests/` já existem;
- os testes gerados reais ainda não foram adicionados;
- os CSVs existentes servem apenas para validar a infraestrutura com placeholders.

Quando a fase experimental oficial começar, cada suíte gerada por LLM deverá ser executada contra:

- a implementação correta da função;
- `BUG01`;
- `BUG02`;
- `BUG03`.

## Como o experimento funciona

De forma simples, o fluxo é este:

1. a equipe gera um teste com uma LLM usando o prompt oficial;
2. a resposta bruta da LLM é salva para rastreabilidade;
3. o código Python extraído vai para a pasta correta em `experiments/generated_tests/`;
4. o script `run_generated_tests.py` executa a suíte contra a versão correta e contra os bugs;
5. o script `summarize_results.py` gera arquivos CSV de resumo;
6. a análise acadêmica acontece depois, com base em resultados reais.

## Estrutura do repositório

```text
ISE26/
├── README.md
├── requirements.txt
├── pytest.ini
├── src/
│   ├── README.md
│   └── ise26/
│       ├── README.md
│       ├── targets.py
│       ├── implementations/
│       │   ├── README.md
│       │   ├── correct.py
│       │   └── buggy/
│       │       └── README.md
│       └── metadata/
│           └── README.md
├── tests/
│   └── README.md
├── experiments/
│   ├── README.md
│   ├── protocol.md
│   ├── prompts/
│   │   └── README.md
│   ├── generated_tests/
│   │   └── README.md
│   └── raw_responses/
├── results/
│   ├── README.md
│   ├── raw/
│   │   └── README.md
│   └── summary/
│       └── README.md
└── scripts/
    └── README.md
```

## Tecnologias usadas

- Python 3.11+
- Pandas
- Pytest
- JSON
- CSV

## Requisitos

Para trabalhar no projeto, o ideal é ter:

- Python 3.11 ou superior;
- `pip`;
- terminal no Windows PowerShell, Prompt de Comando ou terminal compatível;
- noções básicas de estrutura de pastas e arquivos.

## Funções corretas

As 6 funções corretas oficiais estão em `src/ise26/implementations/correct.py`.

| ID | Função | Papel no experimento |
|---|---|---|
| F01 | `clean_customer_names` | Padroniza nomes de clientes sem alterar o `DataFrame` original |
| F02 | `deduplicate_events` | Remove duplicatas mantendo o evento mais recente |
| F03 | `calculate_monthly_revenue` | Calcula receita mensal ignorando cancelamentos |
| F04 | `join_customers_orders` | Faz junção completa entre clientes e pedidos com classificação de status |
| F05 | `validate_schema` | Valida colunas e tipos lógicos esperados |
| F06 | `classify_payment_status` | Classifica pagamentos como válidos, atrasados, pendentes ou inválidos |

### Descrição resumida das 6 funções

1. `clean_customer_names`
   Limpa nomes, remove espaços extras, converte para minúsculas, remove acentos e transforma vazio/nulo em valor ausente.

2. `deduplicate_events`
   Mantém o registro mais recente por `event_id`, trata timestamp inválido como mais antigo e preserva `event_id` nulo.

3. `calculate_monthly_revenue`
   Soma os valores por mês (`YYYY-MM`), ignora pedidos cancelados e trata valores inválidos de `amount` como zero.

4. `join_customers_orders`
   Faz `full outer join`, preserva faltantes dos dois lados, trata chave nula explicitamente e cria `record_status`.

5. `validate_schema`
   Confere se as colunas obrigatórias existem e se os tipos lógicos estão coerentes com o esquema informado.

6. `classify_payment_status`
   Classifica cada linha como `invalid`, `paid_on_time`, `paid_late`, `overdue` ou `pending`.

## Versões defeituosas

Cada função correta possui 3 variantes defeituosas intencionais, totalizando 18 bugs.

Esses arquivos ficam em `src/ise26/implementations/buggy/`.

### Tabela dos 18 bugs

| Função | Bug | Arquivo | Descrição resumida |
|---|---|---|---|
| F01 | BUG01 | `f01_bug01.py` | Não trata nulos corretamente |
| F01 | BUG02 | `f01_bug02.py` | Não remove acentos |
| F01 | BUG03 | `f01_bug03.py` | Não remove espaços extras |
| F02 | BUG01 | `f02_bug01.py` | Mantém o primeiro evento em vez do mais recente |
| F02 | BUG02 | `f02_bug02.py` | Remove linhas com `event_id` nulo |
| F02 | BUG03 | `f02_bug03.py` | Ordena timestamp como string |
| F03 | BUG01 | `f03_bug01.py` | Soma pedidos cancelados |
| F03 | BUG02 | `f03_bug02.py` | Não trata `amount` inválido/nulo como zero |
| F03 | BUG03 | `f03_bug03.py` | Agrupa por dia em vez de mês |
| F04 | BUG01 | `f04_bug01.py` | Usa `inner join` em vez de `full outer join` |
| F04 | BUG02 | `f04_bug02.py` | Não cria `record_status` |
| F04 | BUG03 | `f04_bug03.py` | Classifica incorretamente linhas sem correspondência ou com chave nula |
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

São variantes intencionais com defeitos simples e plausíveis. Elas existem para verificar se os testes gerados conseguem detectar falhas.

### Testes internos

São os testes escritos manualmente pela equipe do projeto para validar a base do repositório. Eles não são os dados experimentais principais.

### Testes gerados por LLM

São testes que ainda serão produzidos externamente, usando uma LLM e o prompt padronizado do projeto.

### Resultados brutos

São os registros detalhados de cada execução do runner experimental.

### Resultados resumidos

São agregações dos resultados brutos por função, por execução e no geral.

## Testes internos

Os testes internos ficam na pasta `tests/` e servem para:

- verificar se as funções corretas continuam corretas;
- verificar se os bugs continuam diferentes da referência;
- verificar integridade do repositório;
- validar a infraestrutura experimental.

### Como rodar os testes

Comando geral:

```bash
python -m pytest
```

Esse é o comando recomendado no Windows, porque em alguns ambientes o executável `pytest` pode não estar disponível diretamente no `PATH`.

## Testes gerados por LLM

Os testes gerados por LLM deverão ser colocados em:

```text
experiments/generated_tests/FXX/run_YY/test_generated.py
```

Exemplos:

- `experiments/generated_tests/F01/run_01/test_generated.py`
- `experiments/generated_tests/F01/run_02/test_generated.py`
- `experiments/generated_tests/F06/run_05/test_generated.py`

Esses arquivos:

- devem conter apenas testes realmente gerados pela LLM;
- não devem ser inventados para “preencher” pasta;
- devem ser rastreáveis até a resposta original salva em `experiments/raw_responses/`.

## Resultados

A pasta `results/` guarda saídas de execução.

### Resultados brutos

Ficam em `results/raw/` e registram cada tentativa de executar uma suíte gerada contra uma implementação.

### Resultados resumidos

Ficam em `results/summary/` e trazem agregações para facilitar leitura.

### Atenção sobre placeholders

Enquanto os arquivos `test_generated.py` ainda forem placeholders, os CSVs produzidos pelos scripts:

- não representam experimento real;
- não devem ser usados como evidência acadêmica;
- servem apenas para validar a infraestrutura.

No estado atual do repositório, este é exatamente o caso.

## Como instalar

Se necessário, crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente no Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como rodar os testes

### Testes internos

```bash
python -m pytest
```

### Runner experimental

```bash
python scripts/run_generated_tests.py
```

### Sumarização dos resultados

```bash
python scripts/summarize_results.py
```

## Como rodar o experimento

Fluxo mínimo quando a fase experimental com LLM começar:

1. garantir que a base interna está passando em `python -m pytest`;
2. ler `experiments/protocol.md`;
3. usar o prompt oficial em `experiments/prompts/test_generation_prompt_template.md`;
4. salvar a resposta bruta da LLM;
5. extrair o código Python para a pasta certa em `experiments/generated_tests/`;
6. rodar `python scripts/run_generated_tests.py`;
7. rodar `python scripts/summarize_results.py`;
8. analisar os CSVs gerados.

## Como interpretar os arquivos gerados

### `results/raw/generated_tests_results.csv`

Cada linha representa uma execução de uma suíte contra uma implementação específica.

### `results/summary/summary_by_function.csv`

Resume os resultados agrupando por função.

### `results/summary/summary_by_run.csv`

Resume os resultados agrupando por execução (`run_01`, `run_02`, etc.).

### `results/summary/summary_overall.csv`

Resume o cenário geral.

## Uso de `ISE26_TARGET_MODULE`

O módulo `src/ise26/targets.py` permite que o mesmo teste importado de `ise26.targets` execute contra implementações diferentes.

Exemplo conceitual:

```python
from ise26.targets import clean_customer_names
```

Exemplo de uso com a implementação correta:

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.correct"
python -m pytest experiments/generated_tests/F01/run_01/test_generated.py
```

Exemplo de uso com um bug:

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.buggy.f01_bug01"
python -m pytest experiments/generated_tests/F01/run_01/test_generated.py
```

## Placeholders quando ainda não há testes gerados por LLM

O repositório já traz a estrutura de pastas pronta para o experimento, mas isso não significa que os testes foram gerados.

Enquanto os arquivos de `generated_tests/` ainda forem placeholders:

- o runner deve continuar funcionando de forma controlada;
- os CSVs devem ser lidos apenas como saída técnica da infraestrutura;
- nenhum resultado deve ser tratado como dado experimental real.

Atualmente, o repositório ainda está nessa fase de preparação estrutural.

## Guia rápido para quem está começando

### O que é Python neste projeto?

É a linguagem usada para implementar as funções, os testes e os scripts experimentais.

### O que é Pandas?

É a biblioteca usada para trabalhar com tabelas em forma de `DataFrame`.

### O que é Pytest?

É a ferramenta usada para rodar os testes automáticos do projeto.

### O que é uma função correta?

É a implementação oficial que representa o comportamento esperado.

### O que é uma função defeituosa?

É uma versão intencionalmente errada, criada para o experimento.

### O que é um teste gerado por LLM?

É um arquivo de teste produzido por um modelo de linguagem, a partir do prompt padronizado do estudo.

### O que alguém iniciante pode fazer aqui?

Mesmo sem muita experiência, a pessoa pode:

- ler os READMEs das pastas;
- rodar os testes internos;
- conferir se a estrutura de arquivos está correta;
- ajudar a organizar respostas brutas da LLM;
- revisar se os nomes e caminhos seguem o protocolo.

### Quais arquivos devem ser evitados sem orientação?

Quem está começando deve evitar alterar sem acompanhamento:

- `src/ise26/implementations/correct.py`
- `src/ise26/implementations/buggy/`
- `src/ise26/metadata/functions.json`
- `src/ise26/metadata/bugs.json`
- `experiments/protocol.md`
- `experiments/prompts/test_generation_prompt_template.md`

## Fluxo recomendado de trabalho

1. instalar dependências;
2. rodar testes internos com `python -m pytest`;
3. ler o protocolo experimental;
4. gerar testes com a LLM usando o prompt padrão;
5. salvar a resposta bruta da LLM;
6. salvar o teste na pasta correta;
7. rodar o experimento;
8. gerar resumos;
9. analisar os resultados.

## O que não fazer

- não inventar teste gerado por LLM;
- não inventar resultado experimental;
- não alterar função correta depois que a fase oficial do experimento começar;
- não “corrigir” bugs intencionais;
- não mudar o prompt no meio da geração oficial;
- não apagar CSVs sem registrar a decisão;
- não misturar teste manual com teste gerado por LLM;
- não tratar placeholders como dados reais;
- não publicar números experimentais antes de executar suítes reais.

## Comandos úteis

```bash
python -m pytest
```

```bash
python scripts/run_generated_tests.py
```

```bash
python scripts/summarize_results.py
```

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.correct"
```

```bash
$env:ISE26_TARGET_MODULE = "ise26.implementations.buggy.f03_bug02"
```

## O que não deve ser feito

Este projeto tem algumas proibições importantes:

- não inventar testes gerados por LLM;
- não inventar resultados;
- não apresentar CSV com placeholder como resultado do estudo;
- não alterar o comportamento oficial das funções sem atualizar testes e documentação;
- não mudar a estrutura do experimento sem registrar isso no protocolo.

## Próximos passos

Os próximos passos naturais do projeto são:

1. definir oficialmente a LLM usada;
2. congelar o prompt final de geração;
3. gerar as suítes reais;
4. executar as suítes contra funções corretas e defeituosas;
5. analisar estabilidade, executabilidade e detecção de defeitos;
6. produzir material acadêmico com base em dados reais.

## Orientações para membros iniciantes do grupo

- Comece lendo este README e os READMEs das pastas.
- Rode `python -m pytest` antes de mexer em qualquer coisa.
- Se tiver dúvida sobre um arquivo, veja primeiro a pasta em que ele está.
- Antes de alterar lógica, confirme se aquilo faz parte da infraestrutura ou do desenho experimental.
- Se um resultado parecer “bonito demais”, desconfie e verifique se ele não veio de placeholder.
- Em caso de dúvida, prefira registrar a incerteza em vez de assumir que algo é resultado real.

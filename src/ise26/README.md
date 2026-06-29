# README do pacote `ise26`

## Papel do pacote

O pacote `ise26` concentra o núcleo do repositório.

Ele organiza, em um único lugar:

- as implementações corretas;
- as implementações defeituosas;
- os metadados das funções e dos bugs;
- a superfície estável de importação em `targets.py`;
- a infraestrutura de geração reproduzível em `llm/`.

## Subpastas principais

### `implementations/`

Guarda as funções corretas e as versões defeituosas.

### `metadata/`

Guarda os arquivos JSON que descrevem formalmente quais funções e bugs fazem parte do experimento.

### `llm/`

Guarda a infraestrutura de integração com a DeepSeek:

- cliente compatível com a API oficial;
- montagem do prompt;
- extração mecânica de código;
- utilitários de reprodutibilidade.

### `targets.py`

Expõe sempre os mesmos nomes públicos para os testes gerados, enquanto escolhe dinamicamente qual implementação real será usada.

## Relação entre `implementations`, `metadata`, `llm` e `targets.py`

- `implementations/correct.py` contém a referência oficial de comportamento.
- `implementations/buggy/` contém os 18 bugs intencionais.
- `metadata/functions.json` lista as funções oficiais e o comportamento esperado usado na montagem do prompt.
- `metadata/bugs.json` lista os bugs oficiais.
- `llm/` prepara chamadas independentes, rastreáveis e sem histórico.
- `targets.py` usa `ISE26_TARGET_MODULE` para expor a implementação correta ou uma variante defeituosa sem alterar o arquivo do teste.

## Cuidados importantes

- Não altere o comportamento de uma função sem atualizar testes e documentação.
- Não altere a infraestrutura `llm/` sem revisar o protocolo experimental.
- Não registre a chave da API em arquivos do repositório.
- Não execute código automaticamente ao importar módulos.
- Não adicione `print` nas funções do experimento.

# README do pacote `ise26`

## Papel do pacote

O pacote `ise26` concentra o núcleo do repositório.

Ele existe para organizar, em um único lugar:

- as implementações corretas;
- as implementações defeituosas;
- os metadados que descrevem funções e bugs;
- o módulo `targets.py`, que serve de ponto estável de importação para testes gerados por LLM.

## Subpastas principais

### `implementations/`

Guarda as funções corretas e as versões defeituosas.

### `metadata/`

Guarda arquivos JSON que descrevem formalmente quais funções e bugs fazem parte do experimento.

### `targets.py`

Não é uma pasta, mas é um arquivo muito importante. Ele decide dinamicamente qual implementação será exposta para os testes gerados.

## Relação entre `implementations`, `metadata` e `targets.py`

- `implementations/correct.py` contém a referência oficial de comportamento.
- `implementations/buggy/` contém os 18 bugs intencionais.
- `metadata/functions.json` lista as funções oficiais.
- `metadata/bugs.json` lista os bugs oficiais.
- `targets.py` lê a variável de ambiente `ISE26_TARGET_MODULE` e expõe as funções do módulo escolhido.

## Cuidados importantes

- Não altere o comportamento de uma função sem atualizar testes e documentação.
- Se uma mudança afetar a identidade experimental de uma função ou bug, os arquivos de metadados também precisam ser revisados.
- Não execute código automaticamente ao importar módulos.
- Não adicione `print` nas funções do experimento.

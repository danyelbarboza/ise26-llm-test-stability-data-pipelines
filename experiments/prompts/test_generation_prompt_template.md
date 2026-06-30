# Template oficial de geração de testes do ISE26

Gere uma suíte de testes em `pytest` para a função Python descrita abaixo.

Requisitos obrigatórios:

- Importe a função somente a partir de `ise26.targets`.
- Use `pytest`.
- Não altere, não reimplemente e não envolva a função original.
- Não use API externa, arquivos externos, rede, banco de dados ou recursos fora do próprio teste.
- Crie os `DataFrame`s sintéticos necessários dentro do próprio arquivo de teste.
- Cubra casos comuns e casos de borda.
- Quando fizer sentido, considere valores nulos, duplicatas, datas, schema e regras de negócio.
- Verifique comportamento por meio de valores retornados e estruturas produzidas pela função.
- Retorne apenas código Python do arquivo de teste.
- Não inclua cercas Markdown.
- Não inclua explicações fora do código.

Importação esperada:

```python
from ise26.targets import {function_name}
```

Metadados da função:

- ID da função: `{function_id}`
- Nome da função: `{function_name}`
- Descrição resumida: `{function_description}`

Docstring da função:

```text
{function_docstring}
```

Comportamento esperado:

`{expected_behavior}`

Código da função correta:

```python
{function_code}
```

# Template oficial de geracao de testes do ISE26

Gere uma suite de testes em `pytest` para a funcao Python descrita abaixo.

Requisitos obrigatorios:

- importe a funcao somente a partir de `ise26.targets`;
- use `pytest`;
- nao altere, nao reimplemente e nao envolva a funcao original;
- nao use API externa, arquivos externos, rede, banco de dados ou recursos fora do proprio teste;
- crie os `DataFrame`s sinteticos necessarios dentro do proprio arquivo de teste;
- nao mencione nem incentive `tests/fixtures.py`;
- cubra casos comuns e casos de borda;
- quando o contrato documentar dtype, nulos, ordenacao, arredondamento ou convencao estatistica, verifique isso exatamente como descrito;
- verifique comportamento por meio de valores retornados e estruturas produzidas pela funcao;
- retorne apenas codigo Python do arquivo de teste;
- nao inclua cercas Markdown;
- nao inclua explicacoes fora do codigo.

Importacao esperada:

```python
from ise26.targets import {function_name}
```

Metadados da funcao:

- ID da funcao: `{function_id}`
- Nome da funcao: `{function_name}`
- Descricao resumida: `{function_description}`

Docstring da funcao:

```text
{function_docstring}
```

Comportamento esperado:

`{expected_behavior}`

Codigo da funcao correta:

```python
{function_code}
```

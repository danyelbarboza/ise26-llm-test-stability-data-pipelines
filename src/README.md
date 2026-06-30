# Pasta `src`

Esta pasta contém o código-fonte principal do projeto.

## O que fica aqui

O pacote Python `ise26`, que reúne:

- as implementações corretas;
- as implementações defeituosas;
- os metadados do experimento;
- o módulo de roteamento dinâmico usado pelos testes gerados por LLM;
- a infraestrutura `llm/`, responsável pela geração rastreável;
- os helpers de caminho e separação por modelo/experimento.

## O que uma pessoa iniciante precisa saber

- `src/` existe para separar código-fonte, testes, scripts e documentação;
- alterar `implementations/` ou `metadata/` pode exigir atualização de testes e documentação;
- alterar `llm/` afeta a rastreabilidade das gerações;
- `experiment_paths.py` centraliza a lógica de caminhos por modelo e por `experiment_id`.

## Como os módulos são importados

Nos testes internos, o projeto usa `pythonpath = src` em `pytest.ini`.

Nos scripts que precisam importar `ise26` diretamente, o caminho `src/` é adicionado explicitamente quando necessário para manter o comando simples no terminal.

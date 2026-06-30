# README da pasta `metadata`

## O que esta pasta contem

Esta pasta contem metadados estruturados do experimento.

Os dois arquivos principais sao:

- `functions.json`
- `bugs.json`

Na configuracao atual do repositorio, os arquivos da raiz cobrem 10 funcoes corretas e 30 bugs intencionais. As copias em `exp_6_functions/`, `exp_10_functions/` e `exp_final_10_functions/` preservam o recorte de cada experimento.

## Papel de `functions.json`

Esse arquivo descreve as funcoes corretas oficiais do estudo.

Ele ajuda a responder perguntas como:

- quais funcoes fazem parte do experimento?
- qual e o nome oficial de cada funcao?
- em qual modulo esta a implementacao correta?
- qual e a descricao resumida da funcao?

## Papel de `bugs.json`

Esse arquivo descreve as versoes defeituosas oficiais do estudo.

Ele ajuda a responder perguntas como:

- quais bugs existem?
- a qual funcao cada bug pertence?
- em qual modulo esta cada bug?
- qual e a descricao resumida do defeito?

## Como esses arquivos ajudam na rastreabilidade

Os metadados sao uteis para:

- scripts experimentais;
- documentacao;
- revisao do desenho experimental;
- checagens de integridade do repositorio.

Eles reduzem a chance de alguem confundir nomes de funcoes, modulos ou bugs.

## O que atualizar quando uma funcao ou bug muda

Se houver mudanca oficial em funcao ou bug, revise:

- `functions.json`
- `bugs.json`
- testes internos
- README principal
- READMEs das pastas relevantes
- protocolo experimental, se necessario

Se a mudanca for apenas textual, ainda assim vale conferir se os nomes oficiais continuam coerentes.

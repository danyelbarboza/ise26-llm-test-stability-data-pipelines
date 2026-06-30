# README da pasta `metadata`

## O que esta pasta contém

Esta pasta contém metadados estruturados do experimento.

Os dois arquivos principais são:

- `functions.json`
- `bugs.json`

Na configuração atual do repositório, os arquivos da raiz cobrem 10 funções corretas e 30 bugs intencionais. As cópias em `exp_6_functions/` e `exp_10_functions/` preservam o recorte de cada experimento.

## Papel de `functions.json`

Esse arquivo descreve as funções corretas oficiais do estudo.

Ele ajuda a responder perguntas como:

- quais funções fazem parte do experimento?
- qual é o nome oficial de cada função?
- em qual módulo está a implementação correta?
- qual é a descrição resumida da função?

## Papel de `bugs.json`

Esse arquivo descreve as versões defeituosas oficiais do estudo.

Ele ajuda a responder perguntas como:

- quais bugs existem?
- a qual função cada bug pertence?
- em qual módulo está cada bug?
- qual é a descrição resumida do defeito?

## Como esses arquivos ajudam na rastreabilidade

Os metadados são úteis para:

- scripts experimentais;
- documentação;
- revisão do desenho experimental;
- checagens de integridade do repositório.

Eles reduzem a chance de alguém confundir nomes de funções, módulos ou bugs.

## O que atualizar quando uma função ou bug muda

Se houver mudança oficial em função ou bug, revise:

- `functions.json`
- `bugs.json`
- testes internos
- README principal
- READMEs das pastas relevantes
- protocolo experimental, se necessário

Se a mudança for apenas textual, ainda assim vale conferir se os nomes oficiais continuam coerentes.

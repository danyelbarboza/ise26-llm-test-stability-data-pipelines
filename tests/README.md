# README da pasta `tests`

## O que esta pasta contém

Esta pasta contém os testes internos do repositório.

Eles foram escritos manualmente pela equipe do projeto para aumentar a confiança na base experimental antes da fase principal com testes gerados por LLM.

## Diferença entre testes internos e testes gerados por LLM

### Testes internos

São testes de manutenção e validação da base do projeto.

### Testes gerados por LLM

São os testes produzidos pela DeepSeek como parte do experimento oficial e armazenados em `experiments/generated_tests/`.

## Por que os testes internos existem

Eles servem para:

- validar as 6 funções corretas;
- verificar se os 18 bugs continuam diferentes da referência;
- confirmar integridade estrutural do repositório;
- validar `ise26.targets`;
- validar a infraestrutura DeepSeek sem usar a API real.

## Papel de `tests/fixtures.py`

O arquivo `tests/fixtures.py` reúne pequenos `DataFrame`s sintéticos usados pelos testes internos.

Esses dados:

- são artificiais e didáticos;
- não vêm de fonte real;
- existem apenas para validação interna da base;
- não são resultados experimentais;
- não devem ser confundidos com testes gerados por LLM.

Os testes gerados por LLM devem construir seus próprios dados dentro do arquivo gerado, salvo se o protocolo do experimento mudar no futuro.

## Como rodar

No Windows, use:

```bash
python -m pytest
```

## O que significa um teste passar

Quando um teste passa, isso significa que o comportamento observado foi compatível com o comportamento esperado daquele cenário.

## O que significa um teste falhar

Quando um teste falha, isso indica:

- mudança de comportamento;
- regressão;
- expectativa incorreta no teste;
- ou problema de ambiente.

## Aviso importante

Esses testes não são os dados experimentais principais do estudo.

Eles existem para dar suporte à base experimental e à infraestrutura de geração e execução.

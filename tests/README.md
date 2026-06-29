# README da pasta `tests`

## O que esta pasta contém

Esta pasta contém os testes internos do repositório.

Eles foram escritos manualmente pela equipe do projeto para aumentar a confiança na base experimental antes da fase principal com testes gerados por LLM.

## Diferença entre testes internos e testes gerados por LLM

### Testes internos

São testes de manutenção e validação da base do projeto.

### Testes gerados por LLM

São os testes que ainda serão produzidos como parte do experimento oficial e ficarão em `experiments/generated_tests/`.

## Por que os testes internos existem

Eles servem para:

- validar as 6 funções corretas;
- verificar se os 18 bugs continuam diferentes da referência;
- confirmar integridade de assinaturas e organização;
- reduzir risco de congelar uma base inconsistente.

## Como rodar

No Windows, use:

```bash
python -m pytest
```

## O que significa um teste passar

Quando um teste passa, isso significa que o comportamento observado foi compatível com o comportamento esperado definido para aquele cenário.

## O que significa um teste falhar

Quando um teste falha, isso significa que:

- o comportamento mudou;
- existe uma regressão;
- o teste estava com expectativa incorreta;
- ou houve algum problema de ambiente.

## Aviso importante

Esses testes não são os dados experimentais principais do estudo.

Eles existem para dar suporte ao experimento, não para substituir os testes gerados por LLM.

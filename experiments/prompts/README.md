# Pasta `experiments/prompts`

Esta pasta guarda os prompts usados para a geração de testes com LLM.

## O que é o prompt padrão

O prompt padrão é o texto-base usado para pedir ao modelo que produza uma suíte de testes em `pytest`.

Esse prompt deve instruir a LLM a:

- importar somente de `ise26.targets`;
- criar os próprios `DataFrame`s sintéticos dentro de `test_generated.py`;
- não depender de `tests/fixtures.py`, que é exclusivo dos testes internos;
- não alterar a função original;
- cobrir casos comuns e de borda.

## Por que o mesmo prompt deve ser usado

Manter o mesmo prompt reduz variação desnecessária entre execuções e melhora a comparabilidade experimental.

## Importância de manter o prompt congelado

Se a coleta oficial já tiver começado, mudar o prompt no meio do processo pode comprometer a análise de estabilidade.

## Como registrar alterações

Se o prompt precisar mudar:

- registre a mudança no protocolo;
- atualize a documentação;
- deixe claro em qual rodada a nova versão passou a valer;
- não misture resultados de prompts diferentes sem anotação explícita.

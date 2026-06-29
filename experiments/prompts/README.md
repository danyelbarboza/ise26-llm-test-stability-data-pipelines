# README da pasta `prompts`

## O que esta pasta contém

Esta pasta guarda os prompts usados para a geração de testes com LLM.

## O que é o prompt padrão

O prompt padrão é o texto-base usado para pedir à LLM que produza uma suíte de testes no formato esperado pelo projeto.

## Por que o mesmo prompt deve ser usado

Manter o mesmo prompt reduz variação desnecessária entre execuções e ajuda a preservar comparabilidade experimental.

## Importância de manter o prompt congelado

Se o grupo começar uma coleta oficial, mudar o prompt no meio do processo pode comprometer a comparação entre execuções.

## Como registrar alterações

Se o prompt precisar mudar:

- registre a mudança no protocolo;
- deixe claro quando a nova versão passou a valer;
- evite misturar resultados de versões diferentes sem anotação.

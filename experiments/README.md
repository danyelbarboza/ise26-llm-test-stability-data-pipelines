# Pasta `experiments`

Esta pasta concentra o protocolo experimental, os prompts, as configurações de modelo e os testes gerados por LLM.

## O que fica aqui

- `protocol.md`: regras oficiais do experimento;
- `prompts/`: prompt padrão e variações documentadas;
- `config/`: arquivos JSON com parâmetros do modelo;
- `generated_tests/`: saídas geradas pela LLM, separadas por modelo;
- `raw_responses/`: resposta bruta, quando usada como artefato de rastreabilidade.

## Organização por modelo

Os artefatos gerados por cada modelo devem ficar isolados em subpastas próprias. Hoje o repositório já separa:

- `experiments/generated_tests/deepseek_v4_flash/`
- `experiments/generated_tests/deepseek_v4_pro/`

Isso evita misturar a rodada oficial do Flash com futuras rodadas do Pro.

## Regras importantes

- não editar manualmente os testes gerados, salvo quando o protocolo permitir;
- não inventar testes para preencher pastas vazias;
- não mudar o prompt oficial no meio de uma rodada;
- não misturar artefatos de modelos diferentes no mesmo diretório.

## Para iniciantes

Se você acabou de entrar no projeto, comece por:

1. ler `protocol.md`;
2. ler `README.md` na raiz;
3. verificar `config/` para entender qual modelo está sendo usado;
4. olhar `generated_tests/` para entender como cada execução é salva.

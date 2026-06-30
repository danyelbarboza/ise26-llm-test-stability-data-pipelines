# Pasta `experiments`

Esta pasta concentra o protocolo experimental, os prompts, as configurações de modelo e os testes gerados por LLM.

## O que fica aqui

- `protocol.md`: regras oficiais do experimento;
- `prompts/`: prompt padrão e documentação do texto-base;
- `config/`: arquivos JSON com parâmetros do modelo e do experimento;
- `generated_tests/`: saídas geradas pela LLM, separadas por `experiment_id` e por modelo.

## Organização por experimento e por modelo

O repositório mantém duas trilhas principais:

- `exp_6_functions`: baseline histórica de 6 funções;
- `exp_10_functions`: expansão nova de 10 funções, com 50 suítes planejadas por modelo e 200 execuções-alvo por modelo.

Dentro de cada experimento, os artefatos são separados por modelo:

- `deepseek_v4_flash`;
- `deepseek_v4_pro`.

Isso evita misturar Flash com Pro e evita misturar a baseline histórica com a expansão nova.

## Regras importantes

- não editar manualmente os testes gerados, salvo quando o protocolo permitir;
- não inventar testes para preencher pastas vazias;
- não mudar o prompt oficial no meio de uma rodada;
- não misturar artefatos de modelos diferentes no mesmo diretório;
- não misturar artefatos de experimentos diferentes no mesmo diretório.

## Para iniciantes

Se você acabou de entrar no projeto, comece por:

1. ler `protocol.md`;
2. ler o `README.md` da raiz;
3. verificar `config/` para entender qual modelo e qual `experiment_id` estão ativos;
4. olhar `generated_tests/` para entender como cada execução é salva.

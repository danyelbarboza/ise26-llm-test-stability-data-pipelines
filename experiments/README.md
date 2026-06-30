# Pasta `experiments`

Esta pasta concentra o protocolo experimental, os prompts, as configuracoes de modelo e os testes gerados por LLM.

## O que fica aqui

- `protocol.md`: regras oficiais do experimento;
- `prompts/`: prompt padrao e documentacao do texto-base;
- `config/`: arquivos JSON com parametros do modelo e do experimento;
- `generated_tests/`: saidas geradas pela LLM, separadas por `experiment_id` e por modelo.

## Trilhas experimentais

- `exp_6_functions`: baseline historica usada so para validacao interna;
- `exp_10_functions`: expansao intermediaria, hoje tratada como `deprecated`;
- `exp_final_10_functions`: experimento final do artigo.

Cada experimento tem sua propria arvore de artefatos e nao deve ser misturado com outro.

## Organizacao por modelo

Dentro de cada experimento, os artefatos sao separados por modelo:

- `deepseek_v4_flash`;
- `deepseek_v4_pro`.

Isso evita misturar Flash com Pro e evita misturar os recortes historicos com o experimento final.

## Regras importantes

- nao editar manualmente os testes gerados, salvo quando o protocolo permitir;
- nao inventar testes para preencher pastas vazias;
- nao mudar o prompt oficial no meio de uma rodada;
- nao misturar artefatos de modelos diferentes no mesmo diretorio;
- nao misturar artefatos de experimentos diferentes no mesmo diretorio;
- `tests/fixtures.py` e exclusivo dos testes internos.

## Para iniciantes

Se voce acabou de entrar no projeto, comece por:

1. ler `protocol.md`;
2. ler o `README.md` da raiz;
3. verificar `config/` para entender qual modelo e qual `experiment_id` estao ativos;
4. olhar `generated_tests/` para entender como cada execucao e salva.

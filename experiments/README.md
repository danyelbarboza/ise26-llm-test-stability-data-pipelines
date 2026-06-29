# README da pasta `experiments`

## Papel desta pasta

Esta pasta reúne os artefatos diretamente ligados à execução experimental.

Aqui ficam:

- o protocolo do experimento;
- a configuração oficial do modelo;
- os prompts usados para geração;
- os testes gerados por LLM;
- a área reservada para respostas brutas legadas ou auxiliares.

## Papel do protocolo

O arquivo `protocol.md` descreve as regras do experimento, incluindo:

- provedor oficial;
- modelo oficial;
- parâmetros congelados;
- regras de rastreabilidade;
- política de edição manual;
- métricas e limitações.

## Papel da configuração

A pasta `config/` guarda a configuração oficial usada pelo gerador.

No estado atual, o arquivo principal é:

```text
experiments/config/deepseek_v4_flash.json
```

## Papel dos prompts

A pasta `prompts/` guarda o prompt-base oficial.

Esse prompt deve permanecer estável durante a rodada oficial, porque mudar o texto no meio da coleta prejudica a comparabilidade entre execuções.

## Papel dos testes gerados

A pasta `generated_tests/` recebe:

- o `test_generated.py`;
- o prompt salvo;
- a resposta bruta salva;
- os metadados;
- o status da execução.

## Como salvar respostas de LLM

No fluxo oficial atual, a resposta bruta deve ser salva dentro da própria pasta da execução:

```text
experiments/generated_tests/F01/run_01/raw_response.txt
```

A pasta `raw_responses/` pode existir por histórico ou apoio manual, mas não é o caminho oficial da nova infraestrutura automatizada.

## Como organizar múltiplas execuções

Cada função possui cinco execuções planejadas:

- `F01/run_01/`
- `F01/run_02/`
- `F01/run_03/`
- `F01/run_04/`
- `F01/run_05/`

O mesmo padrão vale para `F02` até `F06`.

## Regra sobre edição manual

O teste gerado não deve ser corrigido manualmente na coleta oficial.

Se a resposta vier em Markdown, a extração do código deve ser mecânica. Se o código vier com sintaxe inválida, ele continua sendo salvo como artefato real da geração.

## Cuidado com rastreabilidade

Nunca deixe um `test_generated.py` sem ligação clara com:

- o prompt utilizado;
- a resposta bruta recebida;
- a configuração oficial do modelo;
- os hashes registrados em `metadata.json`.

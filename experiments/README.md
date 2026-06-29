# README da pasta `experiments`

## Papel desta pasta

Esta pasta reúne os artefatos diretamente ligados à execução experimental.

Aqui ficam:

- o protocolo do experimento;
- os prompts usados para geração;
- os testes gerados por LLM;
- as respostas brutas das LLMs.

## Papel do protocolo

O arquivo `protocol.md` descreve as regras do experimento.

Ele deve orientar:

- como gerar testes;
- como salvar respostas;
- como nomear arquivos;
- como executar a infraestrutura;
- como registrar limitações.

## Papel dos prompts

A pasta `prompts/` guarda o prompt padrão de geração. Ele é importante para manter consistência entre execuções.

## Papel dos testes gerados

A pasta `generated_tests/` recebe os arquivos `test_generated.py` produzidos a partir das respostas da LLM.

## Estado atual desta pasta de experimentos

No momento:

- a estrutura do experimento já está criada;
- o protocolo já está definido;
- o prompt padrão já existe;
- os testes gerados reais ainda não foram adicionados;
- a rastreabilidade deve começar a valer assim que a coleta oficial começar.

## Como salvar respostas de LLM

As respostas brutas devem ser salvas em `experiments/raw_responses/`.

Exemplo:

```text
F01_run_01_response.txt
F01_run_02_response.md
```

## Como organizar múltiplas execuções

Cada função possui várias execuções previstas, como:

- `F01/run_01/`
- `F01/run_02/`
- `F01/run_03/`

Esse padrão deve ser seguido para todas as funções.

## Regra sobre edição manual

O ideal é não editar manualmente o teste gerado depois da resposta da LLM.

Se houver algum caso excepcional permitido pelo protocolo, isso deve ser registrado de forma clara.

## Cuidado com rastreabilidade

Nunca deixe um `test_generated.py` sem ligação rastreável com a resposta bruta que o originou.

# Protocolo experimental ISE26

## Objetivo

Avaliarmos a estabilidade de testes automatizados gerados por LLM para funções de transformação de dados em Python.

## Escopo

- 6 funções corretas oficiais;
- 18 versões defeituosas intencionais;
- 5 execuções por função;
- 30 suítes planejadas por modelo;
- execução da suíte contra a implementação correta e contra BUG01, BUG02 e BUG03.

## Modelos oficiais

- DeepSeek V4-Flash: execução oficial concluída e preservada;
- DeepSeek V4-Pro: estrutura preparada, sem execução oficial ainda.

## Comparação entre modelos

A comparação entre Flash e Pro só é válida quando ambos tiverem execução oficial completa, usando exatamente o mesmo protocolo, os mesmos prompts e os mesmos parâmetros, mudando apenas o nome do modelo e a pasta de saída.

## Configuração oficial

- Provedor: DeepSeek;
- Base URL: `https://api.deepseek.com`;
- Modelo Flash: `deepseek-v4-flash`;
- Modelo Pro: `deepseek-v4-pro`;
- Temperatura: `0.7`;
- Top-p: `1.0`;
- Max tokens: `4096`;
- Histórico entre chamadas: desativado;
- Estado padrão do script de geração: `dry-run`.

## Prompt padrão

O prompt oficial pede:

- saída somente em código Python;
- uso de Pytest;
- importação exclusiva de `ise26.targets`;
- criação de dados sintéticos dentro do próprio `test_generated.py`;
- cobertura de casos comuns e de borda;
- respeito às regras de nulos, datas, schema e negócio quando aplicável.

## Regra sobre edição dos testes

- os testes gerados por LLM não devem ser editados manualmente;
- se houver correção metodológica futura, ela deve ser registrada no protocolo e versionada separadamente;
- fixtures do repositório são exclusivas dos testes internos.

## Estrutura de salvamento

Cada modelo recebe sua própria árvore de artefatos:

- `experiments/generated_tests/deepseek_v4_flash/`
- `experiments/generated_tests/deepseek_v4_pro/`

Os resultados também são separados por modelo:

- `results/by_model/deepseek_v4_flash/`
- `results/by_model/deepseek_v4_pro/`

## Critérios de validade

Uma execução é considerada válida quando:

- a suíte existe;
- o arquivo tem sintaxe válida;
- a resposta bruta foi salva;
- o código extraído foi salvo;
- os metadados e status foram registrados.

Uma execução é considerada inválida quando:

- a chamada à API falha;
- o arquivo final tem sintaxe inválida;
- o teste não define suíte executável.

Um placeholder não é resultado experimental real e não deve ser tratado como tal nos resumos.

## Métricas registradas

- executabilidade;
- passagem na correta;
- falha bruta contra bug;
- `reliable_defect_detection_rate`;
- `false_positive_rate`;
- `contaminated_bug_failure_rate`;
- número de linhas do teste gerado;
- número aproximado de funções de teste;
- número aproximado de asserts;
- contagem de imports para `tests.fixtures`;
- contagem de imports limitados a `ise26.targets`.

## Interpretação metodológica

- falhar contra bug não basta para contar detecção de defeito;
- a mesma suíte precisa passar na correta para a detecção ser confiável;
- falha na correta deve ser tratada como falso positivo;
- falha contra bug com falha na correta é resultado contaminado;
- `reliable_defect_detection_rate` é a métrica principal;
- `defect_detection_rate_raw` é auxiliar e não deve ser usada sozinha.

## Limitações

- os dados gerados pela LLM podem variar entre execuções;
- testes com sintaxe inválida não entram como execução real;
- placeholders são úteis para preparação da estrutura, mas não contam como resultado oficial;
- comparação entre Flash e Pro só deve ocorrer quando ambos tiverem execução oficial completa.

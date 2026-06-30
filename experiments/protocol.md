# Protocolo experimental ISE26

## Objetivo

Avaliar a estabilidade de testes automatizados gerados por LLM para funções de transformação de dados em Python.

## Escopo

Este repositório mantém duas trilhas experimentais:

- **`exp_6_functions`**: baseline histórica com 6 funções, já executada oficialmente para Flash e Pro;
- **`exp_10_functions`**: expansão nova com 10 funções, preparada para uma nova rodada oficial.

Para a expansão nova:

- 10 funções corretas;
- 30 versões defeituosas intencionais;
- 5 execuções por função;
- 50 suítes planejadas por modelo;
- 200 execuções-alvo por modelo quando a geração oficial for concluída.

## Modelos oficiais

- DeepSeek V4-Flash;
- DeepSeek V4-Pro.

Cada modelo deve ter sua própria árvore de artefatos. Nunca misture Flash e Pro no mesmo diretório, CSV ou comparação.

## Configuração oficial

- Provedor: DeepSeek;
- Base URL: `https://api.deepseek.com`;
- Modelo Flash da expansão: `deepseek-v4-flash`;
- Modelo Pro da expansão: `deepseek-v4-pro`;
- Temperatura: `0.7`;
- Top-p: `1.0`;
- Max tokens: `4096`;
- Histórico entre chamadas: desativado;
- Estado padrão do gerador: `dry-run`.

## Prompts oficiais

O prompt padrão deve:

- pedir saída somente em código Python;
- pedir testes em `pytest`;
- importar a função alvo somente de `ise26.targets`;
- pedir que cada teste crie seus próprios dados sintéticos;
- cobrir casos comuns e casos de borda;
- considerar nulos, datas, schema, duplicatas e regras de negócio quando aplicável;
- não mencionar nem incentivar `tests/fixtures.py`.

Se o prompt mudar, a alteração precisa ser registrada no protocolo e na documentação.

## Regra sobre edição dos testes

- testes gerados por LLM não devem ser editados manualmente;
- correções técnicas só podem acontecer se forem registradas como parte do protocolo;
- `tests/fixtures.py` é exclusivo dos testes internos;
- testes gerados devem criar seus próprios dados dentro do próprio `test_generated.py`.

## Estrutura de salvamento

### Baseline histórica de 6 funções

- `experiments/generated_tests/deepseek_v4_flash/`
- `experiments/generated_tests/deepseek_v4_pro/`
- `results/by_model/deepseek_v4_flash/`
- `results/by_model/deepseek_v4_pro/`
- `paper_assets/model_comparison/`

### Expansão de 10 funções

- `experiments/generated_tests/exp_10_functions/deepseek_v4_flash/`
- `experiments/generated_tests/exp_10_functions/deepseek_v4_pro/`
- `results/by_experiment/exp_10_functions/by_model/deepseek_v4_flash/`
- `results/by_experiment/exp_10_functions/by_model/deepseek_v4_pro/`
- `paper_assets/exp_10_functions/model_comparison/`

Cada execução deve salvar:

- `prompt.txt`
- `system_prompt.txt`
- `raw_response.txt`
- `test_generated.py`
- `metadata.json`
- `request.json`
- `status.json`
- `manifest.csv`

## Critérios de validade

### Execução válida

Uma suíte é considerada válida quando:

- existe `test_generated.py`;
- o arquivo tem sintaxe Python válida;
- a resposta bruta foi salva;
- o código extraído foi salvo;
- os metadados foram registrados;
- o status foi registrado.

### Execução inválida

Uma suíte é inválida quando:

- a chamada à API falha (`api_error`);
- o arquivo final tem sintaxe inválida;
- o arquivo não define uma suíte executável;
- o teste depende de um recurso externo proibido pelo protocolo.

### Placeholder

Placeholder não é resultado experimental real. Ele serve apenas para preparar a estrutura antes da geração oficial.

## Métricas registradas

- executabilidade;
- passagem na implementação correta;
- falha bruta contra bug (`bug_failure_rate`);
- detecção confiável (`reliable_defect_detection_rate`);
- falso positivo (`false_positive_rate`);
- falha contaminada (`contaminated_bug_failure_rate`);
- número de linhas do teste gerado;
- número aproximado de funções de teste;
- número aproximado de asserts;
- contagem de imports para `tests.fixtures`;
- contagem de imports limitados a `ise26.targets`.

## Interpretação metodológica

- falhar contra o bug não basta para contar detecção de defeito;
- a mesma suíte precisa passar na correta para a detecção ser confiável;
- falha na correta deve ser tratada como falso positivo;
- falha contra bug com falha na correta é resultado contaminado;
- `reliable_defect_detection_rate` é a métrica principal;
- `defect_detection_rate_raw` é auxiliar e não deve ser usada sozinha.

## Comparação entre modelos

A comparação entre Flash e Pro só é válida quando ambos tiverem resultados oficiais reais do mesmo `experiment_id`.

Não compare Flash e Pro usando placeholders, nem compare resultados de `exp_6_functions` com `exp_10_functions`.

## Limitações

- os testes gerados por LLM podem variar entre execuções;
- testes com sintaxe inválida não entram como execução real;
- placeholders ajudam a preparar a estrutura, mas não contam como resultado oficial;
- a expansão de 10 funções deve ser analisada separadamente da baseline histórica de 6 funções.

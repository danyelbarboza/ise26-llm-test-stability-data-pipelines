# README da pasta `implementations`

## O que esta pasta contém

Esta pasta contém as implementações das funções usadas no experimento.

Ela está dividida em:

- `correct.py`
- `buggy/`

## Diferença entre implementação correta e defeituosa

### Implementação correta

Representa o comportamento oficial esperado da função.

### Implementação defeituosa

Representa uma versão intencionalmente errada, usada para verificar se os testes conseguem detectar problemas.

## Papel de `correct.py`

O arquivo `correct.py` contém as 6 funções corretas oficiais:

- `clean_customer_names`
- `deduplicate_events`
- `calculate_monthly_revenue`
- `join_customers_orders`
- `validate_schema`
- `classify_payment_status`

Também contém funções auxiliares usadas internamente pelas implementações corretas.

## Papel da pasta `buggy`

A pasta `buggy/` contém 18 arquivos, com 3 bugs por função.

Cada arquivo:

- importa as implementações corretas;
- sobrescreve apenas a função-alvo;
- mantém a mesma assinatura da função correta correspondente.

## Regras importantes desta pasta

- Funções corretas e defeituosas devem manter a mesma assinatura.
- As funções devem usar `return`, não `print`.
- Nenhum módulo deve executar código automaticamente ao ser importado.
- Se o comportamento correto mudar, os bugs relacionados precisam ser revisados.
- Se um bug deixar de representar o defeito previsto, ele precisa ser ajustado com cuidado, sem alterar a ideia experimental.

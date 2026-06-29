# README da pasta `buggy`

## Por que estas versões defeituosas existem

As versões defeituosas existem para o experimento.

Elas não são “erros esquecidos” do projeto. Elas são defeitos intencionais, simples e plausíveis, criados para verificar se testes gerados por LLM conseguem distinguir comportamento correto de comportamento incorreto.

## Como elas são usadas no experimento

Cada suíte de teste gerada por LLM deverá ser executada contra:

- a implementação correta da função;
- `BUG01`;
- `BUG02`;
- `BUG03`.

Se uma suíte passar na correta e falhar em um bug, isso é um sinal de detecção de defeito.

## Padrão de nome dos arquivos

O padrão é:

```text
fXX_bugYY.py
```

Exemplos:

- `f01_bug01.py`
- `f03_bug02.py`
- `f06_bug03.py`

## Relação entre F01–F06 e BUG01–BUG03

- `F01` a `F06` identificam as funções corretas oficiais.
- `BUG01` a `BUG03` identificam as três variantes defeituosas de cada função.

## Tabela dos 18 bugs

| Função | Arquivo | Bug | Descrição |
|---|---|---|---|
| F01 | `f01_bug01.py` | BUG01 | Não trata nulos corretamente |
| F01 | `f01_bug02.py` | BUG02 | Não remove acentos |
| F01 | `f01_bug03.py` | BUG03 | Não remove espaços extras |
| F02 | `f02_bug01.py` | BUG01 | Mantém o primeiro evento |
| F02 | `f02_bug02.py` | BUG02 | Remove `event_id` nulo |
| F02 | `f02_bug03.py` | BUG03 | Compara timestamp como string |
| F03 | `f03_bug01.py` | BUG01 | Soma cancelados |
| F03 | `f03_bug02.py` | BUG02 | Não trata `amount` inválido/nulo como zero |
| F03 | `f03_bug03.py` | BUG03 | Agrupa por dia |
| F04 | `f04_bug01.py` | BUG01 | Usa `inner join` |
| F04 | `f04_bug02.py` | BUG02 | Omite `record_status` |
| F04 | `f04_bug03.py` | BUG03 | Misclassifica registros sem correspondência ou com chave nula |
| F05 | `f05_bug01.py` | BUG01 | Ignora colunas ausentes |
| F05 | `f05_bug02.py` | BUG02 | Ignora erros de tipo |
| F05 | `f05_bug03.py` | BUG03 | Reprova colunas extras |
| F06 | `f06_bug01.py` | BUG01 | Marca pagamento no vencimento como atraso |
| F06 | `f06_bug02.py` | BUG02 | Trata `amount` zero como pendente |
| F06 | `f06_bug03.py` | BUG03 | Trata `paid_date` inválido como ausência de pagamento |

## Avisos importantes

- Esses bugs são intencionais.
- Eles não devem ser “corrigidos” acidentalmente.
- Se um arquivo desta pasta for alterado, é necessário confirmar se o bug experimental continua representando o defeito esperado.
- Uma correção técnica só deve acontecer se o bug impedir execução, quebrar a assinatura ou deixar de cumprir o papel experimental descrito.

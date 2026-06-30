```python
import pandas as pd
import pytest

from ise26.targets import join_customers_orders


# ------------------------------------------------------------
# Fixtures para cenários comuns
# ------------------------------------------------------------

@pytest.fixture
def basic_customers():
    """DataFrame de clientes com 3 clientes, todos com chave não nula."""
    return pd.DataFrame({
        "customer_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Carol"],
    })


@pytest.fixture
def basic_orders():
    """DataFrame de pedidos com 3 pedidos, chaves não nulas e mix de correspondências."""
    return pd.DataFrame({
        "customer_id": [1, 1, 4],
        "order_date": ["2024-01-10", "2024-01-15", "2024-02-01"],
        "amount": [100.0, 200.0, 50.0],
    })


@pytest.fixture
def customers_with_nulls():
    """Clientes que incluem chave nula."""
    return pd.DataFrame({
        "customer_id": [1, None, 2],
        "name": ["Alice", "Bob Null", "Carol"],
    })


@pytest.fixture
def orders_with_nulls():
    """Pedidos que incluem chave nula."""
    return pd.DataFrame({
        "customer_id": [1, None, 3],
        "order_date": ["2024-01-10", "2024-03-01", "2024-02-01"],
        "amount": [100.0, 75.0, 200.0],
    })


@pytest.fixture
def empty_customers():
    """DataFrame vazio de clientes."""
    return pd.DataFrame(columns=["customer_id", "name"])


@pytest.fixture
def empty_orders():
    """DataFrame vazio de pedidos."""
    return pd.DataFrame(columns=["customer_id", "order_date", "amount"])


# ------------------------------------------------------------
# Testes
# ------------------------------------------------------------

def test_basic_full_outer_join(basic_customers, basic_orders):
    """Cenário típico com correspondências e lados sem match."""
    result = join_customers_orders(basic_customers, basic_orders)
    # Número esperado de linhas: 
    # - matched: customer 1 com order 1 e order 2 -> 2 linhas
    # - customer_without_order: customer 2, 3 -> 2 linhas
    # - order_without_customer: order com customer_id=4 -> 1 linha
    # Total = 5
    assert len(result) == 5

    # Verificar status
    matched = result[result["record_status"] == "matched"]
    assert len(matched) == 2
    assert (matched["name"] == "Alice").all()

    cust_no_order = result[result["record_status"] == "customer_without_order"]
    assert len(cust_no_order) == 2
    assert sorted(cust_no_order["customer_id"].tolist()) == [2, 3]

    order_no_cust = result[result["record_status"] == "order_without_customer"]
    assert len(order_no_cust) == 1
    assert order_no_cust.iloc[0]["customer_id"] == 4

    # Verificar colunas preservadas (todas as colunas dos dois lados)
    expected_cols = {"customer_id", "name", "order_date", "amount", "record_status"}
    assert set(result.columns) == expected_cols

    # Verificar que a ordem segue a especificação: primeiro clientes na ordem original,
    # depois pedidos sem cliente na ordem original
    # customer1 com matched (customer_id=1, name=Alice) deve ser o primeiro bloco
    assert result.iloc[0]["customer_id"] == 1
    assert result.iloc[0]["record_status"] == "matched"
    # Na ordem original de customers: Alice (1) primeiro, depois Bob (2), Carol(3)
    # Como Bob e Carol são customer_without_order, eles vêm depois de Alice
    assert result.iloc[2]["customer_id"] == 2
    assert result.iloc[3]["customer_id"] == 3
    # E por último o pedido sem cliente (customer_id=4)
    assert result.iloc[4]["customer_id"] == 4


def test_null_keys_in_customers(customers_with_nulls, basic_orders):
    """Clientes com chave nula não devem ser marcados como matched."""
    result = join_customers_orders(customers_with_nulls, basic_orders)
    # customer_with_nulls tem 3 linhas: id=1, None, id=2
    # basic_orders tem id=1,1,4
    # Full outer:
    # Linhas matched: customer_id=1 com orders (2 linhas)
    # customer_without_order: customer_id=None (Bob Null) e customer_id=2
    # order_without_customer: customer_id=4
    # Total: 2+2+1 = 5
    # Mas observe que o customer_id=None NÃO casa com nenhum pedido, então virará customer_without_order
    assert len(result) == 5

    # Nenhuma linha com customer_id nulo deve ter status matched
    null_cust_rows = result[result["customer_id"].isna()]
    assert len(null_cust_rows) == 1
    assert null_cust_rows.iloc[0]["record_status"] == "customer_without_order"

    # As linhas matched devem ter customer_id não nulo
    matched = result[result["record_status"] == "matched"]
    assert matched["customer_id"].notna().all()


def test_null_keys_in_orders(basic_customers, orders_with_nulls):
    """Pedidos com chave nula não devem ser marcados como matched."""
    result = join_customers_orders(basic_customers, orders_with_nulls)
    # basic_customers: id=1,2,3
    # orders_with_nulls: id=1, None, 3
    # Full outer:
    # matched: (1,1) e (3,3) -> 2 linhas
    # customer_without_order: id=2
    # order_without_customer: id=None (order da linha 2)
    # Total = 4
    assert len(result) == 4

    null_order_rows = result[result["customer_id"].isna()]
    assert len(null_order_rows) == 1
    assert null_order_rows.iloc[0]["record_status"] == "order_without_customer"

    matched = result[result["record_status"] == "matched"]
    assert len(matched) == 2
    assert matched["customer_id"].notna().all()


def test_null_keys_both_sides(customers_with_nulls, orders_with_nulls):
    """Chaves nulas em ambos os DataFrames: linhas nulas de cada lado devem ficar separadas."""
    result = join_customers_orders(customers_with_nulls, orders_with_nulls)
    # customers: id=1, None, 2
    # orders: id=1, None, 3
    # matched: (1,1) -> 1 linha
    # customer_without_order: id=None (Bob Null) e id=2
    # order_without_customer: id=None (order da linha 2) e id=3
    # Total: 1+2+2 = 5
    # Mas cuidado: o pedido com id=None tem amount=75, order_date e o customer com id=None tem name=Bob Null
    # Eles são distintos porque o full outer join com chave nula não casa.
    assert len(result) == 5

    null_cust = result[(result["customer_id"].isna()) & (result["record_status"] == "customer_without_order")]
    assert len(null_cust) == 1
    assert null_cust.iloc[0]["name"] == "Bob Null"

    null_order = result[(result["customer_id"].isna()) & (result["record_status"] == "order_without_customer")]
    assert len(null_order) == 1
    assert null_order.iloc[0]["amount"] == 75.0

    # Verificar que matched tem customer_id=1 e não nulo
    matched = result[result["record_status"] == "matched"]
    assert len(matched) == 1
    assert matched.iloc[0]["customer_id"] == 1


def test_empty_inputs(empty_customers, empty_orders):
    """DataFrames vazios não devem quebrar e retornar DataFrame vazio."""
    result = join_customers_orders(empty_customers, empty_orders)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    expected_cols = {"customer_id", "name", "order_date", "amount", "record_status"}
    assert set(result.columns) == expected_cols


def test_only_customers_no_orders(basic_customers, empty_orders):
    """Apenas clientes, sem pedidos: todas as linhas devem ser customer_without_order."""
    result = join_customers_orders(basic_customers, empty_orders)
    assert len(result) == len(basic_customers)
    assert (result["record_status"] == "customer_without_order").all()
    # Ordem deve ser a mesma dos clientes
    assert (result["customer_id"] == basic_customers["customer_id"]).all()


def test_only_orders_no_customers(empty_customers, basic_orders):
    """Apenas pedidos, sem clientes: todas as linhas devem ser order_without_customer."""
    result = join_customers_orders(empty_customers, basic_orders)
    assert len(result) == len(basic_orders)
    assert (result["record_status"] == "order_without_customer").all()
    # Ordem deve ser a mesma dos pedidos
    assert (result["customer_id"] == basic_orders["customer_id"]).all()


def test_custom_key_name():
    """Usar uma chave diferente de 'customer_id'."""
    customers = pd.DataFrame({"chave": [1, 2], "nome": ["X", "Y"]})
    orders = pd.DataFrame({"chave": [1, 3], "produto": ["A", "B"]})
    result = join_customers_orders(customers, orders, customer_key="chave")
    assert "chave" in result.columns
    assert "record_status" in result.columns

    # matched: chave=1 -> 1 linha
    # customer_without_order: chave=2
    # order_without_customer: chave=3
    assert len(result) == 3
    assert result[result["record_status"] == "matched"].iloc[0]["chave"] == 1
    assert result[result["record_status"] == "customer_without
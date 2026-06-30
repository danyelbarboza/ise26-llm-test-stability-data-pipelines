import pytest
import pandas as pd
from ise26.targets import calculate_monthly_revenue


class TestCalculateMonthlyRevenue:
    """Suíte de testes para calculate_monthly_revenue."""

    def test_basic_aggregation(self):
        """Caso básico: pedidos não cancelados com datas e valores válidos."""
        data = {
            "order_date": ["2023-01-15", "2023-01-20", "2023-02-10"],
            "amount": [100.0, 200.0, 300.0],
            "status": ["completed", "shipped", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-02"],
            "revenue": [300.0, 300.0]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_ignore_cancelled_english(self):
        """Ignorar pedidos com status 'cancelled' (inglês) em diferentes caixas e com espaços."""
        data = {
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "amount": [10, 20, 30],
            "status": [" cancelled ", "CANCELLED", "cancelled"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [0.0]})  # todos cancelados
        pd.testing.assert_frame_equal(result, expected)

    def test_ignore_cancelled_american(self):
        """Ignorar pedidos com status 'canceled' (americano)."""
        data = {
            "order_date": ["2023-02-01", "2023-02-02"],
            "amount": [50, 150],
            "status": [" Canceled ", "canceled"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-02"], "revenue": [0.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_ignore_cancelled_portuguese(self):
        """Ignorar pedidos com status 'cancelado' (português)."""
        data = {
            "order_date": ["2023-03-01", "2023-03-15"],
            "amount": [100, 200],
            "status": [" cancelado ", "Cancelado"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-03"], "revenue": [0.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_dates_ignored(self):
        """Linhas com datas inválidas (não convertíveis) são ignoradas."""
        data = {
            "order_date": ["2023-01-01", "invalid_date", None, "2023-01-02"],
            "amount": [100, 200, 300, 400],
            "status": ["completed", "completed", "completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [500.0]})  # 100 + 400
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_amounts_as_zero(self):
        """Valores de amount não numéricos ou ausentes são tratados como zero."""
        data = {
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "amount": [100, "abc", None],
            "status": ["completed", "completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [100.0]})  # 100 + 0 + 0
        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_orders_same_month(self):
        """Múltiplos pedidos no mesmo mês devem somar os valores."""
        data = {
            "order_date": ["2023-01-01", "2023-01-15", "2023-01-31"],
            "amount": [10, 20, 30],
            "status": ["completed", "completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [60.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_sorted_by_month(self):
        """Resultado deve estar ordenado por mês (YYYY-MM)."""
        data = {
            "order_date": ["2023-03-01", "2023-01-01", "2023-02-01"],
            "amount": [100, 200, 300],
            "status": ["completed", "completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-02", "2023-03"],
            "revenue": [200.0, 300.0, 100.0]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        """DataFrame vazio deve retornar DataFrame vazio com colunas esperadas."""
        df = pd.DataFrame(columns=["order_date", "amount", "status"])
        result = calculate_monthly_revenue(df)
        assert result.empty
        assert list(result.columns) == ["month", "revenue"]

    def test_all_cancelled_no_revenue(self):
        """Se todos os pedidos são cancelados, revenue total é zero."""
        data = {
            "order_date": ["2023-01-01", "2023-02-01"],
            "amount": [100, 200],
            "status": ["cancelled", "cancelado"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-02"],
            "revenue": [0.0, 0.0]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_custom_column_names(self):
        """Usar nomes de colunas diferentes dos defaults."""
        data = {
            "date": ["2023-01-01"],
            "value": [500],
            "state": ["shipped"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df, date_col="date", amount_col="value", status_col="state")
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [500.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_mixed_valid_and_cancelled(self):
        """Mistura de pedidos válidos e cancelados no mesmo mês."""
        data = {
            "order_date": ["2023-01-01", "2023-01-15", "2023-01-20"],
            "amount": [100, 200, 300],
            "status": ["completed", "canceled", "shipped"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [400.0]})  # 100 + 300
        pd.testing.assert_frame_equal(result, expected)

    def test_all_amounts_zero(self):
        """Quando todos os amounts são zero, revenue é zero."""
        data = {
            "order_date": ["2023-01-01", "2023-01-02"],
            "amount": [0, 0],
            "status": ["completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [0.0]})
        pd.testing.assert_frame_equal(result, expected)

    def test_dataframe_with_only_invalid_dates(self):
        """Se todas as datas são inválidas, resultado vazio."""
        data = {
            "order_date": ["not_a_date", None, ""],
            "amount": [10, 20, 30],
            "status": ["completed", "completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        assert result.empty
        assert list(result.columns) == ["month", "revenue"]

    def test_negative_amounts_are_summed(self):
        """Valores negativos devem ser incluídos normalmente."""
        data = {
            "order_date": ["2023-01-01", "2023-01-02"],
            "amount": [-50, 30],
            "status": ["completed", "completed"],
        }
        df = pd.DataFrame(data)
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": ["2023-01"], "revenue": [-20.0]})
        pd.testing.assert_frame_equal(result, expected)
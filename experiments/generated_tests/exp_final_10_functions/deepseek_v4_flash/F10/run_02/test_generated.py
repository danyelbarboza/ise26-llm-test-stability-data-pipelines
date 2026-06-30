import pandas as pd
import pytest
from ise26.targets import standardize_currency_values


class TestStandardizeCurrencyValues:
    """Test suite for standardize_currency_values."""

    # ---------- Casos básicos e formatos ----------

    def test_formato_brasileiro_ponto_milhar_virgula_decimal(self):
        """R$ 1.234,56 -> 1234.56"""
        df = pd.DataFrame({"amount_raw": ["R$ 1.234,56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_formato_ingles_ponto_decimal(self):
        """1234.56 -> 1234.56"""
        df = pd.DataFrame({"amount_raw": ["1234.56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_sem_separador_milhar(self):
        """R$ 1234,56 -> 1234.56"""
        df = pd.DataFrame({"amount_raw": ["R$ 1234,56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_valor_inteiro_sem_decimais(self):
        """R$ 1000 -> 1000.0"""
        df = pd.DataFrame({"amount_raw": ["R$ 1000"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1000.0

    def test_valor_pequeno(self):
        """0,99 -> 0.99"""
        df = pd.DataFrame({"amount_raw": ["0,99"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 0.99

    def test_valor_negativo_com_parenteses(self):
        """R$ (1.000,50) -> -1000.50"""
        df = pd.DataFrame({"amount_raw": ["R$ (1.000,50)"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == -1000.50

    def test_valor_negativo_com_sinal_ingles(self):
        """-1000.50 -> -1000.50"""
        df = pd.DataFrame({"amount_raw": ["-1000.50"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == -1000.50

    # ---------- Espaços e prefixo opcional ----------

    def test_prefixo_sem_espaco(self):
        """R$1234,56 (sem espaço)"""
        df = pd.DataFrame({"amount_raw": ["R$1234,56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_prefixo_com_varios_espacos(self):
        """R$   1.234,56"""
        df = pd.DataFrame({"amount_raw": ["R$   1.234,56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_sem_prefixo(self):
        """1.234,56 -> 1234.56"""
        df = pd.DataFrame({"amount_raw": ["1.234,56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    # ---------- Valores inválidos ----------

    def test_texto_invalido_retorna_na(self):
        """'abc' -> pd.NA"""
        df = pd.DataFrame({"amount_raw": ["abc"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] is pd.NA

    def test_vazio_retorna_na(self):
        """'' -> pd.NA"""
        df = pd.DataFrame({"amount_raw": [""]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] is pd.NA

    def test_so_prefixo_retorna_na(self):
        """'R$' -> pd.NA"""
        df = pd.DataFrame({"amount_raw": ["R$"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] is pd.NA

    def test_formato_ambiguo_retorna_na(self):
        """'1.234' (sem decimal, poderia ser milhar ou decimal) -> pd.NA"""
        df = pd.DataFrame({"amount_raw": ["1.234"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] is pd.NA

    # ---------- Colunas e estrutura ----------

    def test_preserva_coluna_original(self):
        """Coluna raw permanece inalterada."""
        df = pd.DataFrame({"amount_raw": ["R$ 100,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert "amount_raw" in result.columns
        assert result["amount_raw"].iloc[0] == "R$ 100,00"

    def test_nova_coluna_criada(self):
        """Coluna de output é criada."""
        df = pd.DataFrame({"amount_raw": ["R$ 100,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert "amount" in result.columns

    def test_dtype_float64(self):
        """Dtype da coluna output é Float64 (nullable)."""
        df = pd.DataFrame({"amount_raw": ["R$ 100,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].dtype == pd.Float64Dtype()

    def test_retorna_dataframe_copia(self):
        """Retorna um novo DataFrame, não modifica o original."""
        df = pd.DataFrame({"amount_raw": ["R$ 100,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result is not df

    # ---------- Múltiplas linhas e valores mistos ----------

    def test_multiplas_linhas(self):
        """Testa várias linhas com valores válidos e inválidos."""
        df = pd.DataFrame({
            "amount_raw": [
                "R$ 1.000,50",
                "2000",
                "abc",
                "",
                "R$ (500,25)",
                None,
            ]
        })
        result = standardize_currency_values(df, "amount_raw", "amount")
        expected = pd.Series(
            [1000.50, 2000.0, pd.NA, pd.NA, -500.25, pd.NA],
            dtype="Float64",
            name="amount",
        )
        pd.testing.assert_series_equal(result["amount"], expected, check_dtype=True)

    def test_indice_nao_inteiro(self):
        """Funciona com índice não padrão (ex: string)."""
        df = pd.DataFrame(
            {"amount_raw": ["R$ 50,00", "R$ 100,00"]},
            index=["a", "b"],
        )
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert list(result["amount"]) == [50.0, 100.0]
        assert list(result.index) == ["a", "b"]

    def test_coluna_output_igual_ao_input(self):
        """Se output_col == value_col, a coluna raw é sobrescrita."""
        df = pd.DataFrame({"amount_raw": ["R$ 100,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount_raw")
        assert result["amount_raw"].iloc[0] == 100.0

    # ---------- Casos especiais de números ----------

    def test_grande_numero(self):
        """R$ 9.999.999,99 -> 9999999.99"""
        df = pd.DataFrame({"amount_raw": ["R$ 9.999.999,99"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 9999999.99

    def test_ponto_decimal_ingles_com_milhar_vazio(self):
        """'1,234.56' (inglês vice-versa) -> 1234.56"""
        df = pd.DataFrame({"amount_raw": ["1,234.56"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 1234.56

    def test_valor_zerado(self):
        """R$ 0,00 -> 0.0"""
        df = pd.DataFrame({"amount_raw": ["R$ 0,00"]})
        result = standardize_currency_values(df, "amount_raw", "amount")
        assert result["amount"].iloc[0] == 0.0
import pytest
import pandas as pd
from ise26.targets import calculate_conversion_rate


class TestCalculateConversionRate:
    """Suite de testes para calculate_conversion_rate."""

    # ------------------------------------------------------------------
    # Caso básico com valores positivos
    # ------------------------------------------------------------------
    def test_basic_conversion_rate(self):
        df = pd.DataFrame({
            'channel': ['A', 'B', 'A', 'B'],
            'visits': [100, 200, 50, 150],
            'conversions': [10, 30, 5, 20],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [150.0, 350.0],
            'conversions': [15.0, 50.0],
            'conversion_rate': [15.0/150.0, 50.0/350.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Valores nulos em visits – devem ser tratados como 0
    # ------------------------------------------------------------------
    def test_nan_in_visits(self):
        df = pd.DataFrame({
            'channel': ['X', 'X', 'Y'],
            'visits': [100, None, 200],
            'conversions': [10, 20, 30],
        })
        result = calculate_conversion_rate(df)
        # channel X: visits (100+0)=100, conversions (10+20)=30, rate=0.3
        # channel Y: visits 200, conversions 30, rate=0.15
        expected = pd.DataFrame({
            'channel': ['X', 'Y'],
            'visits': [100.0, 200.0],
            'conversions': [30.0, 30.0],
            'conversion_rate': [30.0/100.0, 30.0/200.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Valores nulos em conversions – tratados como 0
    # ------------------------------------------------------------------
    def test_nan_in_conversions(self):
        df = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [100, 200],
            'conversions': [None, 50],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [100.0, 200.0],
            'conversions': [0.0, 50.0],
            'conversion_rate': [0.0, 50.0/200.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Valores inválidos (não numéricos) em visits – tratados como 0
    # ------------------------------------------------------------------
    def test_invalid_string_in_visits(self):
        df = pd.DataFrame({
            'channel': ['A', 'A'],
            'visits': ['abc', 50],
            'conversions': [10, 5],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A'],
            'visits': [50.0],
            'conversions': [15.0],
            'conversion_rate': [15.0/50.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Visits zero – conversion_rate deve ser 0
    # ------------------------------------------------------------------
    def test_zero_visits(self):
        df = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [0, 100],
            'conversions': [10, 20],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [0.0, 100.0],
            'conversions': [10.0, 20.0],
            'conversion_rate': [0.0, 20.0/100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Visits negativos – tratados como <=0, rate = 0
    # ------------------------------------------------------------------
    def test_negative_visits(self):
        df = pd.DataFrame({
            'channel': ['A'],
            'visits': [-10],
            'conversions': [5],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A'],
            'visits': [-10.0],
            'conversions': [5.0],
            'conversion_rate': [0.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Conversões negativas – permitido, rate negativo se visits > 0
    # ------------------------------------------------------------------
    def test_negative_conversions(self):
        df = pd.DataFrame({
            'channel': ['A'],
            'visits': [100],
            'conversions': [-10],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A'],
            'visits': [100.0],
            'conversions': [-10.0],
            'conversion_rate': [-10.0/100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Tipos mistos (nulo, string, válido)
    # ------------------------------------------------------------------
    def test_mixed_types(self):
        df = pd.DataFrame({
            'channel': ['A', 'A', 'B'],
            'visits': [100, 'invalid', None],
            'conversions': [None, 20, 'x'],
        })
        result = calculate_conversion_rate(df)
        # A: visits=100, conversions=20 -> rate 0.2
        # B: visits=0, conversions=0 -> rate 0
        expected = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [100.0, 0.0],
            'conversions': [20.0, 0.0],
            'conversion_rate': [20.0/100.0, 0.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Canais duplicados – devem ser agregados
    # ------------------------------------------------------------------
    def test_duplicate_channels(self):
        df = pd.DataFrame({
            'channel': ['A', 'A', 'A'],
            'visits': [10, 20, 30],
            'conversions': [1, 2, 3],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A'],
            'visits': [60.0],
            'conversions': [6.0],
            'conversion_rate': [6.0/60.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # DataFrame vazio – retorna DataFrame vazio com colunas corretas
    # ------------------------------------------------------------------
    def test_empty_dataframe(self):
        df = pd.DataFrame({'channel': pd.Series(dtype='object'), 'visits': pd.Series(dtype='int'), 'conversions': pd.Series(dtype='int')})
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': pd.Series(dtype='object'),
            'visits': pd.Series(dtype='float64'),
            'conversions': pd.Series(dtype='float64'),
            'conversion_rate': pd.Series(dtype='float64'),
        })
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    # ------------------------------------------------------------------
    # Linha única sem problemas
    # ------------------------------------------------------------------
    def test_single_row(self):
        df = pd.DataFrame({
            'channel': ['unique'],
            'visits': [42],
            'conversions': [7],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['unique'],
            'visits': [42.0],
            'conversions': [7.0],
            'conversion_rate': [7.0/42.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Ordenação alfabética dos canais
    # ------------------------------------------------------------------
    def test_sorting(self):
        df = pd.DataFrame({
            'channel': ['Z', 'A', 'M'],
            'visits': [10, 20, 30],
            'conversions': [1, 2, 3],
        })
        result = calculate_conversion_rate(df)
        expected_order = ['A', 'M', 'Z']
        assert list(result['channel']) == expected_order

    # ------------------------------------------------------------------
    # Nomes de colunas personalizados
    # ------------------------------------------------------------------
    def test_custom_column_names(self):
        df = pd.DataFrame({
            'grupo': ['red', 'blue', 'red'],
            'cnt_visitas': [100, 200, 50],
            'cnt_conversoes': [5, 10, 2],
        })
        result = calculate_conversion_rate(
            df,
            group_col='grupo',
            visits_col='cnt_visitas',
            conversions_col='cnt_conversoes'
        )
        expected = pd.DataFrame({
            'grupo': ['blue', 'red'],
            'visits': [200.0, 150.0],
            'conversions': [10.0, 7.0],
            'conversion_rate': [10.0/200.0, 7.0/150.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    # ------------------------------------------------------------------
    # Garantir que o DataFrame original não foi modificado
    # ------------------------------------------------------------------
    def test_original_dataframe_unchanged(self):
        original = pd.DataFrame({
            'channel': ['A', 'A'],
            'visits': [100, 200],
            'conversions': [10, 20],
        })
        df_copy = original.copy()
        _ = calculate_conversion_rate(original)
        pd.testing.assert_frame_equal(original, df_copy)

    # ------------------------------------------------------------------
    # Tratamento de todos os valores nulos – todas as taxas zero
    # ------------------------------------------------------------------
    def test_all_nan_conversions_and_visits(self):
        df = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [None, None],
            'conversions': [None, None],
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['A', 'B'],
            'visits': [0.0, 0.0],
            'conversions': [0.0, 0.0],
            'conversion_rate': [0.0, 0.0],
        })
        pd.testing.assert_frame_equal(result, expected)
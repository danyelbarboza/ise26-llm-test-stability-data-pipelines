import pytest
import pandas as pd
import numpy as np
from ise26.targets import calculate_conversion_rate


class TestCalculateConversionRate:
    """Suite de testes para a função calculate_conversion_rate."""

    def test_basic_conversion_rate(self):
        """Caso básico: múltiplos canais com valores positivos."""
        df = pd.DataFrame({
            'channel': ['email', 'social', 'search'],
            'visits': [1000, 500, 2000],
            'conversions': [50, 25, 100]
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['email', 'search', 'social'],
            'visits': [1000.0, 2000.0, 500.0],
            'conversions': [50.0, 100.0, 25.0],
            'conversion_rate': [0.05, 0.05, 0.05]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_missing_channel_unknown(self):
        """Canais nulos, NaN ou vazios são normalizados para 'unknown'."""
        df = pd.DataFrame({
            'channel': [None, np.nan, ' ', 'email', 'email'],
            'visits': [100, 200, 300, 400, 500],
            'conversions': [10, 20, 30, 40, 50]
        })
        result = calculate_conversion_rate(df)
        # Separar unknown e email
        unknown_visits = 100 + 200 + 300  # 600
        unknown_conv = 10 + 20 + 30       # 60
        email_visits = 400 + 500          # 900
        email_conv = 40 + 50             # 90
        expected = pd.DataFrame({
            'channel': ['email', 'unknown'],
            'visits': [900.0, 600.0],
            'conversions': [90.0, 60.0],
            'conversion_rate': [90.0 / 900.0, 60.0 / 600.0]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_missing_and_invalid_numeric(self):
        """Valores ausentes, NaN, strings inválidas em visits/conversions tratados como zero."""
        df = pd.DataFrame({
            'channel': ['email', 'social', 'search'],
            'visits': [100, np.nan, None],
            'conversions': [np.nan, 10, 'invalid']
        })
        result = calculate_conversion_rate(df)
        # Linha 1: visits 100, conversions 0 (NaN)
        # Linha 2: visits 0 (NaN), conversions 10
        # Linha 3: visits 0 (None), conversions 0 ('invalid' -> coerção)
        expected = pd.DataFrame({
            'channel': ['email', 'search', 'social'],
            'visits': [100.0, 0.0, 0.0],
            'conversions': [0.0, 0.0, 10.0],
            'conversion_rate': [0.0, 0.0, 0.0]  # 10/0 = 0, 0/100 = 0, 0/0 = 0
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_visits_zero_returns_zero_rate(self):
        """Quando visits são zero, conversion_rate é zero mesmo com conversões."""
        df = pd.DataFrame({
            'channel': ['a', 'b'],
            'visits': [0, 0],
            'conversions': [100, 0]
        })
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': ['a', 'b'],
            'visits': [0.0, 0.0],
            'conversions': [100.0, 0.0],
            'conversion_rate': [0.0, 0.0]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_conversions_zero_rate_zero(self):
        """Conversões zero resultam em taxa zero, não divisão por zero."""
        df = pd.DataFrame({
            'channel': ['x'],
            'visits': [50],
            'conversions': [0]
        })
        result = calculate_conversion_rate(df)
        assert result.loc[0, 'conversion_rate'] == 0.0

    def test_sorting_alphabetical(self):
        """Resultado ordenado alfabeticamente pelo canal."""
        df = pd.DataFrame({
            'channel': ['z', 'a', 'm'],
            'visits': [1, 2, 3],
            'conversions': [0, 0, 0]
        })
        result = calculate_conversion_rate(df)
        assert list(result['channel']) == ['a', 'm', 'z']

    def test_output_columns(self):
        """DataFrame de saída tem colunas exatas."""
        df = pd.DataFrame({
            'channel': ['a'],
            'visits': [10],
            'conversions': [1]
        })
        result = calculate_conversion_rate(df)
        assert list(result.columns) == ['channel', 'visits', 'conversions', 'conversion_rate']

    def test_data_types(self):
        """Visits e conversions são float, conversion_rate é float."""
        df = pd.DataFrame({
            'channel': ['email'],
            'visits': [100],
            'conversions': [10]
        })
        result = calculate_conversion_rate(df)
        assert result['visits'].dtype == np.float64
        assert result['conversions'].dtype == np.float64
        assert result['conversion_rate'].dtype == np.float64

    def test_aggregation_multiple_rows_same_channel(self):
        """Múltiplas linhas para o mesmo canal são somadas."""
        df = pd.DataFrame({
            'channel': ['email', 'email', 'social'],
            'visits': [100, 200, 300],
            'conversions': [5, 15, 10]
        })
        result = calculate_conversion_rate(df)
        email = result[result['channel'] == 'email']
        assert email['visits'].iloc[0] == 300.0
        assert email['conversions'].iloc[0] == 20.0
        assert email['conversion_rate'].iloc[0] == pytest.approx(20.0 / 300.0)

    def test_non_default_column_names(self):
        """Usa nomes de colunas personalizados."""
        df = pd.DataFrame({
            'source': ['web', 'app'],
            'views': [1000, 500],
            'signups': [10, 5]
        })
        result = calculate_conversion_rate(df,
                                           group_col='source',
                                           visits_col='views',
                                           conversions_col='signups')
        expected = pd.DataFrame({
            'source': ['app', 'web'],
            'visits': [500.0, 1000.0],
            'conversions': [5.0, 10.0],
            'conversion_rate': [0.01, 0.01]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        """DataFrame vazio ainda deve funcionar (sem linhas)."""
        df = pd.DataFrame({'channel': pd.Series(dtype=str),
                           'visits': pd.Series(dtype=int),
                           'conversions': pd.Series(dtype=int)})
        result = calculate_conversion_rate(df)
        expected = pd.DataFrame({
            'channel': pd.Series(dtype=str),
            'visits': pd.Series(dtype=float),
            'conversions': pd.Series(dtype=float),
            'conversion_rate': pd.Series(dtype=float)
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_negative_visits(self):
        """Visitas negativas são mantidas como estão, mas taxa será 0 pois visits <= 0."""
        df = pd.DataFrame({
            'channel': ['a'],
            'visits': [-10],
            'conversions': [5]
        })
        result = calculate_conversion_rate(df)
        # visits negativo, visits <= 0 => taxa 0, mas soma ainda guarda -10.
        assert result.loc[0, 'visits'] == -10.0
        assert result.loc[0, 'conversion_rate'] == 0.0

    def test_float_conversions_ratio(self):
        """Conversões e visitas inteiros geram taxa float correta."""
        df = pd.DataFrame({
            'channel': ['a'],
            'visits': [7],
            'conversions': [3]
        })
        result = calculate_conversion_rate(df)
        assert result.loc[0, 'conversion_rate'] == pytest.approx(3 / 7)

    def test_all_channels_unknown(self):
        """Se todos os canais forem nulos, único grupo 'unknown'."""
        df = pd.DataFrame({
            'channel': [None, None],
            'visits': [100, 200],
            'conversions': [10, 20]
        })
        result = calculate_conversion_rate(df)
        assert len(result) == 1
        assert result['channel'].iloc[0] == 'unknown'
        assert result['visits'].iloc[0] == 300.0
        assert result['conversions'].iloc[0] == 30.0
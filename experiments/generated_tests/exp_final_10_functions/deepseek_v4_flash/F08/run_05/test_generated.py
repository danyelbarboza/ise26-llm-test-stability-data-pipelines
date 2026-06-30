import pandas as pd
import pytest
from ise26.targets import calculate_conversion_rate


def test_basic_conversion_rate():
    """Caso básico: canais com dados válidos."""
    df = pd.DataFrame({
        "channel": ["organic", "paid", "social"],
        "visits": [100, 200, 150],
        "conversions": [5, 10, 3],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["organic", "paid", "social"],
        "visits": [100.0, 200.0, 150.0],
        "conversions": [5.0, 10.0, 3.0],
        "conversion_rate": [5.0 / 100, 10.0 / 200, 3.0 / 150],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    """DataFrame vazio deve retornar vazio."""
    df = pd.DataFrame({"channel": pd.Series(dtype="object"), "visits": pd.Series(dtype="int"), "conversions": pd.Series(dtype="int")})
    result = calculate_conversion_rate(df)
    assert result.empty
    assert list(result.columns) == ["channel", "visits", "conversions", "conversion_rate"]


def test_missing_visits_conversions():
    """Valores faltantes ou inválidos são tratados como zero."""
    df = pd.DataFrame({
        "channel": ["email", "email", "email"],
        "visits": [50, None, "invalid"],
        "conversions": [2, None, 0],
    })
    result = calculate_conversion_rate(df)
    # esperado: uma linha para email com visits=50+0+0=50, conversions=2+0+0=2
    expected = pd.DataFrame({
        "channel": ["email"],
        "visits": [50.0],
        "conversions": [2.0],
        "conversion_rate": [2.0 / 50.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_blank_and_null_channels():
    """Canais em branco ou nulos são normalizados para 'unknown'."""
    df = pd.DataFrame({
        "channel": ["organic", "", None, "organic", ""],
        "visits": [100, 50, 30, 200, 10],
        "conversions": [5, 1, 0, 8, 0],
    })
    result = calculate_conversion_rate(df)
    # agrupa: organic (100+200=300 visits, 5+8=13 conversions), unknown (50+30+10=90 visits, 1+0+0=1 conversion)
    expected = pd.DataFrame({
        "channel": ["organic", "unknown"],
        "visits": [300.0, 90.0],
        "conversions": [13.0, 1.0],
        "conversion_rate": [13.0 / 300.0, 1.0 / 90.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_zero_visits_yields_zero_rate():
    """Quando visits são zero ou inválidas, conversion_rate deve ser zero."""
    df = pd.DataFrame({
        "channel": ["display", "affiliate"],
        "visits": [0, None],
        "conversions": [10, 5],
    })
    result = calculate_conversion_rate(df)
    # ambos virão como 0 visits => rate 0
    expected = pd.DataFrame({
        "channel": ["affiliate", "display"],  # ordenação alfabética
        "visits": [0.0, 0.0],
        "conversions": [5.0, 10.0],
        "conversion_rate": [0.0, 0.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_negative_visits_treated_as_valid_and_used():
    """Valores negativos não são tratados como inválidos; são usados normalmente (podem gerar rate negativo)."""
    df = pd.DataFrame({
        "channel": ["referral"],
        "visits": [-10],
        "conversions": [3],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["referral"],
        "visits": [-10.0],
        "conversions": [3.0],
        "conversion_rate": [3.0 / (-10.0)],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_order_by_channel_alphabetical():
    """O DataFrame resultante deve estar ordenado alfabeticamente pela coluna de grupo."""
    df = pd.DataFrame({
        "channel": ["z", "a", "m"],
        "visits": [10, 20, 30],
        "conversions": [1, 2, 3],
    })
    result = calculate_conversion_rate(df)
    assert list(result["channel"]) == ["a", "m", "z"]


def test_custom_column_names():
    """Testa se o parâmetro group_col, visits_col, conversions_col são respeitados."""
    df = pd.DataFrame({
        "campaign": ["c1", "c2"],
        "click": [100, 200],
        "sale": [2, 4],
    })
    result = calculate_conversion_rate(df, group_col="campaign", visits_col="click", conversions_col="sale")
    expected = pd.DataFrame({
        "campaign": ["c1", "c2"],
        "visits": [100.0, 200.0],
        "conversions": [2.0, 4.0],
        "conversion_rate": [0.02, 0.02],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_all_nan_in_visits_and_conversions():
    """Todos os valores NaN são tratados como zero, resultando em visits=0 e rate=0."""
    df = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [float("nan"), float("nan")],
        "conversions": [float("nan"), float("nan")],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [0.0, 0.0],
        "conversions": [0.0, 0.0],
        "conversion_rate": [0.0, 0.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_types_in_numeric_columns():
    """Colunas numéricas podem conter strings não conversíveis; devem ser tratadas como zero."""
    df = pd.DataFrame({
        "channel": ["x"],
        "visits": ["abc"],
        "conversions": ["12.5"],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["x"],
        "visits": [0.0],
        "conversions": [12.5],
        "conversion_rate": [0.0],  # visits=0 => rate=0
    })
    pd.testing.assert_frame_equal(result, expected)


def test_original_dataframe_not_mutated():
    """A função não deve modificar o DataFrame de entrada."""
    df = pd.DataFrame({
        "channel": ["org", "paid"],
        "visits": [100, 200],
        "conversions": [5, 10],
    })
    df_copy = df.copy()
    calculate_conversion_rate(df)
    pd.testing.assert_frame_equal(df, df_copy)
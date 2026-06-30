import pandas as pd
import pytest
from ise26.targets import calculate_conversion_rate


def test_basic_conversion_rate():
    df = pd.DataFrame({
        "channel": ["A", "B", "A", "C"],
        "visits": [100, 200, 150, 50],
        "conversions": [10, 30, 15, 5],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["A", "B", "C"],
        "visits": [250.0, 200.0, 50.0],
        "conversions": [25.0, 30.0, 5.0],
        "conversion_rate": [0.1, 0.15, 0.1],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_zero_visits_returns_zero_rate():
    df = pd.DataFrame({
        "channel": ["X", "Y"],
        "visits": [0, 100],
        "conversions": [10, 5],
    })
    result = calculate_conversion_rate(df)
    assert result.loc[result["channel"] == "X", "conversion_rate"].iloc[0] == 0.0
    assert result.loc[result["channel"] == "Y", "conversion_rate"].iloc[0] == pytest.approx(0.05)


def test_null_or_invalid_numeric_treated_as_zero():
    df = pd.DataFrame({
        "channel": ["M", "N"],
        "visits": [None, "abc"],
        "conversions": [5, None],
    })
    result = calculate_conversion_rate(df)
    # Both rows should have visits=0, conversions=0 => conversion_rate=0
    for _, row in result.iterrows():
        assert row["visits"] == 0.0
        assert row["conversions"] == 0.0
        assert row["conversion_rate"] == 0.0


def test_duplicate_channels_aggregated():
    df = pd.DataFrame({
        "channel": ["A", "A", "B", "B", "B"],
        "visits": [10, 20, 30, 40, 50],
        "conversions": [1, 2, 3, 4, 5],
    })
    result = calculate_conversion_rate(df)
    expected = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [30.0, 120.0],
        "conversions": [3.0, 12.0],
        "conversion_rate": [0.1, 0.1],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_group_column():
    df = pd.DataFrame({
        "group": ["X", "Y", "X"],
        "visits": [100, 200, 300],
        "conversions": [10, 20, 30],
    })
    result = calculate_conversion_rate(df, group_col="group")
    assert list(result.columns) == ["group", "visits", "conversions", "conversion_rate"]
    assert result["group"].tolist() == ["X", "Y"]
    assert result["visits"].tolist() == [400.0, 200.0]
    assert result["conversions"].tolist() == [40.0, 20.0]


def test_custom_visits_and_conversions_columns():
    df = pd.DataFrame({
        "channel": ["A", "B"],
        "clicks": [100, 200],
        "purchases": [10, 30],
    })
    result = calculate_conversion_rate(df, visits_col="clicks", conversions_col="purchases")
    assert result["visits"].tolist() == [100.0, 200.0]
    assert result["conversions"].tolist() == [10.0, 30.0]


def test_sorting_by_channel_alphabetically():
    df = pd.DataFrame({
        "channel": ["Z", "A", "M"],
        "visits": [1, 2, 3],
        "conversions": [0, 0, 0],
    })
    result = calculate_conversion_rate(df)
    assert result["channel"].tolist() == ["A", "M", "Z"]


def test_nan_in_group_column():
    df = pd.DataFrame({
        "channel": [None, "B", None],
        "visits": [10, 20, 30],
        "conversions": [1, 2, 3],
    })
    result = calculate_conversion_rate(df)
    # NaN groups are preserved and sorted at the end (default na_position='last')
    assert pd.isna(result["channel"].iloc[-1])  # last row should be NaN
    # The NaN group should have aggregated values 40 and 4
    nan_row = result[result["channel"].isna()]
    assert len(nan_row) == 1
    assert nan_row["visits"].iloc[0] == 40.0
    assert nan_row["conversions"].iloc[0] == 4.0


def test_empty_dataframe():
    df = pd.DataFrame({"channel": [], "visits": [], "conversions": []})
    result = calculate_conversion_rate(df)
    assert result.empty
    assert list(result.columns) == ["channel", "visits", "conversions", "conversion_rate"]


def test_original_dataframe_not_modified():
    original = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [10, 20],
        "conversions": [1, 2],
    })
    copy = original.copy()
    calculate_conversion_rate(original)
    pd.testing.assert_frame_equal(original, copy)


def test_mixed_valid_and_invalid():
    df = pd.DataFrame({
        "channel": ["X", "Y", "X", "Y"],
        "visits": [100, "foo", 200, 300],
        "conversions": [10, 20, None, 30],
    })
    result = calculate_conversion_rate(df)
    # X: visits=100+200=300, conversions=10+0=10 => rate=10/300≈0.03333
    # Y: visits=0+300=300, conversions=20+30=50 => rate=50/300≈0.16667
    x_row = result[result["channel"] == "X"].iloc[0]
    y_row = result[result["channel"] == "Y"].iloc[0]
    assert x_row["visits"] == 300.0
    assert x_row["conversions"] == 10.0
    assert x_row["conversion_rate"] == pytest.approx(10/300)
    assert y_row["visits"] == 300.0
    assert y_row["conversions"] == 50.0
    assert y_row["conversion_rate"] == pytest.approx(50/300)


def test_all_visits_zero():
    df = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [0, 0],
        "conversions": [10, 20],
    })
    result = calculate_conversion_rate(df)
    for _, row in result.iterrows():
        assert row["visits"] == 0.0
        assert row["conversion_rate"] == 0.0


def test_no_conversions():
    df = pd.DataFrame({
        "channel": ["A", "B"],
        "visits": [100, 200],
        "conversions": [0, 0],
    })
    result = calculate_conversion_rate(df)
    assert (result["conversion_rate"] == 0.0).all()
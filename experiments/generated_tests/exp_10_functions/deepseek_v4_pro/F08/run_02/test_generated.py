import pandas as pd
import pytest
import numpy as np
from ise26.targets import calculate_conversion_rate


def test_basic_aggregation_sorted_by_channel():
    df = pd.DataFrame({
        "channel": ["Social", "Email", "Social", "Referral", "Email"],
        "visits": [100, 200, 150, 50, 0],
        "conversions": [5, 12, 8, 1, 0],
    })
    result = calculate_conversion_rate(df)
    assert list(result.columns) == ["channel", "visits", "conversions", "conversion_rate"]
    # Sorted alphabetically: Email, Referral, Social
    assert result["channel"].tolist() == ["Email", "Referral", "Social"]
    assert result["visits"].tolist() == [200.0, 50.0, 250.0]  # 200+0, 50, 100+150
    assert result["conversions"].tolist() == [12.0, 1.0, 13.0]
    # Conversion rates: Email 12/200=0.06, Referral 1/50=0.02, Social 13/250=0.052
    assert pytest.approx(result["conversion_rate"].tolist()) == [0.06, 0.02, 13/250]


def test_invalid_numeric_values_treated_as_zero():
    df = pd.DataFrame({
        "channel": ["A", "A", "B"],
        "visits": [10, "bad", None],
        "conversions": ["x", 2, np.nan],
    })
    result = calculate_conversion_rate(df)
    # For A: visits: 10 (coerced from string "bad" becomes NaN, filled with 0) => sum = 10, 
    # conversions: "x" -> NaN -> 0, 2 -> 2 => total 2. Rate = 2/10=0.2
    # For B: visits None -> NaN -> 0, conversions NaN -> 0 => visits=0 => rate=0
    assert result["channel"].tolist() == ["A", "B"]
    assert result["visits"].tolist() == [10.0, 0.0]
    assert result["conversions"].tolist() == [2.0, 0.0]
    assert pytest.approx(result["conversion_rate"].tolist()) == [0.2, 0.0]


def test_zero_and_negative_visits_lead_to_zero_rate():
    df = pd.DataFrame({
        "channel": ["C", "C", "D", "E"],
        "visits": [0, -5, 0, -10],
        "conversions": [3, 2, 0, 0],
    })
    result = calculate_conversion_rate(df)
    # C: sum visits = -5, conversions = 5. Condition row["visits"] <= 0 yields rate = 0
    # D: sum visits = 0, conversions = 0 -> rate 0
    # E: sum visits = -10, conversions = 0 -> rate 0
    # Sorted: C, D, E
    assert result["channel"].tolist() == ["C", "D", "E"]
    assert result["visits"].tolist() == [-5.0, 0.0, -10.0]
    assert result["conversions"].tolist() == [5.0, 0.0, 0.0]
    assert result["conversion_rate"].tolist() == [0.0, 0.0, 0.0]


def test_group_column_custom_name():
    df = pd.DataFrame({
        "campaign": ["X", "Y", "X"],
        "clicks": [30, 20, 10],
        "sales": [2, 1, 0],
    })
    result = calculate_conversion_rate(df, group_col="campaign", visits_col="clicks", conversions_col="sales")
    assert list(result.columns) == ["campaign", "visits", "conversions", "conversion_rate"]
    assert result["campaign"].tolist() == ["X", "Y"]  # sorted
    assert result["visits"].tolist() == [40.0, 20.0]
    assert result["conversions"].tolist() == [2.0, 1.0]
    assert pytest.approx(result["conversion_rate"].tolist()) == [0.05, 0.05]


def test_nan_in_group_column_kept():
    df = pd.DataFrame({
        "channel": ["A", None, "B", None],
        "visits": [10, 5, 20, 15],
        "conversions": [1, 0, 2, 1],
    })
    result = calculate_conversion_rate(df)
    # A: visits=10, conv=1; B:20,2; None group: total visits 5+15=20, conv 0+1=1. Rate=1/20=0.05
    # Sorting: None is treated as a value; with default sort, None appears after strings? In Python, None < strings? Actually None is less than strings, so None will be first.
    # Let's confirm expected order: None, A, B
    assert result["channel"].tolist() == [None, "A", "B"]
    assert result["visits"].tolist() == [20.0, 10.0, 20.0]
    assert result["conversions"].tolist() == [1.0, 1.0, 2.0]
    assert pytest.approx(result["conversion_rate"].tolist()) == [0.05, 0.1, 0.1]


def test_empty_dataframe_returns_empty_correct_schema():
    df = pd.DataFrame({"channel": pd.Series(dtype="object"),
                        "visits": pd.Series(dtype="float64"),
                        "conversions": pd.Series(dtype="float64")})
    result = calculate_conversion_rate(df)
    assert list(result.columns) == ["channel", "visits", "conversions", "conversion_rate"]
    assert len(result) == 0
    # dtypes: channel object, visits float, conversions float, conversion_rate float
    assert result["visits"].dtype == float
    assert result["conversions"].dtype == float
    assert result["conversion_rate"].dtype == float


def test_all_data_invalid_or_missing():
    df = pd.DataFrame({
        "channel": ["Z"],
        "visits": [np.nan],
        "conversions": [np.nan],
    })
    result = calculate_conversion_rate(df)
    assert result["channel"].tolist() == ["Z"]
    assert result["visits"].tolist() == [0.0]
    assert result["conversions"].tolist() == [0.0]
    assert result["conversion_rate"].tolist() == [0.0]


def test_float_precision():
    df = pd.DataFrame({
        "channel": ["P", "P"],
        "visits": [3, 7],
        "conversions": [1, 0],
    })
    result = calculate_conversion_rate(df)
    assert result["channel"].tolist() == ["P"]
    assert result["visits"].tolist() == [10.0]
    assert result["conversions"].tolist() == [1.0]
    assert result["conversion_rate"].tolist() == [0.1]
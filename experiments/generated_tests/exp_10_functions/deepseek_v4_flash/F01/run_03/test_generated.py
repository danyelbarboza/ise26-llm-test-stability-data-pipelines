import pytest
import pandas as pd
import numpy as np
from ise26.targets import clean_customer_names


def test_basic_lowercase_and_trim():
    df = pd.DataFrame({"customer_name": ["  HELLO  "]})
    result = clean_customer_names(df, "customer_name", "clean")
    expected = pd.DataFrame({"customer_name": ["  HELLO  "], "clean": ["hello"]})
    pd.testing.assert_frame_equal(result, expected)


def test_accent_removal():
    df = pd.DataFrame({"name": ["João", "José", "María", "Cécilia"]})
    result = clean_customer_names(df, "name", "normalized")
    expected = pd.DataFrame(
        {
            "name": ["João", "José", "María", "Cécilia"],
            "normalized": ["joao", "jose", "maria", "cecilia"],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_multiple_spaces_collapsed():
    df = pd.DataFrame({"col": ["a   b", "  spaced   out  "]})
    result = clean_customer_names(df, "col", "cleaned")
    expected = pd.DataFrame(
        {
            "col": ["a   b", "  spaced   out  "],
            "cleaned": ["a b", "spaced out"],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_null_values():
    df = pd.DataFrame({"name": [None, np.nan, pd.NA, "John"]})
    result = clean_customer_names(df, "name", "clean")
    expected = pd.DataFrame(
        {"name": [None, np.nan, pd.NA, "John"], "clean": [pd.NA, pd.NA, pd.NA, "john"]}
    )
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_blank_strings_as_na():
    df = pd.DataFrame({"name": ["", "   ", "abc"]})
    result = clean_customer_names(df, "name", "clean")
    expected = pd.DataFrame(
        {"name": ["", "   ", "abc"], "clean": [pd.NA, pd.NA, "abc"]}
    )
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_preserve_original_dataframe():
    df = pd.DataFrame({"name": ["Alice", "Bob"]})
    original = df.copy()
    _ = clean_customer_names(df, "name", "clean")
    # Original should not have the new column and remain unchanged
    assert list(df.columns) == ["name"]
    pd.testing.assert_frame_equal(df, original)


def test_custom_output_column_name():
    df = pd.DataFrame({"raw": ["  TEST  "]})
    result = clean_customer_names(df, "raw", "custom_clean")
    assert "custom_clean" in result.columns
    assert result["custom_clean"].iloc[0] == "test"


def test_duplicate_entries():
    df = pd.DataFrame({"name": ["João", "João", "Maria", "Maria"]})
    result = clean_customer_names(df, "name", "normalized")
    # All rows must be treated independently
    expected_normalized = ["joao", "joao", "maria", "maria"]
    assert result["normalized"].tolist() == expected_normalized


def test_empty_dataframe():
    df = pd.DataFrame({"name": pd.Series(dtype="object")})
    result = clean_customer_names(df, "name", "clean")
    assert isinstance(result, pd.DataFrame)
    assert "clean" in result.columns
    assert len(result) == 0


def test_dataframe_with_other_columns_preserved():
    df = pd.DataFrame(
        {"id": [1, 2], "name": ["Alice", "Bob"], "age": [30, 25]}
    )
    result = clean_customer_names(df, "name", "normalized")
    # Check id and age columns are intact and in same order
    assert list(result.columns) == ["id", "name", "age", "normalized"]
    assert result["id"].tolist() == [1, 2]
    assert result["age"].tolist() == [30, 25]
    assert result["normalized"].tolist() == ["alice", "bob"]


def test_additional_output_column_type():
    df = pd.DataFrame({"name": ["Hello World"]})
    result = clean_customer_names(df, "name", "clean")
    # The normalized column should be of object (string) dtype
    assert result["clean"].dtype == np.object_
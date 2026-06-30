import pandas as pd
import numpy as np
from ise26.targets import clean_customer_names


def test_basic_standardization():
    """Normalize typical customer names: lowercase, trim, remove accents."""
    df = pd.DataFrame({"customer_name": ["  John   Doe  ", "María", "   JOSÉ   GARCÍA   "]})
    result = clean_customer_names(df)
    expected = pd.Series(["john doe", "maria", "jose garcía"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_empty_and_whitespace_only_names():
    """Blank or whitespace-only names become NA."""
    df = pd.DataFrame({"customer_name": ["", "   ", "   ", "Alice"]})
    result = clean_customer_names(df)
    expected = pd.Series([pd.NA, pd.NA, pd.NA, "alice"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_null_values():
    """None, NaN, and pd.NA in input become NA in output."""
    df = pd.DataFrame({"customer_name": [None, np.nan, pd.NA, "Bob"]})
    result = clean_customer_names(df)
    expected = pd.Series([pd.NA, pd.NA, pd.NA, "bob"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_accents_and_multiple_spaces():
    """Accented characters are replaced, multiple spaces collapsed."""
    df = pd.DataFrame({"customer_name": ["   São   João   ", "François", "München   " ]})
    result = clean_customer_names(df)
    expected = pd.Series(["sao joao", "francois", "munchen"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_original_dataframe_unchanged():
    """Input DataFrame is not mutated after call."""
    original = pd.DataFrame({"customer_name": ["  Luis   ", "Ana"]})
    original_copy = original.copy()
    _ = clean_customer_names(original)
    pd.testing.assert_frame_equal(original, original_copy)


def test_returns_new_dataframe():
    """Returned object is a different DataFrame from input."""
    df = pd.DataFrame({"customer_name": ["Test"]})
    result = clean_customer_names(df)
    assert result is not df


def test_custom_column_names():
    """User-supplied input and output column names work."""
    df = pd.DataFrame({"raw": ["  Alice  ", "  Bob  "]})
    result = clean_customer_names(df, name_col="raw", output_col="clean")
    expected = pd.Series(["alice", "bob"], name="clean")
    pd.testing.assert_series_equal(result["clean"], expected)


def test_default_column_names():
    """Default parameters produce expected column names."""
    df = pd.DataFrame({"customer_name": ["Test"]})
    result = clean_customer_names(df)
    assert "customer_name_clean" in result.columns


def test_mixed_case_preserved_and_lowercased():
    """Input with mixed case becomes fully lowercase."""
    df = pd.DataFrame({"customer_name": ["John", "ALICE", "bOb"]})
    result = clean_customer_names(df)
    expected = pd.Series(["john", "alice", "bob"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_duplicate_names():
    """Duplicate names are handled correctly."""
    df = pd.DataFrame({"customer_name": ["John", "john", "John"]})
    result = clean_customer_names(df)
    expected = pd.Series(["john", "john", "john"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)
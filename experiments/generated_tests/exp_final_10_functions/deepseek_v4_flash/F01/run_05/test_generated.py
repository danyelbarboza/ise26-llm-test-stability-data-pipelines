import pytest
import pandas as pd
import numpy as np
from ise26.targets import clean_customer_names


def test_returns_new_dataframe_with_extra_column():
    """Should return a new DataFrame with the normalized column added."""
    df = pd.DataFrame({"customer_name": ["Alice", "Bob"]})
    result = clean_customer_names(df)
    assert isinstance(result, pd.DataFrame)
    assert "customer_name_clean" in result.columns
    assert list(result.columns) == ["customer_name", "customer_name_clean"]


def test_original_dataframe_unchanged():
    """The original DataFrame must not be mutated."""
    df = pd.DataFrame({"customer_name": ["  John   Doe  "]})
    original = df.copy()
    _ = clean_customer_names(df)
    assert df.equals(original)


def test_normalizes_whitespace():
    """Extra spaces inside and around the name should be collapsed."""
    df = pd.DataFrame({"customer_name": ["  Mary   Jane  "]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "mary jane"


def test_lowercases_name():
    """Names should be lowercased."""
    df = pd.DataFrame({"customer_name": ["John SMITH"]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "john smith"


def test_removes_accents():
    """Accented characters should be converted to ASCII equivalents."""
    df = pd.DataFrame({"customer_name": ["José María López"]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "jose maria lopez"


def test_handles_mixed_accents_and_spaces():
    """Combination of accents, uppercase, and extra whitespace."""
    df = pd.DataFrame({"customer_name": ["  CäroLyn  Müller  "]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "carolyn muller"


def test_null_input_becomes_na():
    """pd.NA or None in input should become pd.NA in output."""
    df = pd.DataFrame({"customer_name": [pd.NA, None]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] is pd.NA
    assert result["customer_name_clean"].iloc[1] is pd.NA


def test_blank_string_becomes_na():
    """Whitespace-only strings should be mapped to pd.NA."""
    df = pd.DataFrame({"customer_name": ["", "   "]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] is pd.NA
    assert result["customer_name_clean"].iloc[1] is pd.NA


def test_mixed_valid_and_blank():
    """Mixed values: valid names and blanks produce correct output."""
    df = pd.DataFrame({"customer_name": ["John", "", "  Anna  "]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "john"
    assert result["customer_name_clean"].iloc[1] is pd.NA
    assert result["customer_name_clean"].iloc[2] == "anna"


def test_numeric_or_non_string_input():
    """Non-string types (e.g., numeric) should be converted to string and normalized."""
    df = pd.DataFrame({"customer_name": [123, 45.67]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "123"
    assert result["customer_name_clean"].iloc[1] == "45.67"


def test_custom_column_names():
    """Should accept custom input and output column names."""
    df = pd.DataFrame({"raw": ["  Alice  "]})
    result = clean_customer_names(df, name_col="raw", output_col="clean")
    assert "clean" in result.columns
    assert result["clean"].iloc[0] == "alice"


def test_default_column_name_works():
    """Should work with default column names when the input column exists."""
    df = pd.DataFrame({"customer_name": ["Test"]})
    result = clean_customer_names(df)
    assert "customer_name_clean" in result.columns


def test_raises_key_error_if_name_col_missing():
    """Should raise KeyError if the specified name column does not exist."""
    df = pd.DataFrame({"other": ["value"]})
    with pytest.raises(KeyError, match="name_col"):
        clean_customer_names(df, name_col="customer_name")


def test_handles_nan():
    """np.nan should also be mapped to pd.NA."""
    df = pd.DataFrame({"customer_name": [np.nan]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] is pd.NA


def test_preserves_other_columns():
    """Columns not involved should remain unchanged."""
    df = pd.DataFrame({"id": [1, 2], "customer_name": ["Alice", "Bob"]})
    result = clean_customer_names(df)
    assert list(result.columns) == ["id", "customer_name", "customer_name_clean"]
    assert result["id"].tolist() == [1, 2]
    assert result["customer_name"].tolist() == ["Alice", "Bob"]


def test_hyphen_and_special_characters():
    """Hyphens and apostrophes should be preserved after normalization."""
    df = pd.DataFrame({"customer_name": ["   O'Brien   "]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "o'brien"


def test_consecutive_accents_and_tilde_n():
    """Ensure proper removal of multiple accents and ñ -> n."""
    df = pd.DataFrame({"customer_name": ["Ñuñez Sánchez"]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "nunez sanchez"


def test_very_long_name():
    """Long names should still be processed correctly."""
    long_name = "  " + "A" * 100 + "  "
    df = pd.DataFrame({"customer_name": [long_name]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].iloc[0] == "a" * 100


def test_empty_dataframe():
    """Should handle an empty DataFrame gracefully."""
    df = pd.DataFrame({"customer_name": pd.Series(dtype="object")})
    result = clean_customer_names(df)
    assert len(result) == 0
    assert "customer_name_clean" in result.columns


def test_output_column_is_string_dtype():
    """The new column should be of string dtype (object or string)."""
    df = pd.DataFrame({"customer_name": ["Alice"]})
    result = clean_customer_names(df)
    assert result["customer_name_clean"].dtype == object
import pandas as pd
import pytest
from ise26.targets import validate_schema


def test_valid_schema():
    df = pd.DataFrame({
        "a": [1, 2, 3],
        "b": [1.0, 2.0, 3.0],
        "c": ["x", "y", "z"],
        "d": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        "e": [True, False, True],
    })
    schema = {"a": "int", "b": "float", "c": "string", "d": "datetime", "e": "bool"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_missing_columns():
    df = pd.DataFrame({"a": [1, 2]})
    schema = {"a": "int", "b": "string"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == ["b"]
    assert result["type_errors"] == []


def test_type_mismatch():
    df = pd.DataFrame({
        "a": [1, 2],
        "b": ["x", "y"],
    })
    schema = {"a": "string", "b": "int"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == []
    # order of type_errors may vary if schema iteration order is preserved (Python 3.7+), but we can check individually
    errors = {(e["column"], e["expected_type"], e["actual_type"]) for e in result["type_errors"]}
    assert ("a", "string", "int") in errors
    assert ("b", "int", "string") in errors


def test_extra_columns_allowed():
    df = pd.DataFrame({
        "a": [1],
        "extra1": [10],
        "extra2": [20],
    })
    schema = {"a": "int"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_supported_type_normalization():
    # Case and whitespace should be normalized
    df = pd.DataFrame({"a": [1, 2]})
    schema = {"a": "  Int  "}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []

    schema_lower = {"a": "int"}
    result2 = validate_schema(df, schema_lower)
    assert result2 == result


def test_unsupported_type_raises_valueerror():
    df = pd.DataFrame({"a": [1]})
    schema = {"a": "integer"}
    with pytest.raises(ValueError):
        validate_schema(df, schema)

    schema_bad = {"a": "date"}
    with pytest.raises(ValueError):
        validate_schema(df, schema_bad)


def test_empty_dataframe():
    df = pd.DataFrame()
    schema = {"a": "int"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == ["a"]
    assert result["type_errors"] == []


def test_empty_schema():
    df = pd.DataFrame({"a": [1]})
    schema = {}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_null_values():
    # Null values in object columns should still be considered string
    df = pd.DataFrame({"a": [None, "text"]})
    schema = {"a": "string"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []


def test_datetime_column():
    df = pd.DataFrame({"a": pd.to_datetime(["2020-01-01", None])})
    schema = {"a": "datetime"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []


def test_bool_column():
    df = pd.DataFrame({"a": [True, False, None]})
    schema = {"a": "bool"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []


def test_mixed_valid_and_invalid():
    df = pd.DataFrame({
        "good": [1, 2],
        "bad_type": ["x", "y"],
        "missing_schema": [10, 20],
    })
    schema = {"good": "int", "bad_type": "int", "gone": "float"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == ["gone"]
    # type error for bad_type
    type_cols = [e["column"] for e in result["type_errors"]]
    assert "bad_type" in type_cols
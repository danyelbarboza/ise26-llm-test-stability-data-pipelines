import pandas as pd
import pytest
from ise26.targets import validate_schema


def test_valid_schema_all_types():
    df = pd.DataFrame({
        "a": [1, 2],
        "b": [1.0, 2.0],
        "c": ["x", "y"],
        "d": pd.to_datetime(["2020-01-01", "2020-01-02"]),
        "e": [True, False],
    })
    schema = {
        "a": "int",
        "b": "float",
        "c": "string",
        "d": "datetime",
        "e": "bool",
    }
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_valid_schema_number_type():
    df = pd.DataFrame({
        "int_col": [1, 2],
        "float_col": [1.0, 2.0],
    })
    schema = {
        "int_col": "number",
        "float_col": "number",
    }
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
    assert len(result["type_errors"]) == 2
    for error in result["type_errors"]:
        assert "column" in error
        assert "expected_type" in error
        assert "actual_type" in error


def test_extra_columns_allowed():
    df = pd.DataFrame({
        "a": [1],
        "b": [2],
        "extra": [3],
    })
    schema = {"a": "int", "b": "int"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_empty_dataframe():
    df = pd.DataFrame()
    schema = {"a": "int", "b": "string"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == ["a", "b"]
    assert result["type_errors"] == []


def test_empty_schema():
    df = pd.DataFrame({"a": [1]})
    schema = {}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_unsupported_expected_type_raises():
    df = pd.DataFrame({"a": [1]})
    schema = {"a": "list"}
    with pytest.raises(ValueError):
        validate_schema(df, schema)


def test_normalized_expected_types():
    df = pd.DataFrame({
        "a": [1],
        "b": [1.0],
        "c": ["x"],
        "d": pd.to_datetime(["2020-01-01"]),
        "e": [True],
    })
    schema = {
        "a": " Int ",
        "b": " FLOAT ",
        "c": " String ",
        "d": " DATETIME ",
        "e": " BOOL ",
    }
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["missing_columns"] == []
    assert result["type_errors"] == []


def test_datetime_type():
    df = pd.DataFrame({"dt": pd.to_datetime(["2020-01-01", "2020-01-02"])})
    schema = {"dt": "datetime"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []


def test_bool_type():
    df = pd.DataFrame({"flag": [True, False]})
    schema = {"flag": "bool"}
    result = validate_schema(df, schema)
    assert result["valid"] is True
    assert result["type_errors"] == []


def test_int_as_number():
    df = pd.DataFrame({"a": [1, 2]})
    schema = {"a": "number"}
    result = validate_schema(df, schema)
    assert result["valid"] is True


def test_float_as_number():
    df = pd.DataFrame({"a": [1.0, 2.0]})
    schema = {"a": "number"}
    result = validate_schema(df, schema)
    assert result["valid"] is True


def test_number_mismatch():
    df = pd.DataFrame({"a": ["x", "y"]})
    schema = {"a": "number"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert len(result["type_errors"]) == 1
    assert result["type_errors"][0]["expected_type"] == "number"


def test_null_values_affect_type():
    # An integer column with NaN becomes float in pandas
    df = pd.DataFrame({"a": [1, None]})
    schema = {"a": "int"}
    result = validate_schema(df, schema)
    # actual type is likely 'float' due to NaN
    assert result["valid"] is False
    assert len(result["type_errors"]) == 1


def test_all_missing_and_mismatch():
    df = pd.DataFrame({"x": [1]})
    schema = {"y": "int", "x": "string"}
    result = validate_schema(df, schema)
    assert result["valid"] is False
    assert result["missing_columns"] == ["y"]
    assert len(result["type_errors"]) == 1
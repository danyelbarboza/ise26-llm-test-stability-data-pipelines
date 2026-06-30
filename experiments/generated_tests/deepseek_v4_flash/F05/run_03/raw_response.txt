import pandas as pd
import pytest
from ise26.targets import validate_schema


class TestValidateSchema:

    def test_valid_schema_all_columns_present(self):
        """All required columns exist with correct types."""
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Alice", "Bob"],
            "score": [95.5, 88.3],
            "active": [True, False],
            "birth": pd.to_datetime(["2000-01-01", "1999-12-31"]),
        })
        schema = {"id": "int", "name": "string", "score": "float",
                  "active": "bool", "birth": "datetime"}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_extra_columns_allowed(self):
        """Extra columns beyond schema are allowed."""
        df = pd.DataFrame({
            "a": [1],
            "b": ["x"],
            "c": [3.14],
        })
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_missing_columns(self):
        """Missing columns are reported."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "int", "b": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]

    def test_type_mismatch_int_expected_float_actual(self):
        """Column with float values and expected int causes type error."""
        df = pd.DataFrame({"a": [1.0, 2.5]})
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        error = result["type_errors"][0]
        assert error["column"] == "a"
        assert error["expected_type"] == "int"
        assert error["actual_type"] == "float"

    def test_type_mismatch_string_expected_int(self):
        """String column expected int causes type error."""
        df = pd.DataFrame({"a": ["1", "2"]})
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        error = result["type_errors"][0]
        assert error["expected_type"] == "int"
        assert error["actual_type"] == "string"

    def test_type_mismatch_datetime_expected_string(self):
        """Datetime column expected string causes type error."""
        df = pd.DataFrame({"a": pd.to_datetime(["2020-01-01"])})
        schema = {"a": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        error = result["type_errors"][0]
        assert error["expected_type"] == "string"
        assert error["actual_type"] == "datetime"

    def test_type_mismatch_bool_expected_int(self):
        """Bool column expected int causes type error."""
        df = pd.DataFrame({"a": [True, False]})
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        error = result["type_errors"][0]
        assert error["expected_type"] == "int"
        assert error["actual_type"] == "bool"

    def test_number_type_accepts_int_and_float(self):
        """Number expected type accepts both int and float columns."""
        df = pd.DataFrame({
            "i": [1, 2],
            "f": [1.5, 2.5],
        })
        schema = {"i": "number", "f": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_number_type_rejects_string(self):
        """Number expected type rejects string column."""
        df = pd.DataFrame({"a": ["1", "2"]})
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "number"
        assert result["type_errors"][0]["actual_type"] == "string"

    def test_expected_type_normalization_strip_lowercase(self):
        """Expected types are normalized (strip + lower)."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": " INT "}  # extra spaces and uppercase
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_unsupported_expected_type_raises_valueerror(self):
        """Unsupported expected type raises ValueError."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "category"}
        with pytest.raises(ValueError, match="unsupported expected type"):
            validate_schema(df, schema)

    def test_mixed_errors_missing_and_type(self):
        """Reports both missing columns and type errors."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "string", "b": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["column"] == "a"
        assert result["type_errors"][0]["expected_type"] == "string"

    def test_empty_dataframe_with_columns(self):
        """Empty DataFrame with correct columns is valid."""
        df = pd.DataFrame({"a": pd.Series([], dtype=int)})
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_empty_schema(self):
        """Empty schema always returns valid."""
        df = pd.DataFrame({"a": [1]})
        schema = {}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_empty_dataframe_missing_column_not_present(self):
        """Missing column in empty DataFrame is reported."""
        df = pd.DataFrame()  # no columns
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["a"]

    def test_float_expected_float_actual(self):
        """Float column with expected float passes."""
        df = pd.DataFrame({"a": [1.0, 2.0]})
        schema = {"a": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_int_expected_int_actual(self):
        """Integer column with expected int passes."""
        df = pd.DataFrame({"a": [1, 2]})
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_string_expected_string_actual(self):
        """String column with expected string passes."""
        df = pd.DataFrame({"a": ["hello", "world"]})
        schema = {"a": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_datetime_expected_datetime_actual(self):
        """Datetime column with expected datetime passes."""
        df = pd.DataFrame({"a": pd.to_datetime(["2020-01-01"])})
        schema = {"a": "datetime"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_bool_expected_bool_actual(self):
        """Bool column with expected bool passes."""
        df = pd.DataFrame({"a": [True, False]})
        schema = {"a": "bool"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_multiple_type_errors_all_reported(self):
        """All type errors are reported for multiple mismatched columns."""
        df = pd.DataFrame({
            "a": [1],
            "b": ["x"],
            "c": [1.5],
        })
        schema = {"a": "string", "b": "int", "c": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 3

    def test_case_insensitivity_in_expected_types(self):
        """Case insensitive expected type labels are normalized."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "Int"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_unsupported_type_list(self):
        """List type is unsupported."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "list"}
        with pytest.raises(ValueError):
            validate_schema(df, schema)
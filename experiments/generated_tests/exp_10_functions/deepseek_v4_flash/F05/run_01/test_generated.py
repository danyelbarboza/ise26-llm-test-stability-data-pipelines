import pytest
import pandas as pd
from ise26.targets import validate_schema


class TestValidateSchema:
    """Test suite for validate_schema function."""

    def test_valid_schema_all_types_present(self):
        """All required columns with correct types should pass."""
        df = pd.DataFrame({
            "col_int": [1, 2, 3],
            "col_float": [1.1, 2.2, 3.3],
            "col_number": [1, 2, 3],  # int is valid for 'number'
            "col_str": ["a", "b", "c"],
            "col_dt": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            "col_bool": [True, False, True],
        })
        schema = {
            "col_int": "int",
            "col_float": "float",
            "col_number": "number",
            "col_str": "string",
            "col_dt": "datetime",
            "col_bool": "bool",
        }
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_extra_columns_allowed(self):
        """Extra columns not in schema should be ignored."""
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [3.0, 4.0],
            "extra": ["x", "y"],
        })
        schema = {"a": "int", "b": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_missing_columns_reported(self):
        """Columns in schema but absent from DataFrame should be reported."""
        df = pd.DataFrame({"a": [1, 2]})
        schema = {"a": "int", "b": "string", "c": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert set(result["missing_columns"]) == {"b", "c"}
        assert result["type_errors"] == []

    def test_type_mismatch_detected(self):
        """Type mismatches should be reported with column, expected_type, actual_type."""
        df = pd.DataFrame({
            "int_col": [1, 2],
            "str_col": ["x", "y"],
            "float_col": [1.1, 2.2],
            "bool_col": [True, False],
            "dt_col": pd.to_datetime(["2021-01-01", "2021-01-02"]),
        })
        schema = {
            "int_col": "float",      # wrong: int != float
            "str_col": "int",        # wrong: string != int
            "float_col": "string",   # wrong: float != string
            "bool_col": "datetime",  # wrong: bool != datetime
            "dt_col": "bool",        # wrong: datetime != bool
        }
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == []
        assert len(result["type_errors"]) == 5
        for err in result["type_errors"]:
            assert "column" in err
            assert "expected_type" in err
            assert "actual_type" in err

    def test_normalized_expected_type(self):
        """Expected types with extra spaces or different case should be normalized."""
        df = pd.DataFrame({"col": [1, 2, 3]})
        schema = {"col": "  INT  "}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["type_errors"] == []

    def test_unsupported_expected_type_raises_valueerror(self):
        """Schema with an unsupported expected type should raise ValueError."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "category"}
        with pytest.raises(ValueError):
            validate_schema(df, schema)

    def test_type_number_accepts_int(self):
        """'number' expected type should accept integer column."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_type_number_accepts_float(self):
        """'number' expected type should accept float column."""
        df = pd.DataFrame({"a": [1.1, 2.2, 3.3]})
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_type_number_rejects_string(self):
        """'number' expected type should reject string column."""
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["type_errors"][0]["expected_type"] == "number"

    def test_empty_dataframe_no_columns(self):
        """Empty DataFrame with no columns and empty schema should be valid."""
        df = pd.DataFrame()
        schema = {}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_empty_dataframe_with_schema(self):
        """Empty DataFrame (no rows) with columns should still have correct types."""
        df = pd.DataFrame({
            "a": pd.Series([], dtype=int),
            "b": pd.Series([], dtype=str),
        })
        schema = {"a": "int", "b": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_nan_in_float_column(self):
        """Float column with NaN should still be recognized as float."""
        df = pd.DataFrame({"a": [1.0, None, 3.0]})
        schema = {"a": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_nan_in_string_column(self):
        """String column with NaN (object dtype) should be recognized as string."""
        df = pd.DataFrame({"a": ["x", None, "z"]})
        schema = {"a": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_datetime_with_nat(self):
        """Datetime column with NaT should still be recognized as datetime."""
        df = pd.DataFrame({"a": pd.to_datetime(["2021-01-01", None, "2021-01-03"])})
        schema = {"a": "datetime"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_mixed_ints_and_floats(self):
        """Column with mixed ints and floats -> actual type float, expected number passes."""
        df = pd.DataFrame({"a": [1, 2.5, 3]})
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_missing_and_type_errors_together(self):
        """Both missing columns and type mismatches should be reported."""
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "string", "b": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["column"] == "a"
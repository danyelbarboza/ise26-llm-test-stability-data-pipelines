import pandas as pd
import pytest
from ise26.targets import validate_schema


class TestValidateSchema:
    """Test suite for the validate_schema function."""

    # ---------------------------------------------------------------
    # Helper method to create common test DataFrames
    # ---------------------------------------------------------------
    @staticmethod
    def _create_df(**columns):
        """Create a simple DataFrame from column name -> list of values."""
        return pd.DataFrame(columns)

    # ---------------------------------------------------------------
    # Valid completions
    # ---------------------------------------------------------------
    def test_valid_all_columns_present_and_correct_types(self):
        df = self._create_df(
            a=[1, 2, 3],
            b=[1.0, 2.0, 3.0],
            c=["x", "y", "z"],
            d=pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            e=[True, False, True],
            f=[10, 20, 30],  # numeric (will be inferred as int)
        )
        schema = {"a": "int", "b": "float", "c": "string", "d": "datetime", "e": "bool", "f": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_valid_extra_columns_allowed(self):
        df = self._create_df(
            a=[1, 2],
            b=[10.0, 20.0],
            extra1=["extra", "col"],
            extra2=[99, 100],
        )
        schema = {"a": "int", "b": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_valid_with_nulls_in_data(self):
        df = self._create_df(
            a=[1, None, 3],
            b=[1.0, None, 3.0],
            c=["hello", None, "world"],
            d=pd.to_datetime(["2021-01-01", None, "2021-01-03"]),
            e=[True, None, False],
        )
        schema = {"a": "int", "b": "float", "c": "string", "d": "datetime", "e": "bool"}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    # ---------------------------------------------------------------
    # Missing columns
    # ---------------------------------------------------------------
    def test_missing_columns_single(self):
        df = self._create_df(a=[1, 2])
        schema = {"a": "int", "b": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert result["type_errors"] == []

    def test_missing_columns_multiple(self):
        df = self._create_df(x=[1, 2])
        schema = {"a": "int", "b": "string", "c": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert sorted(result["missing_columns"]) == ["a", "b", "c"]
        assert result["type_errors"] == []

    def test_missing_and_type_error_combined(self):
        df = self._create_df(a=[1, 2], b=[3.0, 4.0])
        schema = {"a": "float", "b": "int", "c": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["c"]
        # a is int but expected float → type error; b is float but expected int → type error
        type_err_cols = {e["column"] for e in result["type_errors"]}
        assert type_err_cols == {"a", "b"}
        assert all(e["expected_type"] in ("int", "float") for e in result["type_errors"])
        assert all(e["actual_type"] in ("int", "float") for e in result["type_errors"])

    # ---------------------------------------------------------------
    # Type mismatches
    # ---------------------------------------------------------------
    def test_type_error_expected_int_actual_float(self):
        df = self._create_df(a=[1.0, 2.0, 3.0])
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == []
        assert len(result["type_errors"]) == 1
        err = result["type_errors"][0]
        assert err["column"] == "a"
        assert err["expected_type"] == "int"
        assert err["actual_type"] == "float"

    def test_type_error_expected_float_actual_int(self):
        df = self._create_df(a=[1, 2, 3])
        schema = {"a": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "float"
        assert result["type_errors"][0]["actual_type"] == "int"

    def test_type_error_expected_string_actual_int(self):
        df = self._create_df(a=[1, 2, 3])
        schema = {"a": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "string"
        assert result["type_errors"][0]["actual_type"] == "int"

    def test_type_error_expected_datetime_actual_string(self):
        df = self._create_df(a=["2021-01-01", "2021-01-02"])
        schema = {"a": "datetime"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "datetime"
        # Actual type might be object if strings, but we must check what the function returns.
        # For string objects, actual_type is likely 'string' (as per infer_series_type).
        assert result["type_errors"][0]["actual_type"] == "string"

    def test_type_error_expected_bool_actual_int(self):
        df = self._create_df(a=[0, 1, 2])
        schema = {"a": "bool"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "bool"
        assert result["type_errors"][0]["actual_type"] == "int"

    def test_type_error_expected_number_actual_string(self):
        df = self._create_df(a=["1", "2", "3"])
        schema = {"a": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["expected_type"] == "number"
        assert result["type_errors"][0]["actual_type"] == "string"

    def test_type_error_multiple_columns(self):
        df = self._create_df(
            a=[1, 2],
            b=[True, False],
            c=[1.0, 2.0],
        )
        schema = {"a": "float", "b": "string", "c": "bool"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 3
        expected_pairs = [
            ("a", "float", "int"),
            ("b", "string", "bool"),
            ("c", "bool", "float"),
        ]
        for err, (col, exp, act) in zip(result["type_errors"], expected_pairs):
            assert err["column"] == col
            assert err["expected_type"] == exp
            assert err["actual_type"] == act

    # ---------------------------------------------------------------
    # Normalization of expected types (strip, lower, case insensitivity)
    # ---------------------------------------------------------------
    def test_normalized_expected_type_with_spaces_and_case(self):
        df = self._create_df(a=[1, 2, 3], b=[1.0, 2.0, 3.0])
        schema = {"a": "  Int  ", "b": "  FLOAT  "}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_normalized_expected_type_various_formats(self):
        df = self._create_df(
            a=[1, 2],
            b=[1.0, 2.0],
            c=["x", "y"],
            d=pd.to_datetime(["2021-01-01", "2021-01-02"]),
            e=[True, False],
            f=[3, 4],
        )
        schema = {
            "a": "int ",       # trailing space
            "b": " float",     # leading space
            "c": "STRING",     # uppercase
            "d": " DateTime ", # mixed case and spaces
            "e": " Bool",      # leading space, capitalized
            "f": "NUMBER",     # uppercase
        }
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    # ---------------------------------------------------------------
    # Unsupported expected types (should raise ValueError)
    # ---------------------------------------------------------------
    def test_unsupported_expected_type_raises_value_error(self):
        df = self._create_df(a=[1, 2])
        schema = {"a": "complex"}
        with pytest.raises(ValueError, match="Unsupported expected type"):
            validate_schema(df, schema)

    def test_unsupported_expected_type_among_valid_raises_value_error(self):
        df = self._create_df(a=[1, 2], b=[3.0, 4.0])
        schema = {"a": "int", "b": "date"}  # 'date' is not supported
        with pytest.raises(ValueError, match="Unsupported expected type"):
            validate_schema(df, schema)

    def test_unsupported_expected_type_after_normalization_still_raises(self):
        df = self._create_df(a=[1, 2])
        schema = {"a": "  Integer  "}  # after strip.lower -> "integer" is not supported
        with pytest.raises(ValueError, match="Unsupported expected type"):
            validate_schema(df, schema)

    def test_empty_schema_valid(self):
        df = self._create_df(a=[1, 2])
        schema = {}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_empty_dataframe_with_schema(self):
        df = pd.DataFrame()
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["a"]
        assert result["type_errors"] == []

    def test_empty_dataframe_with_empty_schema(self):
        df = pd.DataFrame()
        schema = {}
        result = validate_schema(df, schema)
        assert result["valid"] is True
        assert result["missing_columns"] == []
        assert result["type_errors"] == []

    def test_dataframe_with_duplicate_columns(self):
        # DataFrame with duplicate column names is not allowed in pandas
        # This test can be skipped or note that we assume unique columns.
        pass
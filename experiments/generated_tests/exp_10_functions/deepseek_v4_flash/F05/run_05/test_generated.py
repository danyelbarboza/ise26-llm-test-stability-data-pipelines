import pytest
import pandas as pd
from ise26.targets import validate_schema


class TestValidateSchema:
    def test_schema_empty(self):
        df = pd.DataFrame({"a": [1]})
        result = validate_schema(df, {})
        assert result == {
            "valid": True,
            "missing_columns": [],
            "type_errors": [],
        }

    def test_valid_types(self):
        df = pd.DataFrame(
            {
                "int_col": [1, 2],
                "float_col": [1.0, 2.0],
                "number_int": [3, 4],
                "number_float": [3.0, 4.0],
                "str_col": ["a", "b"],
                "datetime_col": pd.to_datetime(["2021-01-01", "2021-01-02"]),
                "bool_col": [True, False],
            }
        )
        schema = {
            "int_col": "int",
            "float_col": "float",
            "number_int": "number",
            "number_float": "number",
            "str_col": "string",
            "datetime_col": "datetime",
            "bool_col": "bool",
        }
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_missing_column(self):
        df = pd.DataFrame({"a": [1]})
        schema = {"b": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert result["type_errors"] == []

    def test_type_mismatch(self):
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "string"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        error = result["type_errors"][0]
        assert error["column"] == "a"
        assert error["expected_type"] == "string"
        # actual_type should not be "string" for an integer column
        assert error["actual_type"] != "string"

    def test_extra_columns_allowed(self):
        df = pd.DataFrame({"req": [1], "extra": ["x"]})
        schema = {"req": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_normalized_types(self):
        # whitespace and case normalization
        df = pd.DataFrame({"a": [1]})
        schema = {"a": " Int "}
        result = validate_schema(df, schema)
        assert result["valid"] is True

        df2 = pd.DataFrame({"a": [1.0]})
        schema2 = {"a": "FLOAT"}
        result2 = validate_schema(df2, schema2)
        assert result2["valid"] is True

    def test_unsupported_type_raises(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(ValueError):
            validate_schema(df, {"a": "unknown"})

    def test_multiple_errors(self):
        df = pd.DataFrame({"a": [1], "c": [True]})
        schema = {"a": "string", "b": "int", "c": "float"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert len(result["type_errors"]) == 2
        error_cols = {e["column"] for e in result["type_errors"]}
        assert "a" in error_cols
        assert "c" in error_cols

    def test_empty_dataframe_with_schema(self):
        df = pd.DataFrame()
        schema = {"a": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["a"]
        assert result["type_errors"] == []

    def test_datetime_type_match(self):
        df = pd.DataFrame(
            {"dt": pd.to_datetime(["2021-01-01", "2021-01-02"])}
        )
        result = validate_schema(df, {"dt": "datetime"})
        assert result["valid"] is True

    def test_bool_type_match(self):
        df = pd.DataFrame({"b": [True, False]})
        result = validate_schema(df, {"b": "bool"})
        assert result["valid"] is True

    def test_number_type_match_with_ints_and_floats(self):
        df = pd.DataFrame({"a": [1, 2], "b": [1.0, 2.0]})
        schema = {"a": "number", "b": "number"}
        result = validate_schema(df, schema)
        assert result["valid"] is True

    def test_mixed_valid_invalid(self):
        df = pd.DataFrame(
            {
                "good_int": [1],
                "bad_float_as_int": [1.5],
            }
        )
        schema = {
            "good_int": "int",
            "bad_float_as_int": "int",
        }
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["column"] == "bad_float_as_int"
        assert result["type_errors"][0]["expected_type"] == "int"

    def test_missing_column_and_type_error_together(self):
        df = pd.DataFrame({"a": [1]})
        schema = {"a": "string", "b": "int"}
        result = validate_schema(df, schema)
        assert result["valid"] is False
        assert result["missing_columns"] == ["b"]
        assert len(result["type_errors"]) == 1
        assert result["type_errors"][0]["column"] == "a"

    def test_all_expected_types_are_supported(self):
        supported = ["int", "float", "number", "string", "datetime", "bool"]
        for t in supported:
            df = pd.DataFrame({"c": [1]} if t == "int" else {"c": [1.0]})
            # Ajustar o DataFrame para cada tipo
            if t == "int":
                df = pd.DataFrame({"c": [1]})
            elif t == "float":
                df = pd.DataFrame({"c": [1.0]})
            elif t == "number":
                df = pd.DataFrame({"c": [1]})  # pode ser int ou float
            elif t == "string":
                df = pd.DataFrame({"c": ["x"]})
            elif t == "datetime":
                df = pd.DataFrame(
                    {"c": pd.to_datetime(["2021-01-01"])}
                )
            elif t == "bool":
                df = pd.DataFrame({"c": [True]})
            result = validate_schema(df, {"c": t})
            assert result["valid"] is True, f"Failed for type {t}"
import pandas as pd
import numpy as np
import pytest
from ise26.targets import clean_customer_names


class TestCleanCustomerNames:
    """Test suite for clean_customer_names function."""

    # ------------------------------------------------------------------
    # Basic transformation
    # ------------------------------------------------------------------
    def test_basic_normalisation(self):
        """Standard names with extra spaces and mixed case become clean."""
        df = pd.DataFrame({
            "customer_name": ["  Marie  Anne  ", "JOSÉ Santos", "john DOE"]
        })
        result = clean_customer_names(df)

        assert "customer_name_clean" in result.columns
        expected = ["marie anne", "jose santos", "john doe"]
        # convert to list and compare
        assert result["customer_name_clean"].tolist() == expected

    def test_lowercasing_and_whitespace_collapse(self):
        """Whitespace is collapsed and text is lowercased."""
        df = pd.DataFrame({
            "customer_name": [
                "  \tJean\t\t-Pierre  ",     # tabs and multiple spaces
                "   Luis   Carlos ",
                "PEDRO"
            ]
        })
        result = clean_customer_names(df)
        expected = ["jean-pierre", "luis carlos", "pedro"]
        assert result["customer_name_clean"].tolist() == expected

    def test_accent_removal(self):
        """Accented characters are replaced by their ASCII equivalents."""
        df = pd.DataFrame({
            "customer_name": [
                "José Álvares",
                "Mária Crüger",
                "Ñoño",
                "strășină"   # Romanian specific
            ]
        })
        result = clean_customer_names(df)
        expected = ["jose alvares", "maria cruger", "nono", "strasina"]
        assert result["customer_name_clean"].tolist() == expected

    # ------------------------------------------------------------------
    # Null / blank handling
    # ------------------------------------------------------------------
    def test_null_values_map_to_pdna(self):
        """None and numpy NaN become pd.NA in the output column."""
        df = pd.DataFrame({
            "customer_name": [None, np.nan, "Valid Name"]
        })
        result = clean_customer_names(df)
        col = result["customer_name_clean"]
        assert col[0] is pd.NA
        assert col[1] is pd.NA
        assert col[2] == "valid name"

    def test_blank_strings_map_to_pdna(self):
        """Empty and whitespace-only strings are treated as blank -> pd.NA."""
        df = pd.DataFrame({
            "customer_name": ["", "   ", "\t", " Bill "]
        })
        result = clean_customer_names(df)
        col = result["customer_name_clean"]
        assert col[0] is pd.NA
        assert col[1] is pd.NA
        assert col[2] is pd.NA
        assert col[3] == "bill"

    def test_mixed_nulls_and_blanks(self):
        """Combination of None, NaN, empty and whitespace returns pd.NA."""
        df = pd.DataFrame({
            "customer_name": [None, np.nan, "", "   ", "Valid", "\t \n"]
        })
        result = clean_customer_names(df)
        col = result["customer_name_clean"]
        for i in range(4):
            assert col[i] is pd.NA
        assert col[4] == "valid"
        assert col[5] is pd.NA

    # ------------------------------------------------------------------
    # Original DataFrame preservation
    # ------------------------------------------------------------------
    def test_original_dataframe_unchanged(self):
        """The input DataFrame is not mutated: no new column, data intact."""
        original = pd.DataFrame({
            "customer_name": ["Alice", "Bob  "],
            "other_col": [1, 2]
        })
        df_copy = original.copy()
        result = clean_customer_names(original)

        # original should be exactly as before
        pd.testing.assert_frame_equal(original, df_copy)
        # original should not have the new column
        assert "customer_name_clean" not in original.columns

        # result is a different object
        assert result is not original

    def test_returned_dataframe_contains_original_plus_new_column(self):
        """The output DataFrame contains all original columns + new clean column."""
        df = pd.DataFrame({
            "customer_name": ["Eve", "Adam"],
            "id": [10, 20]
        })
        result = clean_customer_names(df, output_col="normalized")
        expected_columns = ["customer_name", "id", "normalized"]
        assert list(result.columns) == expected_columns

    # ------------------------------------------------------------------
    # Custom column names
    # ------------------------------------------------------------------
    def test_custom_input_and_output_column_names(self):
        """Works with non-default column name arguments."""
        df = pd.DataFrame({
            "raw_name": ["  María Elena  ", " Carlos "]
        })
        result = clean_customer_names(df, name_col="raw_name", output_col="clean_name")
        assert "clean_name" in result.columns
        assert result["clean_name"].tolist() == ["maria elena", "carlos"]

    # ------------------------------------------------------------------
    # Error conditions
    # ------------------------------------------------------------------
    def test_missing_input_column_raises(self):
        """If the specified name_col is missing, function should raise an error."""
        df = pd.DataFrame({"not_name": [1, 2]})
        with pytest.raises(Exception):  # _ensure_columns_present likely raises KeyError or ValueError
            clean_customer_names(df, name_col="customer_name")

    def test_empty_dataframe_works(self):
        """An empty DataFrame should return an empty DataFrame with the new column."""
        df = pd.DataFrame({"customer_name": pd.Series(dtype="object")})
        result = clean_customer_names(df)
        assert result.empty
        assert "customer_name_clean" in result.columns
        assert result["customer_name_clean"].dtype == object

    # ------------------------------------------------------------------
    # dtype and conservation
    # ------------------------------------------------------------------
    def test_output_dtype_is_object_or_string(self):
        """The new column is object dtype (or a nullable string extension)."""
        df = pd.DataFrame({"customer_name": ["Some", "Names"]})
        result = clean_customer_names(df)
        col = result["customer_name_clean"]
        # pd.NA works with object or StringDtype; both are acceptable.
        assert col.dtype == object or pd.api.types.is_string_dtype(col.dtype)
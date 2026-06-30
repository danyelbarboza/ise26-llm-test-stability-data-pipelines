import pandas as pd
import pytest
from ise26.targets import parse_order_items_json

class TestParseOrderItemsJson:
    def test_basic_explode(self):
        """All fields valid and present."""
        df = pd.DataFrame({
            "order_id": [1, 2],
            "items_json": [
                '[{"sku": "A", "quantity": 2, "unit_price": 10}]',
                '[{"sku": "B", "quantity": 3, "unit_price": 5.5}]',
            ],
        })
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1, 2],
            "sku": ["A", "B"],
            "quantity": [2.0, 3.0],
            "unit_price": [10.0, 5.5],
            "item_total": [20.0, 16.5],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_items_per_order(self):
        """One order with several items, order preserved."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": [
                '[{"sku": "X", "quantity": 1, "unit_price": 100}, '
                '{"sku": "Y", "quantity": 2, "unit_price": 50}]',
            ],
        })
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1, 1],
            "sku": ["X", "Y"],
            "quantity": [1.0, 2.0],
            "unit_price": [100.0, 50.0],
            "item_total": [100.0, 100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_order_of_rows_and_items(self):
        """Multiple orders with multiple items: global order respects
        original row order and item list order."""
        df = pd.DataFrame({
            "order_id": [10, 20],
            "items_json": [
                '[{"sku": "a", "quantity": 1, "unit_price": 1}, '
                '{"sku": "b", "quantity": 1, "unit_price": 1}]',
                '[{"sku": "c", "quantity": 1, "unit_price": 1}]',
            ],
        })
        result = parse_order_items_json(df)
        expected_order_ids = [10, 10, 20]
        expected_skus = ["a", "b", "c"]
        assert result["order_id"].tolist() == expected_order_ids
        assert result["sku"].tolist() == expected_skus

    def test_missing_sku_becomes_na(self):
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"quantity": 1, "unit_price": 10}]'],
        })
        result = parse_order_items_json(df)
        assert result.shape == (1, 5)
        assert pd.isna(result.loc[0, "sku"])
        # sku column dtype is object
        assert result["sku"].dtype == object

    def test_invalid_quantity_zero(self):
        """quantity that cannot be parsed becomes 0."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"sku": "X", "quantity": "abc", "unit_price": 10}]'],
        })
        result = parse_order_items_json(df)
        assert result.loc[0, "quantity"] == 0.0
        assert result.loc[0, "item_total"] == 0.0

    def test_invalid_unit_price_zero(self):
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"sku": "X", "quantity": 5, "unit_price": null}]'],
        })
        result = parse_order_items_json(df)
        assert result.loc[0, "unit_price"] == 0.0
        assert result.loc[0, "item_total"] == 0.0

    def test_missing_quantity_or_unit_price_zero(self):
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": [
                '[{"sku": "A", "unit_price": 100}, '
                '{"sku": "B", "quantity": 10}]'
            ],
        })
        result = parse_order_items_json(df)
        # first item: quantity zero -> total zero
        assert result.loc[0, "quantity"] == 0.0
        assert result.loc[0, "item_total"] == 0.0
        # second item: unit_price zero -> total zero
        assert result.loc[1, "unit_price"] == 0.0
        assert result.loc[1, "item_total"] == 0.0

    def test_non_numeric_strings_coerced(self):
        """Strings that represent numbers are parsed."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": [
                '[{"sku": "X", "quantity": "3.14", "unit_price": "2.5"}]'
            ],
        })
        result = parse_order_items_json(df)
        assert result.loc[0, "quantity"] == 3.14
        assert result.loc[0, "unit_price"] == 2.5
        assert result.loc[0, "item_total"] == 7.85

    def test_json_not_a_list_skipped(self):
        """Non-list JSON payload (e.g., dict) is skipped entirely."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['{"sku": "A", "quantity": 1, "unit_price": 10}'],
        })
        result = parse_order_items_json(df)
        assert len(result) == 0

    def test_invalid_json_string_skipped(self):
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ["not a json"],
        })
        result = parse_order_items_json(df)
        assert len(result) == 0

    def test_empty_json_list_skipped(self):
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ["[]"],
        })
        result = parse_order_items_json(df)
        assert len(result) == 0

    def test_missing_json_value_skipped(self):
        df = pd.DataFrame({
            "order_id": [1, 2],
            "items_json": [None, pd.NA],
        })
        result = parse_order_items_json(df)
        assert len(result) == 0

    def test_custom_column_names(self):
        df = pd.DataFrame({
            "transaction": [101],
            "payload": ['[{"sku": "Z", "quantity": 1, "unit_price": 9.99}]'],
        })
        result = parse_order_items_json(
            df, json_col="payload", order_id_col="transaction"
        )
        assert "transaction" in result.columns
        assert "order_id" not in result.columns
        assert result["transaction"].iloc[0] == 101

    def test_preserves_order_id_dtype(self):
        """Output order_id column dtype matches input column dtype."""
        df_int = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"sku":"A","quantity":1,"unit_price":1}]'],
        })
        result_int = parse_order_items_json(df_int)
        assert result_int["order_id"].dtype == "int64"

        df_str = pd.DataFrame({
            "order_id": ["ORD-1"],
            "items_json": ['[{"sku":"A","quantity":1,"unit_price":1}]'],
        })
        result_str = parse_order_items_json(df_str)
        assert result_str["order_id"].dtype == object

    def test_output_dtypes(self):
        """All numeric output columns are float64."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"sku":"A","quantity":2,"unit_price":1.5}]'],
        })
        result = parse_order_items_json(df)
        assert result["quantity"].dtype == "float64"
        assert result["unit_price"].dtype == "float64"
        assert result["item_total"].dtype == "float64"

    def test_empty_dataframe(self):
        df = pd.DataFrame({"order_id": [], "items_json": []}).astype({"order_id": "int64"})
        result = parse_order_items_json(df)
        assert list(result.columns) == ["order_id", "sku", "quantity", "unit_price", "item_total"]
        assert len(result) == 0
        assert result["order_id"].dtype == "int64"
        assert result["sku"].dtype == object
        assert result["quantity"].dtype == "float64"
        assert result["unit_price"].dtype == "float64"
        assert result["item_total"].dtype == "float64"

    def test_item_with_non_dict_raises_attribute_error(self):
        """A JSON list containing a non-dict item (e.g., a number) will
        raise because the code expects a dict."""
        df = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[1, {"sku":"X","quantity":1,"unit_price":1}]'],
        })
        with pytest.raises(AttributeError):
            parse_order_items_json(df)

    def test_missing_json_column_raises(self):
        df = pd.DataFrame({"order_id": [1]})
        with pytest.raises(ValueError, match="parse_order_items_json"):
            parse_order_items_json(df)

    def test_missing_order_id_column_raises(self):
        df = pd.DataFrame({"items_json": ['[{"sku":"A"}]']})
        with pytest.raises(ValueError, match="parse_order_items_json"):
            parse_order_items_json(df)

    def test_output_index_is_default_range(self):
        """The returned DataFrame index is a fresh RangeIndex (reset)."""
        df = pd.DataFrame({
            "order_id": [100, 200],
            "items_json": [
                '[{"sku":"p","quantity":1,"unit_price":1}]',
                '[{"sku":"q","quantity":1,"unit_price":1}]',
            ],
        })
        result = parse_order_items_json(df)
        assert result.index.tolist() == [0, 1]
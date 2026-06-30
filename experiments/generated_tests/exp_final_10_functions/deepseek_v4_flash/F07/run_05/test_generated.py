import pytest
import pandas as pd
import numpy as np
from ise26.targets import parse_order_items_json


def _make_df(items_json, order_id_col="order_id", **kwargs):
    """Helper to create DataFrame with given items_json column."""
    data = {order_id_col: kwargs.get("order_ids", [1, 2, 3][:len(items_json)])}
    if len(data[order_id_col]) < len(items_json):
        # Extend order IDs if needed (default to 1,2,3...)
        data[order_id_col] = list(range(1, len(items_json) + 1))
    data["items_json"] = items_json
    return pd.DataFrame(data)


def _expected_dtypes():
    """Return dict of expected dtypes for output columns."""
    return {
        "order_id": "int64",   # default dtype from input
        "sku": "object",
        "quantity": "float64",
        "unit_price": "float64",
        "item_total": "float64",
    }


class TestParseOrderItemsJson:

    def test_single_order_single_item(self):
        df = _make_df(['[{"sku":"A","quantity":2,"unit_price":10.5}]'])
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1],
            "sku": ["A"],
            "quantity": [2.0],
            "unit_price": [10.5],
            "item_total": [21.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_single_order_multiple_items(self):
        items = '[{"sku":"A","quantity":1,"unit_price":5},{"sku":"B","quantity":3,"unit_price":2.5}]'
        df = _make_df([items])
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1, 1],
            "sku": ["A", "B"],
            "quantity": [1.0, 3.0],
            "unit_price": [5.0, 2.5],
            "item_total": [5.0, 7.5],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_orders(self):
        df = pd.DataFrame({
            "order_id": [101, 102],
            "items_json": [
                '[{"sku":"x","quantity":2,"unit_price":1}]',
                '[{"sku":"y","quantity":1,"unit_price":40}]'
            ]
        })
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [101, 102],
            "sku": ["x", "y"],
            "quantity": [2.0, 1.0],
            "unit_price": [1.0, 40.0],
            "item_total": [2.0, 40.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        df = pd.DataFrame({"order_id": pd.Series(dtype="int64"), "items_json": pd.Series(dtype="object")})
        result = parse_order_items_json(df)
        assert result.empty
        assert list(result.columns) == ["order_id", "sku", "quantity", "unit_price", "item_total"]
        assert result.dtypes["order_id"] == "int64"
        assert result.dtypes["sku"] == "object"
        assert result.dtypes["quantity"] == "float64"
        assert result.dtypes["unit_price"] == "float64"
        assert result.dtypes["item_total"] == "float64"

    def test_missing_json(self):
        df = pd.DataFrame({
            "order_id": [1, 2],
            "items_json": [np.nan, None]   # missing payloads
        })
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": pd.Series(dtype="int64"),
            "sku": pd.Series(dtype="object"),
            "quantity": pd.Series(dtype="float64"),
            "unit_price": pd.Series(dtype="float64"),
            "item_total": pd.Series(dtype="float64"),
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_json(self):
        # invalid JSON: string, number, dict
        df = pd.DataFrame({
            "order_id": [1, 2, 3],
            "items_json": [
                "not a list",
                123,
                '{"key":"value"}'
            ]
        })
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": pd.Series(dtype="int64"),
            "sku": pd.Series(dtype="object"),
            "quantity": pd.Series(dtype="float64"),
            "unit_price": pd.Series(dtype="float64"),
            "item_total": pd.Series(dtype="float64"),
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_json_list(self):
        df = _make_df(['[]'])
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": pd.Series(dtype="int64"),
            "sku": pd.Series(dtype="object"),
            "quantity": pd.Series(dtype="float64"),
            "unit_price": pd.Series(dtype="float64"),
            "item_total": pd.Series(dtype="float64"),
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_missing_sku(self):
        df = _make_df(['[{"quantity":1,"unit_price":10}]'])
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1],
            "sku": [pd.NA],
            "quantity": [1.0],
            "unit_price": [10.0],
            "item_total": [10.0],
        })
        # Note: pd.NA is converted to None in object column? Use pd.isna check
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
        assert pd.isna(result.iloc[0]["sku"])

    def test_invalid_quantity_unit_price(self):
        # Non-numeric or missing values should become zero
        df = _make_df(['[{"sku":"A","quantity":"bad","unit_price":None}]'])
        result = parse_order_items_json(df)
        expected = pd.DataFrame({
            "order_id": [1],
            "sku": ["A"],
            "quantity": [0.0],
            "unit_price": [0.0],
            "item_total": [0.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_custom_column_names(self):
        df = pd.DataFrame({
            "custom_id": [10],
            "payload": ['[{"sku":"Z","quantity":5,"unit_price":3}]']
        })
        result = parse_order_items_json(df, json_col="payload", order_id_col="custom_id")
        expected = pd.DataFrame({
            "custom_id": [10],
            "sku": ["Z"],
            "quantity": [5.0],
            "unit_price": [3.0],
            "item_total": [15.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_dtypes_preserved(self):
        # Check output dtypes exactly as expected
        df = pd.DataFrame({
            "order_id": pd.Series([1, 2], dtype="int32"),
            "items_json": [
                '[{"sku":"a","quantity":1,"unit_price":2}]',
                '[{"sku":"b","quantity":3,"unit_price":4}]'
            ]
        })
        result = parse_order_items_json(df)
        # order_id should be int32, others float64, object
        assert result["order_id"].dtype == "int32"
        assert result["sku"].dtype == "object"
        assert result["quantity"].dtype == "float64"
        assert result["unit_price"].dtype == "float64"
        assert result["item_total"].dtype == "float64"

    def test_no_mutation(self):
        original = pd.DataFrame({
            "order_id": [1],
            "items_json": ['[{"sku":"x","quantity":2,"unit_price":3}]']
        })
        copy = original.copy()
        _ = parse_order_items_json(original)
        pd.testing.assert_frame_equal(original, copy)

    def test_ordering(self):
        # Verify that multiple items from same order appear in order and order rows are sorted by original row index
        df = pd.DataFrame({
            "order_id": [200, 100],
            "items_json": [
                '[{"sku":"b"},{"sku":"a"}]',  # order 200 items order: b, a
                '[{"sku":"z"}]'               # order 100 single item
            ]
        })
        result = parse_order_items_json(df)
        # Expected order: first row from order 200 (since it appears first in df) then second row from order 200, then order 100
        expected = pd.DataFrame({
            "order_id": [200, 200, 100],
            "sku": ["b", "a", "z"],
            "quantity": [0.0, 0.0, 0.0],
            "unit_price": [0.0, 0.0, 0.0],
            "item_total": [0.0, 0.0, 0.0],
        })
        pd.testing.assert_frame_equal(result, expected)
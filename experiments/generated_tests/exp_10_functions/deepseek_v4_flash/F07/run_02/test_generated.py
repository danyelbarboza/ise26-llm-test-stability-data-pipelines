import pytest
import pandas as pd
from ise26.targets import parse_order_items_json


def test_valid_json_with_multiple_items():
    """Basic case: a single order with two valid items."""
    df = pd.DataFrame({
        "order_id": [1001],
        "items_json": [
            '[{"sku": "A1", "quantity": 2, "unit_price": 10.5},'
            ' {"sku": "B2", "quantity": 1, "unit_price": 25.0}]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1001, 1001],
        "sku": ["A1", "B2"],
        "quantity": [2, 1],
        "unit_price": [10.5, 25.0],
        "item_total": [21.0, 25.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_valid_json_single_item():
    """A single item in the JSON list."""
    df = pd.DataFrame({
        "order_id": [42],
        "items_json": ['[{"sku": "X", "quantity": 5, "unit_price": 3.0}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [42],
        "sku": ["X"],
        "quantity": [5],
        "unit_price": [3.0],
        "item_total": [15.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_missing_json_column_raises_key_error():
    """If json_col doesn't exist, the function should raise KeyError."""
    df = pd.DataFrame({"order_id": [1]})
    with pytest.raises(KeyError):
        parse_order_items_json(df, json_col="items_json")


def test_invalid_json_returns_empty_dataframe():
    """Row with invalid JSON string should be skipped."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ["not a valid json"]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"])
    pd.testing.assert_frame_equal(result, expected)


def test_empty_json_array_returns_empty():
    """Empty array [] should produce no items."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ["[]"]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"])
    pd.testing.assert_frame_equal(result, expected)


def test_null_json_returns_empty():
    """Null / missing JSON value (NaN) should be skipped."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": [None]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"])
    pd.testing.assert_frame_equal(result, expected)


def test_missing_keys_in_item_use_defaults():
    """Item without quantity or unit_price should default to zero."""
    df = pd.DataFrame({
        "order_id": [10],
        "items_json": ['[{"sku": "Z"}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [10],
        "sku": ["Z"],
        "quantity": [0],
        "unit_price": [0.0],
        "item_total": [0.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_non_numeric_quantity_and_price_coerced_to_zero():
    """Quantity or unit_price that are strings/objects become 0."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "A", "quantity": "abc", "unit_price": "xyz"}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["A"],
        "quantity": [0],
        "unit_price": [0.0],
        "item_total": [0.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_order_id_column():
    """Use a different column name for order identifier."""
    df = pd.DataFrame({
        "my_order_col": [55],
        "items_json": ['[{"sku": "K", "quantity": 3, "unit_price": 4.0}]']
    })
    result = parse_order_items_json(df, order_id_col="my_order_col")
    expected = pd.DataFrame({
        "my_order_col": [55],
        "sku": ["K"],
        "quantity": [3],
        "unit_price": [4.0],
        "item_total": [12.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_multiple_orders_with_mixed_validity():
    """Some orders valid, some invalid, one mixed."""
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "items_json": [
            '[{"sku": "A", "quantity": 1, "unit_price": 10.0}]',
            "invalid",
            '[]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["A"],
        "quantity": [1],
        "unit_price": [10.0],
        "item_total": [10.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_duplicates_and_order_preservation():
    """Items appear in the same order as JSON, duplicates are fine."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "A", "quantity": 1, "unit_price": 2.0},'
                       ' {"sku": "A", "quantity": 3, "unit_price": 4.0}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1, 1],
        "sku": ["A", "A"],
        "quantity": [1, 3],
        "unit_price": [2.0, 4.0],
        "item_total": [2.0, 12.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    """No rows at all."""
    df = pd.DataFrame(columns=["order_id", "items_json"])
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"])
    pd.testing.assert_frame_equal(result, expected)


def test_sku_missing_becomes_none():
    """Missing sku becomes None (or nan)."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"quantity": 2, "unit_price": 5.0}]']
    })
    result = parse_order_items_json(df)
    # sku column should contain None
    assert result["sku"].iloc[0] is None


def test_item_total_calculation():
    """Verify item_total = quantity * unit_price with floats."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "X", "quantity": 2.5, "unit_price": 4.0}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["X"],
        "quantity": [2.5],
        "unit_price": [4.0],
        "item_total": [10.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_original_dataframe_not_modified():
    """The function should not modify the original DataFrame."""
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "A", "quantity": 1, "unit_price": 1.0}]']
    })
    original_copy = df.copy()
    _ = parse_order_items_json(df)
    pd.testing.assert_frame_equal(df, original_copy)
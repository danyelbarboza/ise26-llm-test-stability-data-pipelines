import pytest
import pandas as pd
import numpy as np
from ise26.targets import parse_order_items_json


def test_valid_single_order_single_item():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "A1", "quantity": 2, "unit_price": 10.5}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["A1"],
        "quantity": [2.0],
        "unit_price": [10.5],
        "item_total": [21.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_valid_single_order_multiple_items():
    df = pd.DataFrame({
        "order_id": [10],
        "items_json": ['[{"sku": "X", "quantity": 1, "unit_price": 5.0}, {"sku": "Y", "quantity": 3, "unit_price": 2.0}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [10, 10],
        "sku": ["X", "Y"],
        "quantity": [1.0, 3.0],
        "unit_price": [5.0, 2.0],
        "item_total": [5.0, 6.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_multiple_orders():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "items_json": [
            '[{"sku": "A", "quantity": 1, "unit_price": 100.0}]',
            '[{"sku": "B", "quantity": 2, "unit_price": 50.0}]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1, 2],
        "sku": ["A", "B"],
        "quantity": [1.0, 2.0],
        "unit_price": [100.0, 50.0],
        "item_total": [100.0, 100.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_json_array():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"], dtype=object)
    # Ensure same order_id_col dtype
    expected["order_id"] = expected["order_id"].astype(int)
    pd.testing.assert_frame_equal(result, expected)


def test_missing_json_column_value_nan():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": [np.nan]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"], dtype=object)
    expected["order_id"] = expected["order_id"].astype(int)
    pd.testing.assert_frame_equal(result, expected)


def test_missing_json_column_value_none():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": [None]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"], dtype=object)
    expected["order_id"] = expected["order_id"].astype(int)
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_json_string():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ["not a json"]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"], dtype=object)
    expected["order_id"] = expected["order_id"].astype(int)
    pd.testing.assert_frame_equal(result, expected)


def test_missing_fields_in_item():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "Z"}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["Z"],
        "quantity": [0.0],
        "unit_price": [0.0],
        "item_total": [0.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_non_numeric_quantity_and_unit_price():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "Q", "quantity": "two", "unit_price": "free"}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["Q"],
        "quantity": [0.0],
        "unit_price": [0.0],
        "item_total": [0.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_valid_invalid_rows():
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "items_json": [
            '[{"sku": "A", "quantity": 2, "unit_price": 3.0}]',
            'invalid',
            '[{"sku": "B", "quantity": 5, "unit_price": 1.5}]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1, 3],
        "sku": ["A", "B"],
        "quantity": [2.0, 5.0],
        "unit_price": [3.0, 1.5],
        "item_total": [6.0, 7.5]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_column_names():
    df = pd.DataFrame({
        "ord_id": [100],
        "payload": ['[{"sku": "C", "quantity": 4, "unit_price": 2.0}]']
    })
    result = parse_order_items_json(df, json_col="payload", order_id_col="ord_id")
    expected = pd.DataFrame({
        "ord_id": [100],
        "sku": ["C"],
        "quantity": [4.0],
        "unit_price": [2.0],
        "item_total": [8.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    df = pd.DataFrame({"order_id": pd.Series(dtype=int), "items_json": pd.Series(dtype=str)})
    result = parse_order_items_json(df)
    expected = pd.DataFrame(columns=["order_id", "sku", "quantity", "unit_price", "item_total"], dtype=object)
    expected["order_id"] = expected["order_id"].astype(int)
    pd.testing.assert_frame_equal(result, expected)


def test_duplicate_order_ids():
    df = pd.DataFrame({
        "order_id": [1, 1],
        "items_json": [
            '[{"sku": "A", "quantity": 1, "unit_price": 10.0}]',
            '[{"sku": "B", "quantity": 2, "unit_price": 5.0}]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1, 1],
        "sku": ["A", "B"],
        "quantity": [1.0, 2.0],
        "unit_price": [10.0, 5.0],
        "item_total": [10.0, 10.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_output_order_preserved():
    # Ensure items are sorted by source order and item order
    df = pd.DataFrame({
        "order_id": [2, 1],
        "items_json": [
            '[{"sku": "B1", "quantity": 1, "unit_price": 1.0}]',
            '[{"sku": "A1", "quantity": 1, "unit_price": 1.0}, {"sku": "A2", "quantity": 2, "unit_price": 2.0}]'
        ]
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [2, 1, 1],
        "sku": ["B1", "A1", "A2"],
        "quantity": [1.0, 1.0, 2.0],
        "unit_price": [1.0, 1.0, 2.0],
        "item_total": [1.0, 1.0, 4.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_input_not_mutated():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "A", "quantity": 1, "unit_price": 1.0}]']
    })
    df_copy = df.copy()
    _ = parse_order_items_json(df)
    pd.testing.assert_frame_equal(df, df_copy)


def test_data_types_of_output():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "S", "quantity": 2, "unit_price": 3.5}]']
    })
    result = parse_order_items_json(df)
    assert result["order_id"].dtype == np.dtype('int64')
    assert result["sku"].dtype == np.dtype('object')
    assert result["quantity"].dtype == np.dtype('float64')
    assert result["unit_price"].dtype == np.dtype('float64')
    assert result["item_total"].dtype == np.dtype('float64')


def test_quantity_unit_price_string_numeric():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": "N", "quantity": "3", "unit_price": "4.5"}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": ["N"],
        "quantity": [3.0],
        "unit_price": [4.5],
        "item_total": [13.5]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_sku_as_none():
    df = pd.DataFrame({
        "order_id": [1],
        "items_json": ['[{"sku": null, "quantity": 1, "unit_price": 2.0}]']
    })
    result = parse_order_items_json(df)
    expected = pd.DataFrame({
        "order_id": [1],
        "sku": [None],
        "quantity": [1.0],
        "unit_price": [2.0],
        "item_total": [2.0]
    })
    pd.testing.assert_frame_equal(result, expected)
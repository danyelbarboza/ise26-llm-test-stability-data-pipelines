"""Buggy variant for F07 that emits a row for malformed JSON payloads."""

from __future__ import annotations

import json

import pandas as pd

from .. import correct as _correct
from ..correct import *  # noqa: F401,F403


def parse_order_items_json(
    df: pd.DataFrame,
    json_col: str = "items_json",
    order_id_col: str = "order_id",
) -> pd.DataFrame:
    """Return a buggy explosion result that keeps invalid payload rows."""

    # BUG: Malformed or empty JSON payloads produce placeholder rows instead of being skipped.
    result = df.copy(deep=True)
    output_rows: list[dict[str, object]] = []

    for source_order, (_, row) in enumerate(result.iterrows()):
        raw_value = row[json_col]
        parsed_items: list[dict[str, object]] = []

        if not pd.isna(raw_value):
            text = str(raw_value).strip()
            if text != "":
                try:
                    parsed_value = json.loads(text)
                except (TypeError, ValueError, json.JSONDecodeError):
                    parsed_value = None
                if isinstance(parsed_value, dict):
                    parsed_value = [parsed_value]
                if isinstance(parsed_value, list):
                    parsed_items = [item for item in parsed_value if isinstance(item, dict)]

        if not parsed_items:
            output_rows.append(
                {
                    order_id_col: row[order_id_col],
                    "sku": pd.NA,
                    "quantity": 0.0,
                    "unit_price": 0.0,
                    "item_total": 0.0,
                    "_source_order": source_order,
                    "_item_order": 0,
                }
            )
            continue

        for item_order, item in enumerate(parsed_items):
            quantity = _correct._coerce_numeric_or_zero(item.get("quantity"))
            unit_price = _correct._coerce_numeric_or_zero(item.get("unit_price"))
            output_rows.append(
                {
                    order_id_col: row[order_id_col],
                    "sku": _correct._normalize_optional_text(item.get("sku")),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "item_total": quantity * unit_price,
                    "_source_order": source_order,
                    "_item_order": item_order,
                }
            )

    output = pd.DataFrame.from_records(output_rows)
    output = output.sort_values(by=["_source_order", "_item_order"], kind="stable")
    return output[[order_id_col, "sku", "quantity", "unit_price", "item_total"]].reset_index(drop=True)

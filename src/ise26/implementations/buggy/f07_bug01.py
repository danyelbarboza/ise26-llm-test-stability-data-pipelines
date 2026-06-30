"""Buggy variant for F07 that drops every order item after the first one."""

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
    """Return a buggy item-explosion result that keeps only the first item."""

    # BUG: Each order keeps only the first parsed item instead of exploding all items.
    result = df.copy(deep=True)
    output_rows: list[dict[str, object]] = []

    for source_order, (_, row) in enumerate(result.iterrows()):
        raw_value = row[json_col]
        if pd.isna(raw_value):
            continue

        text = str(raw_value).strip()
        if text == "":
            continue

        try:
            parsed_value = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

        if isinstance(parsed_value, dict):
            parsed_value = [parsed_value]

        if not isinstance(parsed_value, list) or not parsed_value:
            continue

        first_item = parsed_value[0]
        if not isinstance(first_item, dict):
            continue

        quantity = _correct._coerce_numeric_or_zero(first_item.get("quantity"))
        unit_price = _correct._coerce_numeric_or_zero(first_item.get("unit_price"))
        output_rows.append(
            {
                order_id_col: row[order_id_col],
                "sku": _correct._normalize_optional_text(first_item.get("sku")),
                "quantity": quantity,
                "unit_price": unit_price,
                "item_total": quantity * unit_price,
                "_source_order": source_order,
                "_item_order": 0,
            }
        )

    if not output_rows:
        return pd.DataFrame(columns=[order_id_col, "sku", "quantity", "unit_price", "item_total"])

    output = pd.DataFrame.from_records(output_rows)
    output = output.sort_values(by=["_source_order", "_item_order"], kind="stable")
    return output[[order_id_col, "sku", "quantity", "unit_price", "item_total"]].reset_index(drop=True)

"""Synthetic DataFrame factories used by the internal test suite."""

from __future__ import annotations

import pandas as pd


def customer_names_dirty_df() -> pd.DataFrame:
    """Return small synthetic names that cover normalization edge cases."""

    # This dataset mixes accents, spacing issues, uppercase text, and missing values.
    return pd.DataFrame(
        {
            "customer_name": [
                "  Jos\u00e9  da  Silva ",
                "  ANA  ",
                "MARIA",
                None,
                "",
                "Luiz   Otavio",
            ]
        }
    )


def events_with_duplicates_df() -> pd.DataFrame:
    """Return synthetic events covering recency, ties, invalid timestamps, and null IDs."""

    # The payload column makes it easy to see which row survives deduplication.
    return pd.DataFrame(
        {
            "event_id": [1, 1, 2, 2, 2, None],
            "updated_at": [
                "2024-01-01",
                "2024-02-01",
                "invalid",
                "2024-03-10",
                "2024-03-10",
                "2024-05-01",
            ],
            "payload": [
                "old",
                "new",
                "older_invalid",
                "tie_first",
                "tie_last",
                "missing_id",
            ],
            "source_label": [
                "row_01",
                "row_02",
                "row_03",
                "row_04",
                "row_05",
                "row_06",
            ],
        }
    )


def orders_for_monthly_revenue_df() -> pd.DataFrame:
    """Return synthetic orders for monthly revenue aggregation scenarios."""

    # This dataset covers multiple months, canceled labels, invalid amounts, and invalid dates.
    return pd.DataFrame(
        {
            "order_date": [
                "2024-01-10",
                "2024-01-11",
                "2024-01-20",
                "2024-02-01",
                "2024-02-05",
                "invalid",
                "2024-03-01",
            ],
            "amount": [100, None, 50, "invalid", 40, 999, 30],
            "status": [
                "paid",
                " paid ",
                " Cancelado ",
                "paid",
                " canceled ",
                "paid",
                " PAID ",
            ],
        }
    )


def customers_for_join_df() -> pd.DataFrame:
    """Return synthetic customers for full outer join scenarios."""

    # This dataset covers matched, unmatched, and null-key customer rows.
    return pd.DataFrame(
        {
            "customer_id": [1, 2, None],
            "customer_name": ["Alice", "Bob", "Missing Customer Id"],
        }
    )


def orders_for_join_df() -> pd.DataFrame:
    """Return synthetic orders for full outer join scenarios."""

    # This dataset covers matched, unmatched, and null-key order rows.
    return pd.DataFrame(
        {
            "customer_id": [1, 3, None],
            "order_id": [10, 11, 12],
        }
    )


def expected_schema_definition() -> dict[str, str]:
    """Return the shared schema definition used by validation tests."""

    return {
        "customer_id": "int",
        "amount": "number",
        "order_date": "datetime",
        "status": "string",
    }


def valid_schema_df() -> pd.DataFrame:
    """Return a synthetic DataFrame that satisfies the expected schema."""

    # The values are intentionally small and typed to match the logical schema labels.
    return pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([10.5, 12.0], dtype="float64"),
            "order_date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "status": pd.Series(["paid", "pending"], dtype="string"),
        }
    )


def missing_column_schema_df() -> pd.DataFrame:
    """Return a synthetic DataFrame that omits a required schema column."""

    # The missing order_date column supports internal missing-column assertions.
    return pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([10, 20], dtype="int64"),
            "status": pd.Series(["paid", "pending"], dtype="string"),
        }
    )


def wrong_type_schema_df() -> pd.DataFrame:
    """Return a synthetic DataFrame with a logical type mismatch."""

    # customer_id is stored as string here to trigger an int-type mismatch.
    return pd.DataFrame(
        {
            "customer_id": pd.Series(["1", "2"], dtype="string"),
            "amount": pd.Series([10, 20], dtype="int64"),
            "order_date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "status": pd.Series(["paid", "pending"], dtype="string"),
        }
    )


def extra_column_schema_df() -> pd.DataFrame:
    """Return a valid synthetic DataFrame that also contains an extra column."""

    # Extra columns are allowed and should not invalidate the schema result.
    return pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([10.5, 12.0], dtype="float64"),
            "order_date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "status": pd.Series(["paid", "pending"], dtype="string"),
            "extra_column": ["x", "y"],
        }
    )


def payments_for_status_classification_df() -> pd.DataFrame:
    """Return synthetic payment rows covering all official status branches."""

    # The rows cover on-time, late, pending, overdue, and invalid classifications.
    return pd.DataFrame(
        {
            "due_date": [
                "2024-01-10",
                "2024-01-10",
                "2024-01-20",
                "2024-01-05",
                "2024-01-15",
                "2024-01-15",
                "invalid",
                "2024-01-25",
                "2024-01-30",
            ],
            "paid_date": [
                "2024-01-10",
                "2024-01-12",
                None,
                None,
                None,
                None,
                None,
                "not-a-date",
                None,
            ],
            "amount": [100, 100, 100, 100, 0, -5, 100, 100, 100],
        }
    )


def payment_reference_date() -> str:
    """Return the shared synthetic reference date used by payment tests."""

    return "2024-01-15"


def order_items_json_df() -> pd.DataFrame:
    """Return synthetic order items for JSON explosion scenarios."""

    # The payloads cover multiple items, invalid JSON, empty lists, and null values.
    return pd.DataFrame(
        {
            "order_id": [101, 102, 103, 104, 105, 106],
            "items_json": [
                '[{"sku": "SKU-1", "quantity": 2, "unit_price": 10.5}, {"sku": "SKU-2", "quantity": "3", "unit_price": "4.00"}]',
                '[{"sku": "SKU-3", "quantity": 1, "unit_price": 7.25}]',
                "invalid",
                "[]",
                None,
                '[{"sku": "SKU-4", "quantity": "bad", "unit_price": 8}]',
            ],
        }
    )


def conversion_events_df() -> pd.DataFrame:
    """Return synthetic conversion events for channel aggregation scenarios."""

    # The data mixes valid counts, strings, zero visits, and missing values.
    return pd.DataFrame(
        {
            "channel": ["search", "search", "social", "social", "email", "email"],
            "visits": [100, "20", 0, "invalid", None, 50],
            "conversions": [10, 5, 0, 2, 4, None],
        }
    )


def outlier_amounts_df() -> pd.DataFrame:
    """Return synthetic amounts for IQR-based outlier capping tests."""

    # A single large value makes it easy to assert that capping occurred.
    return pd.DataFrame(
        {
            "amount": [10, 11, 12, 13, 14, 15, 1000, None, "invalid"],
        }
    )


def currency_values_df() -> pd.DataFrame:
    """Return synthetic currency strings for normalization tests."""

    # The values cover Brazilian and English separators, blanks, invalid text, and a negative value.
    return pd.DataFrame(
        {
            "amount_raw": [
                "R$ 1.234,56",
                "1.234,56",
                "1234.56",
                "1,234.56",
                "",
                None,
                "abc",
                "R$ -10,00",
            ],
        }
    )

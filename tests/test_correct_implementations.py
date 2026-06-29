"""Manual tests for the correct ISE26 transformation implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd
import pandas.testing as pdt
import pytest

from ise26.implementations.correct import (
    calculate_monthly_revenue,
    classify_payment_status,
    clean_customer_names,
    deduplicate_events,
    join_customers_orders,
    validate_schema,
)


def test_clean_customer_names_standardizes_values_without_mutating_input() -> None:
    """Verify name normalization, null handling, and input immutability."""

    source = pd.DataFrame({"customer_name": ["  João  SILVA ", " Ana   Maria ", None, "   "]})
    original = source.copy(deep=True)

    result = clean_customer_names(source)

    assert "customer_name_clean" in result.columns
    assert result["customer_name_clean"].tolist()[0] == "joao silva"
    assert result["customer_name_clean"].tolist()[1] == "ana maria"
    assert pd.isna(result["customer_name_clean"].tolist()[2])
    assert pd.isna(result["customer_name_clean"].tolist()[3])
    pdt.assert_frame_equal(source, original)


def test_clean_customer_names_supports_custom_column_names() -> None:
    """Verify custom input and output column names for name normalization."""

    source = pd.DataFrame({"raw_name": ["  MÁRIA  de souza  "]})

    result = clean_customer_names(source, name_col="raw_name", output_col="normalized_name")

    assert result["normalized_name"].tolist() == ["maria de souza"]
    assert "customer_name_clean" not in result.columns


def test_deduplicate_events_keeps_most_recent_and_preserves_null_ids() -> None:
    """Verify recency rules, null identifier preservation, and immutability."""

    source = pd.DataFrame(
        {
            "event_id": [1, 1, 2, 2, None],
            "updated_at": ["2024-01-01", "2024-02-01", "invalid", "2024-03-10", "2024-05-01"],
            "payload": ["old", "new", "older_invalid", "newer_valid", "missing_id"],
        }
    )
    original = source.copy(deep=True)

    result = deduplicate_events(source)

    # The expected frame is ordered to reflect the original-row ordering rule
    # after duplicate resolution, including preservation of the null identifier.
    expected = pd.DataFrame(
        {
            "event_id": [1.0, 2.0, None],
            "updated_at": ["2024-02-01", "2024-03-10", "2024-05-01"],
            "payload": ["new", "newer_valid", "missing_id"],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)
    pdt.assert_frame_equal(source, original)


def test_deduplicate_events_keeps_last_original_row_when_timestamps_tie() -> None:
    """Verify the original-order tie-break rule for equal timestamps."""

    source = pd.DataFrame(
        {
            "event_id": [7, 7, 7],
            "updated_at": ["2024-01-10", "2024-01-10", "2024-01-10"],
            "payload": ["first", "second", "third"],
        }
    )

    result = deduplicate_events(source)

    assert result["payload"].tolist() == ["third"]


def test_calculate_monthly_revenue_ignores_canceled_orders_and_invalid_dates() -> None:
    """Verify monthly aggregation, canceled filtering, and amount coercion."""

    source = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "2024-01-11", "2024-01-20", "invalid", "2024-02-01"],
            "amount": [100, None, 20, 999, "invalid"],
            "status": ["paid", " paid ", " Cancelado ", "paid", "paid"],
        }
    )

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": ["2024-01", "2024-02"],
            "revenue": [100.0, 0.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_monthly_revenue_sorts_months_and_normalizes_cancel_statuses() -> None:
    """Verify month ordering and canceled-status normalization across languages."""

    source = pd.DataFrame(
        {
            "order_date": ["2024-02-10", "2024-01-15", "2024-02-11", "2024-01-20"],
            "amount": [50, 10, 999, 999],
            "status": ["paid", " paid ", " canceled ", " CANCELADO "],
        }
    )

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": ["2024-01", "2024-02"],
            "revenue": [10, 50],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_join_customers_orders_performs_full_outer_join_with_status_labels() -> None:
    """Verify full outer join semantics, status labels, and immutability."""

    customers = pd.DataFrame({"customer_id": [1, 2], "customer_name": ["Alice", "Bob"]})
    orders = pd.DataFrame({"customer_id": [1, 3], "order_id": [10, 11]})
    customers_original = customers.copy(deep=True)
    orders_original = orders.copy(deep=True)

    result = join_customers_orders(customers, orders)

    assert len(result) == 3
    assert result["record_status"].tolist() == [
        "matched",
        "customer_without_order",
        "order_without_customer",
    ]
    assert result.loc[result["customer_id"] == 2, "record_status"].iloc[0] == "customer_without_order"
    assert result.loc[result["customer_id"] == 3, "record_status"].iloc[0] == "order_without_customer"
    pdt.assert_frame_equal(customers, customers_original)
    pdt.assert_frame_equal(orders, orders_original)


def test_join_customers_orders_handles_null_keys_without_false_matches() -> None:
    """Verify that null keys remain unmatched on both sides."""

    customers = pd.DataFrame(
        {
            "customer_id": [1, None],
            "customer_name": ["Alice", "Missing Customer Id"],
        }
    )
    orders = pd.DataFrame(
        {
            "customer_id": [1, None],
            "order_id": [10, 11],
        }
    )

    result = join_customers_orders(customers, orders)

    assert result["record_status"].tolist() == [
        "matched",
        "customer_without_order",
        "order_without_customer",
    ]
    assert result.loc[result["order_id"] == 11, "record_status"].iloc[0] == "order_without_customer"
    assert result.loc[result["customer_name"] == "Missing Customer Id", "record_status"].iloc[0] == "customer_without_order"


def test_validate_schema_accepts_extra_columns_and_reports_missing_or_wrong_types() -> None:
    """Verify valid schemas, missing columns, and logical type mismatches."""

    valid_df = pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([10.5, 12.0], dtype="float64"),
            "order_date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "status": pd.Series(["paid", "pending"], dtype="string"),
            "extra_column": ["x", "y"],
        }
    )
    invalid_df = pd.DataFrame(
        {
            "customer_id": ["1", "2"],
            "amount": [10, 20],
            "status": ["paid", "pending"],
        }
    )
    schema = {
        "customer_id": "int",
        "amount": "number",
        "order_date": "datetime",
        "status": "string",
    }

    valid_result = validate_schema(valid_df, schema)
    invalid_result = validate_schema(invalid_df, schema)

    assert valid_result == {"valid": True, "missing_columns": [], "type_errors": []}
    # The invalid case checks both dimensions of the validator at once:
    # missing required columns and logical type mismatches for existing ones.
    assert invalid_result["valid"] is False
    assert invalid_result["missing_columns"] == ["order_date"]
    assert invalid_result["type_errors"] == [
        {"column": "customer_id", "expected_type": "int", "actual_type": "string"}
    ]


def test_validate_schema_normalizes_expected_types_and_rejects_unsupported_types() -> None:
    """Verify expected-type normalization and unsupported-type failures."""

    source = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "amount": [10, 20],
            "active": [True, False],
        }
    )

    normalized_result = validate_schema(
        source,
        {
            "customer_id": " Int ",
            "amount": " Number ",
            "active": " bool ",
        },
    )

    assert normalized_result == {"valid": True, "missing_columns": [], "type_errors": []}

    with pytest.raises(ValueError, match="Unsupported schema type"):
        validate_schema(source, {"customer_id": "integer"})


def test_classify_payment_status_assigns_all_expected_statuses() -> None:
    """Verify every payment-status branch and preserve input immutability."""

    source = pd.DataFrame(
        {
            "due_date": ["2024-01-10", "2024-01-10", "2024-01-10", "2024-01-20", None, "invalid"],
            "paid_date": ["2024-01-10", "2024-01-12", None, None, None, None],
            "amount": [100, 100, 100, 100, 100, 100],
        }
    )
    original = source.copy(deep=True)

    result = classify_payment_status(source, reference_date="2024-01-15")

    assert result["payment_status"].tolist() == [
        "paid_on_time",
        "paid_late",
        "overdue",
        "pending",
        "invalid",
        "invalid",
    ]
    pdt.assert_frame_equal(source, original)


def test_classify_payment_status_marks_invalid_paid_dates_and_invalid_reference_date() -> None:
    """Verify invalid paid_date handling and reference-date validation."""

    source = pd.DataFrame(
        {
            "due_date": ["2024-01-10", "2024-01-20", "2024-01-25"],
            "paid_date": ["not-a-date", "", None],
            "amount": [100, 100, 100],
        }
    )

    result = classify_payment_status(source, reference_date="2024-01-15")

    assert result["payment_status"].tolist() == [
        "invalid",
        "pending",
        "pending",
    ]

    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(source, reference_date="invalid-reference-date")


@pytest.mark.parametrize(
    ("function_name", "runner"),
    [
        (
            "clean_customer_names",
            lambda: clean_customer_names(
                pd.DataFrame({"customer_name": [" Alice ", None]}),
            ),
        ),
        (
            "deduplicate_events",
            lambda: deduplicate_events(
                pd.DataFrame(
                    {
                        "event_id": [1, 1, None],
                        "updated_at": ["2024-01-01", "2024-02-01", "2024-03-01"],
                    }
                )
            ),
        ),
        (
            "calculate_monthly_revenue",
            lambda: calculate_monthly_revenue(
                pd.DataFrame(
                    {
                        "order_date": ["2024-01-01", "invalid"],
                        "amount": [10, 999],
                        "status": ["paid", "cancelled"],
                    }
                )
            ),
        ),
        (
            "join_customers_orders",
            lambda: join_customers_orders(
                pd.DataFrame({"customer_id": [1, None], "customer_name": ["Alice", "No Id"]}),
                pd.DataFrame({"customer_id": [1, None], "order_id": [10, 11]}),
            ),
        ),
        (
            "validate_schema",
            lambda: validate_schema(
                pd.DataFrame({"customer_id": [1], "amount": [10]}),
                {"customer_id": "int", "amount": "number"},
            ),
        ),
        (
            "classify_payment_status",
            lambda: classify_payment_status(
                pd.DataFrame(
                    {
                        "due_date": ["2024-01-10", "2024-01-12"],
                        "paid_date": [None, "2024-01-11"],
                        "amount": [100, 100],
                    }
                ),
                reference_date="2024-01-11",
            ),
        ),
    ],
    ids=[
        "clean_customer_names",
        "deduplicate_events",
        "calculate_monthly_revenue",
        "join_customers_orders",
        "validate_schema",
        "classify_payment_status",
    ],
)
def test_correct_functions_do_not_mutate_original_dataframes(
    function_name: str,
    runner: Callable[[], Any],
) -> None:
    """Verify that each official function preserves the input DataFrame objects."""

    # The function-specific inputs are created inside the runner so each case
    # stays small and focused while still checking that the implementation does
    # not mutate its original DataFrame arguments.
    if function_name == "clean_customer_names":
        source = pd.DataFrame({"customer_name": [" Alice ", None]})
        original = source.copy(deep=True)
        clean_customer_names(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "deduplicate_events":
        source = pd.DataFrame(
            {
                "event_id": [1, 1, None],
                "updated_at": ["2024-01-01", "2024-02-01", "2024-03-01"],
            }
        )
        original = source.copy(deep=True)
        deduplicate_events(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "calculate_monthly_revenue":
        source = pd.DataFrame(
            {
                "order_date": ["2024-01-01", "invalid"],
                "amount": [10, 999],
                "status": ["paid", "cancelled"],
            }
        )
        original = source.copy(deep=True)
        calculate_monthly_revenue(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "join_customers_orders":
        customers = pd.DataFrame({"customer_id": [1, None], "customer_name": ["Alice", "No Id"]})
        orders = pd.DataFrame({"customer_id": [1, None], "order_id": [10, 11]})
        customers_original = customers.copy(deep=True)
        orders_original = orders.copy(deep=True)
        join_customers_orders(customers, orders)
        pdt.assert_frame_equal(customers, customers_original)
        pdt.assert_frame_equal(orders, orders_original)
        return

    if function_name == "validate_schema":
        source = pd.DataFrame({"customer_id": [1], "amount": [10]})
        original = source.copy(deep=True)
        validate_schema(source, {"customer_id": "int", "amount": "number"})
        pdt.assert_frame_equal(source, original)
        return

    source = pd.DataFrame(
        {
            "due_date": ["2024-01-10", "2024-01-12"],
            "paid_date": [None, "2024-01-11"],
            "amount": [100, 100],
        }
    )
    original = source.copy(deep=True)
    classify_payment_status(source, reference_date="2024-01-11")
    pdt.assert_frame_equal(source, original)

"""Manual tests for the correct ISE26 transformation implementations."""

from __future__ import annotations

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
from tests.fixtures import (
    customer_names_dirty_df,
    customers_for_join_df,
    events_with_duplicates_df,
    expected_schema_definition,
    extra_column_schema_df,
    missing_column_schema_df,
    orders_for_join_df,
    orders_for_monthly_revenue_df,
    payment_reference_date,
    payments_for_status_classification_df,
    valid_schema_df,
    wrong_type_schema_df,
)


def test_clean_customer_names_standardizes_values_without_mutating_input() -> None:
    """Verify name normalization, null handling, and input immutability."""

    source = customer_names_dirty_df()
    original = source.copy(deep=True)

    result = clean_customer_names(source)

    assert "customer_name_clean" in result.columns
    assert result["customer_name_clean"].tolist()[0] == "jose da silva"
    assert result["customer_name_clean"].tolist()[1] == "ana"
    assert result["customer_name_clean"].tolist()[2] == "maria"
    assert pd.isna(result["customer_name_clean"].tolist()[3])
    assert pd.isna(result["customer_name_clean"].tolist()[4])
    assert result["customer_name_clean"].tolist()[5] == "luiz otavio"
    pdt.assert_frame_equal(source, original)


def test_clean_customer_names_supports_custom_column_names() -> None:
    """Verify custom input and output column names for name normalization."""

    source = customer_names_dirty_df().rename(columns={"customer_name": "raw_name"})

    result = clean_customer_names(source, name_col="raw_name", output_col="normalized_name")

    assert result["normalized_name"].tolist()[0] == "jose da silva"
    assert "customer_name_clean" not in result.columns


def test_deduplicate_events_keeps_most_recent_and_preserves_null_ids() -> None:
    """Verify recency rules, null identifier preservation, and immutability."""

    source = events_with_duplicates_df()
    original = source.copy(deep=True)

    result = deduplicate_events(source)

    expected = pd.DataFrame(
        {
            "event_id": [1.0, 2.0, None],
            "updated_at": ["2024-02-01", "2024-03-10", "2024-05-01"],
            "payload": ["new", "tie_last", "missing_id"],
            "source_label": ["row_02", "row_05", "row_06"],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)
    pdt.assert_frame_equal(source, original)


def test_deduplicate_events_keeps_last_original_row_when_timestamps_tie() -> None:
    """Verify the original-order tie-break rule for equal timestamps."""

    source = events_with_duplicates_df().loc[
        lambda frame: frame["event_id"].eq(2) & frame["updated_at"].eq("2024-03-10")
    ].reset_index(drop=True)

    result = deduplicate_events(source)

    assert result["payload"].tolist() == ["tie_last"]


def test_calculate_monthly_revenue_ignores_canceled_orders_and_invalid_dates() -> None:
    """Verify monthly aggregation, canceled filtering, and amount coercion."""

    source = orders_for_monthly_revenue_df()

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": ["2024-01", "2024-02", "2024-03"],
            "revenue": [100.0, 0.0, 30.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_monthly_revenue_sorts_months_and_normalizes_cancel_statuses() -> None:
    """Verify month ordering and canceled-status normalization across languages."""

    source = orders_for_monthly_revenue_df()

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": ["2024-01", "2024-02", "2024-03"],
            "revenue": [100.0, 0.0, 30.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_join_customers_orders_performs_full_outer_join_with_status_labels() -> None:
    """Verify full outer join semantics, status labels, and immutability."""

    customers = customers_for_join_df()
    orders = orders_for_join_df()
    customers_original = customers.copy(deep=True)
    orders_original = orders.copy(deep=True)

    result = join_customers_orders(customers, orders)

    assert len(result) == 5
    assert result["record_status"].tolist() == [
        "matched",
        "customer_without_order",
        "order_without_customer",
        "customer_without_order",
        "order_without_customer",
    ]
    assert result.loc[result["customer_id"] == 2, "record_status"].iloc[0] == "customer_without_order"
    assert result.loc[result["customer_id"] == 3, "record_status"].iloc[0] == "order_without_customer"
    pdt.assert_frame_equal(customers, customers_original)
    pdt.assert_frame_equal(orders, orders_original)


def test_join_customers_orders_handles_null_keys_without_false_matches() -> None:
    """Verify that null keys remain unmatched on both sides."""

    customers = customers_for_join_df()
    orders = orders_for_join_df()

    result = join_customers_orders(customers, orders)

    assert result.loc[result["order_id"] == 12, "record_status"].iloc[0] == "order_without_customer"
    assert result.loc[result["customer_name"] == "Missing Customer Id", "record_status"].iloc[0] == "customer_without_order"
    assert result.loc[result["customer_id"].eq(1), "record_status"].iloc[0] == "matched"


def test_validate_schema_accepts_extra_columns_and_reports_missing_or_wrong_types() -> None:
    """Verify valid schemas, missing columns, and logical type mismatches."""

    schema = expected_schema_definition()

    valid_result = validate_schema(extra_column_schema_df(), schema)
    missing_result = validate_schema(missing_column_schema_df(), schema)
    wrong_type_result = validate_schema(wrong_type_schema_df(), schema)

    assert valid_result == {"valid": True, "missing_columns": [], "type_errors": []}
    assert missing_result["valid"] is False
    assert missing_result["missing_columns"] == ["order_date"]
    assert missing_result["type_errors"] == []
    assert wrong_type_result["valid"] is False
    assert wrong_type_result["missing_columns"] == []
    assert wrong_type_result["type_errors"] == [
        {"column": "customer_id", "expected_type": "int", "actual_type": "string"}
    ]


def test_validate_schema_normalizes_expected_types_and_rejects_unsupported_types() -> None:
    """Verify expected-type normalization and unsupported-type failures."""

    source = valid_schema_df().assign(active=[True, False])

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

    source = payments_for_status_classification_df()
    original = source.copy(deep=True)

    result = classify_payment_status(source, reference_date=payment_reference_date())

    assert result["payment_status"].tolist() == [
        "paid_on_time",
        "paid_late",
        "pending",
        "overdue",
        "invalid",
        "invalid",
        "invalid",
        "invalid",
        "pending",
    ]
    pdt.assert_frame_equal(source, original)


def test_classify_payment_status_marks_invalid_paid_dates_and_invalid_reference_date() -> None:
    """Verify invalid paid_date handling and reference-date validation."""

    source = payments_for_status_classification_df().iloc[[7, 2, 8]].reset_index(drop=True)

    result = classify_payment_status(source, reference_date=payment_reference_date())

    assert result["payment_status"].tolist() == [
        "invalid",
        "pending",
        "pending",
    ]

    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(source, reference_date="invalid-reference-date")


@pytest.mark.parametrize(
    "function_name",
    [
        "clean_customer_names",
        "deduplicate_events",
        "calculate_monthly_revenue",
        "join_customers_orders",
        "validate_schema",
        "classify_payment_status",
    ],
)
def test_correct_functions_do_not_mutate_original_dataframes(function_name: str) -> None:
    """Verify that each official function preserves the input DataFrame objects."""

    if function_name == "clean_customer_names":
        source = customer_names_dirty_df()
        original = source.copy(deep=True)
        clean_customer_names(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "deduplicate_events":
        source = events_with_duplicates_df()
        original = source.copy(deep=True)
        deduplicate_events(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "calculate_monthly_revenue":
        source = orders_for_monthly_revenue_df()
        original = source.copy(deep=True)
        calculate_monthly_revenue(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "join_customers_orders":
        customers = customers_for_join_df()
        orders = orders_for_join_df()
        customers_original = customers.copy(deep=True)
        orders_original = orders.copy(deep=True)
        join_customers_orders(customers, orders)
        pdt.assert_frame_equal(customers, customers_original)
        pdt.assert_frame_equal(orders, orders_original)
        return

    if function_name == "validate_schema":
        source = valid_schema_df()
        original = source.copy(deep=True)
        validate_schema(source, expected_schema_definition())
        pdt.assert_frame_equal(source, original)
        return

    source = payments_for_status_classification_df()
    original = source.copy(deep=True)
    classify_payment_status(source, reference_date=payment_reference_date())
    pdt.assert_frame_equal(source, original)

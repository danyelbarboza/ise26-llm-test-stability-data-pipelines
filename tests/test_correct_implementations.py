"""Manual tests for the correct ISE26 transformation implementations."""

from __future__ import annotations

import pandas as pd
import pandas.testing as pdt
import pytest

from ise26.implementations.correct import (
    calculate_conversion_rate,
    calculate_monthly_revenue,
    classify_payment_status,
    cap_outliers_iqr,
    clean_customer_names,
    deduplicate_events,
    join_customers_orders,
    parse_order_items_json,
    standardize_currency_values,
    validate_schema,
)
from tests.fixtures import (
    conversion_events_df,
    customer_names_dirty_df,
    customers_for_join_df,
    events_with_duplicates_df,
    expected_schema_definition,
    extra_column_schema_df,
    currency_values_df,
    missing_column_schema_df,
    orders_for_join_df,
    orders_for_monthly_revenue_df,
    order_items_json_df,
    payment_reference_date,
    payments_for_status_classification_df,
    outlier_amounts_df,
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


@pytest.mark.parametrize(
    ("function", "args", "kwargs"),
    [
        (clean_customer_names, (pd.DataFrame({"other": ["x"]}),), {"name_col": "customer_name"}),
        (join_customers_orders, (pd.DataFrame({"other": [1]}), pd.DataFrame({"customer_id": [1]})), {}),
        (parse_order_items_json, (pd.DataFrame({"order_id": [1]}),), {}),
    ],
)
def test_selected_functions_raise_clear_error_when_required_columns_are_missing(
    function: object,
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> None:
    """Verify that missing required columns produce a deterministic error."""

    with pytest.raises(ValueError, match="Missing required column"):
        function(*args, **kwargs)  # type: ignore[misc]


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
            "month": pd.Series(["2024-01", "2024-02", "2024-03"], dtype="string"),
            "revenue": pd.Series([100.0, 0.0, 30.0], dtype="float64"),
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_monthly_revenue_sorts_months_and_normalizes_cancel_statuses() -> None:
    """Verify month ordering and canceled-status normalization across languages."""

    source = orders_for_monthly_revenue_df()

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": pd.Series(["2024-01", "2024-02", "2024-03"], dtype="string"),
            "revenue": pd.Series([100.0, 0.0, 30.0], dtype="float64"),
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_monthly_revenue_returns_empty_frame_for_invalid_or_canceled_rows() -> None:
    """Verify the predictable empty-output contract for fully filtered datasets."""

    source = pd.DataFrame(
        {
            "order_date": ["invalid", "2024-01-01"],
            "amount": [10, 20],
            "status": ["paid", "cancelado"],
        }
    )

    result = calculate_monthly_revenue(source)

    expected = pd.DataFrame(
        {
            "month": pd.Series(dtype="string"),
            "revenue": pd.Series(dtype="float64"),
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
        {"column": "customer_id", "expected": "int", "actual": "string"}
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


def test_parse_order_items_json_explodes_items_and_skips_invalid_payloads() -> None:
    """Verify JSON explosion, invalid payload skipping, and item totals."""

    source = order_items_json_df()

    result = parse_order_items_json(source)

    expected = pd.DataFrame(
        {
            "order_id": [101, 101, 102, 106],
            "sku": ["SKU-1", "SKU-2", "SKU-3", "SKU-4"],
            "quantity": [2.0, 3.0, 1.0, 0.0],
            "unit_price": [10.5, 4.0, 7.25, 8.0],
            "item_total": [21.0, 12.0, 7.25, 0.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_parse_order_items_json_supports_custom_order_identifier_column() -> None:
    """Verify that the output keeps a custom order identifier column name."""

    source = order_items_json_df().rename(columns={"order_id": "purchase_id"})

    result = parse_order_items_json(source, order_id_col="purchase_id")

    assert list(result.columns) == ["purchase_id", "sku", "quantity", "unit_price", "item_total"]
    assert result["purchase_id"].tolist() == [101, 101, 102, 106]
    assert result.shape[0] == 4


def test_parse_order_items_json_requires_json_lists_and_keeps_missing_sku_as_na() -> None:
    """Verify that non-list JSON payloads are skipped and missing SKUs stay missing."""

    source = pd.DataFrame(
        {
            "order_id": [201, 202],
            "items_json": [
                '{"sku": "SKU-IGNORED"}',
                '[{"quantity": 2, "unit_price": "3.50"}]',
            ],
        }
    )

    result = parse_order_items_json(source)

    expected = pd.DataFrame(
        {
            "order_id": [202],
            "sku": [pd.NA],
            "quantity": [2.0],
            "unit_price": [3.5],
            "item_total": [7.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_conversion_rate_aggregates_channels_and_handles_invalid_values() -> None:
    """Verify grouping, numeric coercion, and zero-safe rate calculation."""

    source = conversion_events_df()

    result = calculate_conversion_rate(source)

    expected = pd.DataFrame(
        {
            "channel": ["email", "search", "social"],
            "visits": [50.0, 120.0, 0.0],
            "conversions": [4.0, 15.0, 2.0],
            "conversion_rate": [0.08, 0.125, 0.0],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_calculate_conversion_rate_returns_zero_for_zero_visit_groups() -> None:
    """Verify the zero-visit boundary case."""

    source = pd.DataFrame(
        {
            "channel": ["display", "display"],
            "visits": [0, "invalid"],
            "conversions": [5, 7],
        }
    )

    result = calculate_conversion_rate(source)

    assert result.loc[result["channel"] == "display", "conversion_rate"].iloc[0] == 0.0
    assert result.loc[result["channel"] == "display", "visits"].iloc[0] == 0.0
    assert result.loc[result["channel"] == "display", "conversions"].iloc[0] == 12.0


def test_calculate_conversion_rate_groups_missing_channels_as_unknown() -> None:
    """Verify that null channel names are grouped under an explicit label."""

    source = pd.DataFrame(
        {
            "channel": ["search", None],
            "visits": [10, 5],
            "conversions": [1, 2],
        }
    )

    result = calculate_conversion_rate(source)

    expected = pd.DataFrame(
        {
            "channel": ["search", "unknown"],
            "visits": [10.0, 5.0],
            "conversions": [1.0, 2.0],
            "conversion_rate": [0.1, 0.4],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected)


def test_cap_outliers_iqr_caps_large_values_and_preserves_input() -> None:
    """Verify IQR capping and original-column preservation."""

    source = outlier_amounts_df()
    original = source.copy(deep=True)

    result = cap_outliers_iqr(source)

    expected = source.copy(deep=True)
    expected["amount_capped"] = pd.Series(
        [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 19.0, pd.NA, pd.NA],
        dtype="Float64",
    )

    pdt.assert_frame_equal(result, expected)
    pdt.assert_frame_equal(source, original)


def test_cap_outliers_iqr_supports_custom_output_column_and_keeps_nulls_missing() -> None:
    """Verify custom output names and missing-value preservation."""

    source = outlier_amounts_df().iloc[[0, 7, 8]].reset_index(drop=True)

    result = cap_outliers_iqr(source, output_col="amount_trimmed")

    assert "amount_trimmed" in result.columns
    assert pd.isna(result.loc[1, "amount_trimmed"])
    assert pd.isna(result.loc[2, "amount_trimmed"])


def test_cap_outliers_iqr_leaves_single_numeric_value_unchanged_when_iqr_is_unavailable() -> None:
    """Verify the fallback path when there are fewer than two numeric values."""

    source = pd.DataFrame({"amount": [10, None, "invalid"]})

    result = cap_outliers_iqr(source)

    assert result.loc[0, "amount_capped"] == 10.0
    assert pd.isna(result.loc[1, "amount_capped"])
    assert pd.isna(result.loc[2, "amount_capped"])


def test_standardize_currency_values_parses_common_formats_and_preserves_input() -> None:
    """Verify currency normalization for Brazilian and English formats."""

    source = currency_values_df()
    original = source.copy(deep=True)

    result = standardize_currency_values(source)

    expected = source.copy(deep=True)
    expected["amount"] = pd.Series(
        [1234.56, 1234.56, 1234.56, 1234.56, pd.NA, pd.NA, pd.NA, -10.0],
        dtype="Float64",
    )

    pdt.assert_frame_equal(result, expected)
    pdt.assert_frame_equal(source, original)


def test_standardize_currency_values_supports_custom_output_column() -> None:
    """Verify custom output names and missing-value preservation."""

    source = currency_values_df().iloc[[4, 5, 6]].reset_index(drop=True)

    result = standardize_currency_values(source, output_col="amount_value")

    assert list(result.columns) == ["amount_raw", "amount_value"]
    assert result["amount_value"].isna().all()


@pytest.mark.parametrize(
    "function_name",
    [
        "clean_customer_names",
        "deduplicate_events",
        "calculate_monthly_revenue",
        "join_customers_orders",
        "validate_schema",
        "classify_payment_status",
        "parse_order_items_json",
        "calculate_conversion_rate",
        "cap_outliers_iqr",
        "standardize_currency_values",
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

    if function_name == "classify_payment_status":
        source = payments_for_status_classification_df()
        original = source.copy(deep=True)
        classify_payment_status(source, reference_date=payment_reference_date())
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "parse_order_items_json":
        source = order_items_json_df()
        original = source.copy(deep=True)
        parse_order_items_json(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "calculate_conversion_rate":
        source = conversion_events_df()
        original = source.copy(deep=True)
        calculate_conversion_rate(source)
        pdt.assert_frame_equal(source, original)
        return

    if function_name == "cap_outliers_iqr":
        source = outlier_amounts_df()
        original = source.copy(deep=True)
        cap_outliers_iqr(source)
        pdt.assert_frame_equal(source, original)
        return

    source = currency_values_df()
    original = source.copy(deep=True)
    standardize_currency_values(source)
    pdt.assert_frame_equal(source, original)

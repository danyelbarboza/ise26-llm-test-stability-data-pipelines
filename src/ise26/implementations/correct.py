"""Correct data-transformation implementations used in the ISE26 experiment."""

from __future__ import annotations

import unicodedata
from typing import Any

import pandas as pd


def _clone_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a deep copy of the received DataFrame.

    The experiment requires transformation functions to avoid mutating the
    original input data. This helper centralizes the copying behavior and keeps
    the intent explicit at each public function entrypoint.

    Args:
        df: Input DataFrame that must remain unchanged.

    Returns:
        A deep copy of the input DataFrame.
    """

    return df.copy(deep=True)


def _remove_accents(value: str) -> str:
    """Remove accents and diacritics from a string value.

    The function relies on Unicode normalization and strips combining marks so
    that names such as ``"João"`` become ``"joao"`` after normalization.

    Args:
        value: Text value to normalize.

    Returns:
        The same text without accent marks.
    """

    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_optional_string(value: Any) -> Any:
    """Normalize a nullable textual value for transformation workflows.

    Null-like values are preserved as ``pd.NA``. Non-null values are converted
    to strings, stripped, internal whitespace is collapsed, lowercased, and
    accent marks are removed. Empty strings after normalization are also mapped
    to ``pd.NA``.

    Args:
        value: Original scalar value from a DataFrame column.

    Returns:
        A normalized string or ``pd.NA`` when the value should be treated as
        missing.
    """

    if pd.isna(value):
        return pd.NA

    text = str(value)
    compact_text = " ".join(text.split()).strip().lower()

    if compact_text == "":
        return pd.NA

    return _remove_accents(compact_text)


def _normalize_status_text(value: Any) -> str:
    """Convert a scalar status value into a comparable normalized string.

    The output is intentionally non-null and optimized for membership checks in
    rule-based filtering logic, such as recognizing canceled order statuses.

    Args:
        value: Original scalar status value.

    Returns:
        A stripped lowercase string. Null-like values become an empty string.
    """

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def _infer_series_type(series: pd.Series) -> str:
    """Infer a logical type label for a pandas Series.

    The function maps pandas dtypes and mixed object content into the logical
    type labels supported by the experiment schema validator.

    Args:
        series: Series whose non-null content should be classified.

    Returns:
        One of the logical labels used by the validator, or a generic fallback
        label such as ``"mixed"`` or ``"empty"``.
    """

    non_null = series.dropna()

    if non_null.empty:
        return "empty"

    if pd.api.types.is_bool_dtype(non_null):
        return "bool"

    if pd.api.types.is_datetime64_any_dtype(non_null):
        return "datetime"

    if pd.api.types.is_string_dtype(non_null):
        return "string"

    if pd.api.types.is_integer_dtype(non_null):
        return "int"

    if pd.api.types.is_float_dtype(non_null):
        return "float"

    if pd.api.types.is_numeric_dtype(non_null):
        return "number"

    inferred = pd.api.types.infer_dtype(non_null, skipna=True)
    mapping = {
        "boolean": "bool",
        "datetime": "datetime",
        "datetime64": "datetime",
        "date": "datetime",
        "floating": "float",
        "integer": "int",
        "mixed-integer": "int",
        "mixed-integer-float": "number",
        "decimal": "number",
        "string": "string",
        "unicode": "string",
    }

    return mapping.get(inferred, inferred if inferred else "mixed")


def _matches_expected_type(actual_type: str, expected_type: str) -> bool:
    """Return whether an inferred logical type matches a schema expectation.

    Args:
        actual_type: Logical type inferred from the Series values.
        expected_type: Logical type requested by the input schema.

    Returns:
        ``True`` when the inferred type is acceptable for the expected type and
        ``False`` otherwise.
    """

    if actual_type == "empty":
        return True

    valid_expected_types = {"int", "float", "number", "string", "datetime", "bool"}
    if expected_type not in valid_expected_types:
        raise ValueError(f"Unsupported schema type: {expected_type}")

    if expected_type == "number":
        return actual_type in {"int", "float", "number"}

    if expected_type == "float":
        return actual_type == "float"

    return actual_type == expected_type


def _normalize_expected_type(expected_type: Any) -> str:
    """Normalize and validate an expected logical type from the schema.

    The schema validator accepts a small controlled vocabulary of logical
    labels. Normalizing the incoming value keeps the output deterministic and
    avoids treating formatting differences such as surrounding spaces or
    capitalized input as distinct schema definitions.

    Args:
        expected_type: Raw expected type value provided by the schema mapping.

    Returns:
        A normalized expected-type label using lowercase text.

    Raises:
        ValueError: If the normalized type is not supported by the validator.
    """

    normalized_expected_type = str(expected_type).strip().lower()
    valid_expected_types = {"int", "float", "number", "string", "datetime", "bool"}

    if normalized_expected_type not in valid_expected_types:
        raise ValueError(f"Unsupported schema type: {expected_type}")

    return normalized_expected_type


def clean_customer_names(
    df: pd.DataFrame,
    name_col: str = "customer_name",
    output_col: str = "customer_name_clean",
) -> pd.DataFrame:
    """Standardize customer names into a new normalized column.

    The transformation collapses repeated whitespace, lowercases the content,
    removes accent marks, and maps null or blank values to ``pd.NA``. The
    original input DataFrame is preserved.

    Args:
        df: Source DataFrame containing the customer name column.
        name_col: Name of the input column with raw customer names.
        output_col: Name of the output column that will store normalized names.

    Returns:
        A new DataFrame containing the additional normalized name column.
    """

    result = _clone_dataframe(df)
    result[output_col] = result[name_col].apply(_normalize_optional_string)
    return result


def deduplicate_events(
    df: pd.DataFrame,
    id_col: str = "event_id",
    timestamp_col: str = "updated_at",
) -> pd.DataFrame:
    """Remove duplicated events while keeping the most recent row per event.

    Rows with null identifiers are preserved because they cannot be safely
    grouped into a duplicate set. Invalid timestamps are treated as older than
    valid timestamps. When timestamps tie within the same event identifier, the
    last row in the original order is retained.

    Args:
        df: Source DataFrame with event records.
        id_col: Column that identifies an event entity.
        timestamp_col: Column containing the update timestamp.

    Returns:
        A new DataFrame with duplicated identified events removed.
    """

    result = _clone_dataframe(df)
    result["_original_order"] = range(len(result))
    result["_parsed_timestamp"] = pd.to_datetime(result[timestamp_col], errors="coerce")

    identified_rows = result[result[id_col].notna()].copy()
    unidentified_rows = result[result[id_col].isna()].copy()

    deduplicated_identified = (
        identified_rows.sort_values(
            by=[id_col, "_parsed_timestamp", "_original_order"],
            ascending=[True, True, True],
            kind="stable",
            na_position="first",
        )
        .drop_duplicates(subset=[id_col], keep="last")
        .copy()
    )

    final_result = pd.concat([deduplicated_identified, unidentified_rows], ignore_index=True)
    final_result = final_result.sort_values(by="_original_order", kind="stable").drop(
        columns=["_original_order", "_parsed_timestamp"]
    )

    return final_result.reset_index(drop=True)


def calculate_monthly_revenue(
    df: pd.DataFrame,
    date_col: str = "order_date",
    amount_col: str = "amount",
    status_col: str = "status",
) -> pd.DataFrame:
    """Aggregate monthly revenue from valid non-canceled orders.

    The function ignores rows with invalid order dates, normalizes the status
    field to detect canceled orders, treats invalid or missing amounts as zero,
    and returns the monthly totals in ``YYYY-MM`` format.

    Args:
        df: Source DataFrame with order information.
        date_col: Column containing the order date.
        amount_col: Column containing the monetary amount.
        status_col: Column containing the order status.

    Returns:
        A DataFrame with columns ``month`` and ``revenue`` sorted by month.
    """

    result = _clone_dataframe(df)
    parsed_dates = pd.to_datetime(result[date_col], errors="coerce")
    normalized_status = result[status_col].apply(_normalize_status_text)
    normalized_amounts = pd.to_numeric(result[amount_col], errors="coerce").fillna(0)
    cancelled_statuses = {"cancelled", "canceled", "cancelado"}

    valid_mask = parsed_dates.notna() & ~normalized_status.isin(cancelled_statuses)

    filtered = pd.DataFrame(
        {
            "month": parsed_dates[valid_mask].dt.strftime("%Y-%m"),
            "revenue": normalized_amounts[valid_mask],
        }
    )

    monthly_revenue = filtered.groupby("month", as_index=False)["revenue"].sum().sort_values(
        "month",
        kind="stable",
    )

    return monthly_revenue.reset_index(drop=True)


def join_customers_orders(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    customer_key: str = "customer_id",
) -> pd.DataFrame:
    """Join customer and order datasets using a full outer join.

    The output preserves unmatched rows from both inputs and annotates the join
    outcome through the ``record_status`` column. Null join keys are handled
    explicitly so rows with missing identifiers are never classified as
    ``matched``. The result is also sorted deterministically and returned with
    a reset index.

    Args:
        customers: Customer DataFrame.
        orders: Order DataFrame.
        customer_key: Join key shared by both datasets.

    Returns:
        A new DataFrame containing the full outer join plus a status label.
    """

    customers_copy = _clone_dataframe(customers)
    orders_copy = _clone_dataframe(orders)

    customers_copy["_customer_source_order"] = range(len(customers_copy))
    orders_copy["_order_source_order"] = range(len(orders_copy))

    customers_with_key = customers_copy[customers_copy[customer_key].notna()].copy()
    customers_without_key = customers_copy[customers_copy[customer_key].isna()].copy()
    orders_with_key = orders_copy[orders_copy[customer_key].notna()].copy()
    orders_without_key = orders_copy[orders_copy[customer_key].isna()].copy()

    merged_with_keys = customers_with_key.merge(
        orders_with_key,
        on=customer_key,
        how="outer",
        indicator=True,
        sort=False,
    )

    status_mapping = {
        "both": "matched",
        "left_only": "customer_without_order",
        "right_only": "order_without_customer",
    }
    merged_with_keys["record_status"] = merged_with_keys["_merge"].map(status_mapping)
    merged_with_keys["_sort_order"] = merged_with_keys["_customer_source_order"].combine_first(
        merged_with_keys["_order_source_order"]
    )

    merged_columns = [column_name for column_name in merged_with_keys.columns if column_name != "_merge"]

    customer_null_rows = customers_without_key.copy()
    for column_name in merged_columns:
        if column_name not in customer_null_rows.columns:
            customer_null_rows[column_name] = pd.NA
    customer_null_rows["record_status"] = "customer_without_order"
    customer_null_rows["_sort_order"] = customer_null_rows["_customer_source_order"]
    customer_null_rows = customer_null_rows[merged_columns]

    order_null_rows = orders_without_key.copy()
    for column_name in merged_columns:
        if column_name not in order_null_rows.columns:
            order_null_rows[column_name] = pd.NA
    order_null_rows["record_status"] = "order_without_customer"
    order_null_rows["_sort_order"] = order_null_rows["_order_source_order"]
    order_null_rows = order_null_rows[merged_columns]

    final_result = pd.concat(
        [
            merged_with_keys.drop(columns="_merge"),
            customer_null_rows,
            order_null_rows,
        ],
        ignore_index=True,
        sort=False,
    )

    final_result = final_result.sort_values(
        by=["_sort_order", "_customer_source_order", "_order_source_order", "record_status"],
        kind="stable",
        na_position="last",
    )

    return final_result.drop(
        columns=["_sort_order", "_customer_source_order", "_order_source_order"]
    ).reset_index(drop=True)


def validate_schema(df: pd.DataFrame, schema: dict[str, str]) -> dict[str, Any]:
    """Validate DataFrame columns against a logical schema definition.

    Extra columns are allowed. Missing columns and logical type mismatches are
    reported in a structured dictionary so that downstream tooling can inspect
    validation failures programmatically. Expected logical types are normalized
    with ``strip().lower()`` and must belong to the supported set:
    ``int``, ``float``, ``number``, ``string``, ``datetime``, or ``bool``.

    Args:
        df: DataFrame to validate.
        schema: Mapping from column name to expected logical type.

    Returns:
        A dictionary with ``valid``, ``missing_columns``, and ``type_errors``.

    Raises:
        ValueError: If the schema contains an unsupported expected type.
    """

    missing_columns: list[str] = []
    type_errors: list[dict[str, str]] = []

    for column_name, expected_type in schema.items():
        normalized_expected_type = _normalize_expected_type(expected_type)

        if column_name not in df.columns:
            missing_columns.append(column_name)
            continue

        actual_type = _infer_series_type(df[column_name])
        if not _matches_expected_type(actual_type, normalized_expected_type):
            type_errors.append(
                {
                    "column": column_name,
                    "expected_type": normalized_expected_type,
                    "actual_type": actual_type,
                }
            )

    return {
        "valid": not missing_columns and not type_errors,
        "missing_columns": missing_columns,
        "type_errors": type_errors,
    }


def classify_payment_status(
    df: pd.DataFrame,
    reference_date: Any,
    due_date_col: str = "due_date",
    paid_date_col: str = "paid_date",
    amount_col: str = "amount",
    output_col: str = "payment_status",
) -> pd.DataFrame:
    """Classify each payment row according to due date, payment date, and amount.

    Invalid monetary values and invalid due dates are immediately marked as
    ``invalid``. A provided but invalid paid date is also classified as
    ``invalid`` instead of being treated as a missing payment. Valid paid dates
    are compared against the due date, while genuinely unpaid rows are
    classified relative to the provided reference date.

    Args:
        df: Source DataFrame with payment information.
        reference_date: Date used to classify unpaid records as pending or overdue.
        due_date_col: Column containing the due date.
        paid_date_col: Column containing the payment date.
        amount_col: Column containing the payment amount.
        output_col: Name of the output classification column.

    Returns:
        A new DataFrame with the payment status column added.
    """

    parsed_reference_date = pd.to_datetime(reference_date, errors="coerce")
    if pd.isna(parsed_reference_date):
        raise ValueError("reference_date must be a valid date-like value")

    result = _clone_dataframe(df)
    due_dates = pd.to_datetime(result[due_date_col], errors="coerce")
    paid_dates = pd.to_datetime(result[paid_date_col], errors="coerce")
    amounts = pd.to_numeric(result[amount_col], errors="coerce")
    paid_date_text = result[paid_date_col].astype("string").str.strip()
    paid_date_provided = result[paid_date_col].notna() & paid_date_text.ne("").fillna(False)

    statuses = pd.Series(index=result.index, dtype="object")

    invalid_paid_date_mask = paid_date_provided & paid_dates.isna()
    invalid_mask = due_dates.isna() | amounts.isna() | (amounts <= 0) | invalid_paid_date_mask
    statuses.loc[invalid_mask] = "invalid"

    paid_on_time_mask = (~invalid_mask) & paid_dates.notna() & (paid_dates <= due_dates)
    statuses.loc[paid_on_time_mask] = "paid_on_time"

    paid_late_mask = (~invalid_mask) & paid_dates.notna() & (paid_dates > due_dates)
    statuses.loc[paid_late_mask] = "paid_late"

    unpaid_mask = (~invalid_mask) & paid_dates.isna()
    overdue_mask = unpaid_mask & (parsed_reference_date > due_dates)
    pending_mask = unpaid_mask & (parsed_reference_date <= due_dates)

    statuses.loc[overdue_mask] = "overdue"
    statuses.loc[pending_mask] = "pending"

    result[output_col] = statuses
    return result

"""Tests that confirm each buggy implementation diverges from the correct one."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest

from ise26.implementations import correct
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
    wrong_type_schema_df,
)


def _dataframes_differ(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    """Return whether two DataFrame outputs are different."""

    return not left.equals(right)


def _dicts_differ(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Return whether two dictionary outputs are different."""

    return left != right


def _run_f01_bug01(module: Any) -> bool:
    """Exercise F01 bug 01 with a null-handling scenario."""

    source = customer_names_dirty_df().iloc[[3]].reset_index(drop=True)
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f01_bug02(module: Any) -> bool:
    """Exercise F01 bug 02 with an accent-removal scenario."""

    source = customer_names_dirty_df().iloc[[0]].reset_index(drop=True)
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f01_bug03(module: Any) -> bool:
    """Exercise F01 bug 03 with an internal-whitespace scenario."""

    source = customer_names_dirty_df().iloc[[5]].reset_index(drop=True)
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f02_bug01(module: Any) -> bool:
    """Exercise F02 bug 01 with duplicate recency ordering."""

    source = events_with_duplicates_df().iloc[[0, 1]].reset_index(drop=True)
    return _dataframes_differ(correct.deduplicate_events(source), module.deduplicate_events(source))


def _run_f02_bug02(module: Any) -> bool:
    """Exercise F02 bug 02 with a null event identifier."""

    source = events_with_duplicates_df().iloc[[1, 5]].reset_index(drop=True)
    return _dataframes_differ(correct.deduplicate_events(source), module.deduplicate_events(source))


def _run_f02_bug03(module: Any) -> bool:
    """Exercise F02 bug 03 with lexicographically misleading timestamps."""

    source = pd.DataFrame(
        {
            "event_id": [1, 1],
            "updated_at": ["2024-2-15", "2024-11-01"],
            "payload": ["february", "november"],
        }
    )
    return _dataframes_differ(correct.deduplicate_events(source), module.deduplicate_events(source))


def _run_f03_bug01(module: Any) -> bool:
    """Exercise F03 bug 01 with a canceled order."""

    source = orders_for_monthly_revenue_df().iloc[[0, 2]].reset_index(drop=True)
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f03_bug02(module: Any) -> bool:
    """Exercise F03 bug 02 with a month that only has invalid amounts."""

    source = orders_for_monthly_revenue_df().iloc[[3]].reset_index(drop=True)
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f03_bug03(module: Any) -> bool:
    """Exercise F03 bug 03 with multiple days in the same month."""

    source = orders_for_monthly_revenue_df().iloc[[0, 1]].reset_index(drop=True)
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f04_bug01(module: Any) -> bool:
    """Exercise F04 bug 01 with unmatched rows on both sides."""

    customers = customers_for_join_df()
    orders = orders_for_join_df()
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f04_bug02(module: Any) -> bool:
    """Exercise F04 bug 02 with a missing status-column scenario."""

    customers = customers_for_join_df().iloc[[0]].reset_index(drop=True)
    orders = orders_for_join_df().iloc[[0]].reset_index(drop=True)
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f04_bug03(module: Any) -> bool:
    """Exercise F04 bug 03 with a null-key order row."""

    customers = customers_for_join_df()
    orders = orders_for_join_df()
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f05_bug01(module: Any) -> bool:
    """Exercise F05 bug 01 with a missing required column."""

    source = missing_column_schema_df()
    schema = expected_schema_definition()
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f05_bug02(module: Any) -> bool:
    """Exercise F05 bug 02 with a type mismatch scenario."""

    source = wrong_type_schema_df()
    schema = expected_schema_definition()
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f05_bug03(module: Any) -> bool:
    """Exercise F05 bug 03 with an extra-column scenario."""

    source = extra_column_schema_df()
    schema = expected_schema_definition()
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f06_bug01(module: Any) -> bool:
    """Exercise F06 bug 01 with a due-date boundary payment."""

    source = payments_for_status_classification_df().iloc[[0]].reset_index(drop=True)
    return _dataframes_differ(
        correct.classify_payment_status(source, payment_reference_date()),
        module.classify_payment_status(source, payment_reference_date()),
    )


def _run_f06_bug02(module: Any) -> bool:
    """Exercise F06 bug 02 with a zero-amount unpaid row."""

    source = payments_for_status_classification_df().iloc[[4]].reset_index(drop=True)
    return _dataframes_differ(
        correct.classify_payment_status(source, payment_reference_date()),
        module.classify_payment_status(source, payment_reference_date()),
    )


def _run_f06_bug03(module: Any) -> bool:
    """Exercise F06 bug 03 with an invalid provided paid date."""

    source = payments_for_status_classification_df().iloc[[7]].reset_index(drop=True)
    return _dataframes_differ(
        correct.classify_payment_status(source, payment_reference_date()),
        module.classify_payment_status(source, payment_reference_date()),
    )


BUG_RUNNERS: list[tuple[str, Callable[[Any], bool]]] = [
    ("ise26.implementations.buggy.f01_bug01", _run_f01_bug01),
    ("ise26.implementations.buggy.f01_bug02", _run_f01_bug02),
    ("ise26.implementations.buggy.f01_bug03", _run_f01_bug03),
    ("ise26.implementations.buggy.f02_bug01", _run_f02_bug01),
    ("ise26.implementations.buggy.f02_bug02", _run_f02_bug02),
    ("ise26.implementations.buggy.f02_bug03", _run_f02_bug03),
    ("ise26.implementations.buggy.f03_bug01", _run_f03_bug01),
    ("ise26.implementations.buggy.f03_bug02", _run_f03_bug02),
    ("ise26.implementations.buggy.f03_bug03", _run_f03_bug03),
    ("ise26.implementations.buggy.f04_bug01", _run_f04_bug01),
    ("ise26.implementations.buggy.f04_bug02", _run_f04_bug02),
    ("ise26.implementations.buggy.f04_bug03", _run_f04_bug03),
    ("ise26.implementations.buggy.f05_bug01", _run_f05_bug01),
    ("ise26.implementations.buggy.f05_bug02", _run_f05_bug02),
    ("ise26.implementations.buggy.f05_bug03", _run_f05_bug03),
    ("ise26.implementations.buggy.f06_bug01", _run_f06_bug01),
    ("ise26.implementations.buggy.f06_bug02", _run_f06_bug02),
    ("ise26.implementations.buggy.f06_bug03", _run_f06_bug03),
]


@pytest.mark.parametrize(
    ("module_path", "runner"),
    BUG_RUNNERS,
    ids=[module_path.split(".")[-1] for module_path, _ in BUG_RUNNERS],
)
def test_each_buggy_module_differs_from_the_correct_implementation(
    module_path: str,
    runner: Callable[[Any], bool],
) -> None:
    """Verify that every buggy implementation diverges in at least one scenario."""

    module = importlib.import_module(module_path)
    assert runner(module), f"{module_path} did not diverge from the correct implementation"

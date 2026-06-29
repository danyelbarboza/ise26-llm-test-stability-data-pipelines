"""Tests that confirm each buggy implementation diverges from the correct one."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest

from ise26.implementations import correct


def _dataframes_differ(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    """Return whether two DataFrame outputs are different."""

    return not left.equals(right)


def _dicts_differ(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Return whether two dictionary outputs are different."""

    return left != right


def _run_f01_bug01(module: Any) -> bool:
    """Exercise F01 bug 01 with a null-handling scenario."""

    source = pd.DataFrame({"customer_name": [None]})
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f01_bug02(module: Any) -> bool:
    """Exercise F01 bug 02 with an accent-removal scenario."""

    source = pd.DataFrame({"customer_name": ["José"]})
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f01_bug03(module: Any) -> bool:
    """Exercise F01 bug 03 with an internal-whitespace scenario."""

    source = pd.DataFrame({"customer_name": [" Ana   Maria "]})
    return _dataframes_differ(
        correct.clean_customer_names(source),
        module.clean_customer_names(source),
    )


def _run_f02_bug01(module: Any) -> bool:
    """Exercise F02 bug 01 with duplicate recency ordering."""

    source = pd.DataFrame(
        {
            "event_id": [1, 1],
            "updated_at": ["2024-01-01", "2024-02-01"],
            "payload": ["old", "new"],
        }
    )
    return _dataframes_differ(correct.deduplicate_events(source), module.deduplicate_events(source))


def _run_f02_bug02(module: Any) -> bool:
    """Exercise F02 bug 02 with a null event identifier."""

    source = pd.DataFrame(
        {
            "event_id": [1, None],
            "updated_at": ["2024-01-01", "2024-02-01"],
            "payload": ["kept", "missing_id"],
        }
    )
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

    source = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "2024-01-11"],
            "amount": [100, 50],
            "status": ["paid", "cancelled"],
        }
    )
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f03_bug02(module: Any) -> bool:
    """Exercise F03 bug 02 with a month that only has invalid amounts."""

    source = pd.DataFrame(
        {
            "order_date": ["2024-02-10"],
            "amount": [None],
            "status": ["paid"],
        }
    )
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f03_bug03(module: Any) -> bool:
    """Exercise F03 bug 03 with multiple days in the same month."""

    source = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "2024-01-20"],
            "amount": [10, 20],
            "status": ["paid", "paid"],
        }
    )
    return _dataframes_differ(
        correct.calculate_monthly_revenue(source),
        module.calculate_monthly_revenue(source),
    )


def _run_f04_bug01(module: Any) -> bool:
    """Exercise F04 bug 01 with unmatched rows on both sides."""

    customers = pd.DataFrame({"customer_id": [1, 2]})
    orders = pd.DataFrame({"customer_id": [1, 3], "order_id": [10, 11]})
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f04_bug02(module: Any) -> bool:
    """Exercise F04 bug 02 with a missing status-column scenario."""

    customers = pd.DataFrame({"customer_id": [1]})
    orders = pd.DataFrame({"customer_id": [1], "order_id": [10]})
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f04_bug03(module: Any) -> bool:
    """Exercise F04 bug 03 with a null-key order row."""

    customers = pd.DataFrame({"customer_id": [1, None], "customer_name": ["Alice", "Missing Customer Id"]})
    orders = pd.DataFrame({"customer_id": [1, None], "order_id": [10, 11]})
    return _dataframes_differ(
        correct.join_customers_orders(customers, orders),
        module.join_customers_orders(customers, orders),
    )


def _run_f05_bug01(module: Any) -> bool:
    """Exercise F05 bug 01 with a missing required column."""

    source = pd.DataFrame({"customer_id": [1], "amount": [10]})
    schema = {"customer_id": "int", "amount": "number", "order_date": "datetime"}
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f05_bug02(module: Any) -> bool:
    """Exercise F05 bug 02 with a type mismatch scenario."""

    source = pd.DataFrame({"customer_id": ["one"]})
    schema = {"customer_id": "int"}
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f05_bug03(module: Any) -> bool:
    """Exercise F05 bug 03 with an extra-column scenario."""

    source = pd.DataFrame({"customer_id": [1], "extra_column": ["x"]})
    schema = {"customer_id": "int"}
    return _dicts_differ(correct.validate_schema(source, schema), module.validate_schema(source, schema))


def _run_f06_bug01(module: Any) -> bool:
    """Exercise F06 bug 01 with a due-date boundary payment."""

    source = pd.DataFrame({"due_date": ["2024-01-10"], "paid_date": ["2024-01-10"], "amount": [100]})
    return _dataframes_differ(
        correct.classify_payment_status(source, "2024-01-15"),
        module.classify_payment_status(source, "2024-01-15"),
    )


def _run_f06_bug02(module: Any) -> bool:
    """Exercise F06 bug 02 with a zero-amount unpaid row."""

    source = pd.DataFrame({"due_date": ["2024-01-20"], "paid_date": [None], "amount": [0]})
    return _dataframes_differ(
        correct.classify_payment_status(source, "2024-01-15"),
        module.classify_payment_status(source, "2024-01-15"),
    )


def _run_f06_bug03(module: Any) -> bool:
    """Exercise F06 bug 03 with an invalid provided paid date."""

    source = pd.DataFrame({"due_date": ["2024-01-10"], "paid_date": ["not-a-date"], "amount": [100]})
    return _dataframes_differ(
        correct.classify_payment_status(source, "2024-01-15"),
        module.classify_payment_status(source, "2024-01-15"),
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

    # Each buggy module should disagree with the correct implementation on
    # at least one focused scenario; otherwise it would not be useful for
    # the defect-detection part of the experiment.
    module = importlib.import_module(module_path)
    assert runner(module), f"{module_path} did not diverge from the correct implementation"

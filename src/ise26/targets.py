"""Dynamic target resolution for generated-test execution.

Generated test suites should always import functions from this module so that
the experimental runner can switch between the correct and buggy
implementations by changing an environment variable.
"""

from __future__ import annotations

import importlib
import os
from types import ModuleType


DEFAULT_TARGET_MODULE = "ise26.implementations.correct"
TARGET_ENV_VAR = "ISE26_TARGET_MODULE"
TARGET_FUNCTION_NAMES = [
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
]


def get_target_module_name() -> str:
    """Return the implementation module configured for the current process.

    The value comes from the ``ISE26_TARGET_MODULE`` environment variable. When
    the variable is absent or blank, the correct implementation module is used.

    Returns:
        The dotted module path that should provide the target functions.
    """

    module_name = os.getenv(TARGET_ENV_VAR, "").strip()
    return module_name or DEFAULT_TARGET_MODULE


def load_target_module() -> ModuleType:
    """Import and return the active implementation module.

    Returns:
        The imported Python module that contains the target transformation
        functions.

    Raises:
        ImportError: If the configured module cannot be imported.
        AttributeError: If the configured module does not expose a required
            target function.
    """

    module_name = get_target_module_name()

    try:
        module = importlib.import_module(module_name)
    except ImportError as error:
        raise ImportError(
            f"Unable to import target module '{module_name}' from {TARGET_ENV_VAR}."
        ) from error

    for function_name in TARGET_FUNCTION_NAMES:
        # The generated tests assume a stable public surface. Validating every
        # required function up front produces a clearer failure mode than
        # letting imports fail later during test execution.
        if not hasattr(module, function_name):
            raise AttributeError(
                f"Target module '{module_name}' does not define '{function_name}'."
            )

    return module


def _bind_target_functions() -> dict[str, object]:
    """Bind public function names from the active target module.

    Returns:
        A mapping from target function names to the callables loaded from the
        configured implementation module.
    """

    module = load_target_module()
    return {function_name: getattr(module, function_name) for function_name in TARGET_FUNCTION_NAMES}


# Bind the active callables at import time so generated tests can use standard
# imports such as ``from ise26.targets import clean_customer_names``.
_BOUND_FUNCTIONS = _bind_target_functions()

clean_customer_names = _BOUND_FUNCTIONS["clean_customer_names"]
deduplicate_events = _BOUND_FUNCTIONS["deduplicate_events"]
calculate_monthly_revenue = _BOUND_FUNCTIONS["calculate_monthly_revenue"]
join_customers_orders = _BOUND_FUNCTIONS["join_customers_orders"]
validate_schema = _BOUND_FUNCTIONS["validate_schema"]
classify_payment_status = _BOUND_FUNCTIONS["classify_payment_status"]
parse_order_items_json = _BOUND_FUNCTIONS["parse_order_items_json"]
calculate_conversion_rate = _BOUND_FUNCTIONS["calculate_conversion_rate"]
cap_outliers_iqr = _BOUND_FUNCTIONS["cap_outliers_iqr"]
standardize_currency_values = _BOUND_FUNCTIONS["standardize_currency_values"]

__all__ = [
    "DEFAULT_TARGET_MODULE",
    "TARGET_ENV_VAR",
    "TARGET_FUNCTION_NAMES",
    "get_target_module_name",
    "load_target_module",
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
]

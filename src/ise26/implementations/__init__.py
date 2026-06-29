"""Implementation entrypoints for correct and buggy transformation functions.

This module re-exports the correct implementations so repository-internal tests
and exploratory usage can import the canonical functions from a single place.
"""

from .correct import (
    calculate_monthly_revenue,
    classify_payment_status,
    clean_customer_names,
    deduplicate_events,
    join_customers_orders,
    validate_schema,
)

# Re-exporting only the correct implementations keeps the package surface small
# while leaving the buggy variants available through their explicit modules.
__all__ = [
    "calculate_monthly_revenue",
    "classify_payment_status",
    "clean_customer_names",
    "deduplicate_events",
    "join_customers_orders",
    "validate_schema",
]

"""Repository-level integrity checks for the ISE26 experiment scaffold."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from ise26.implementations import correct


FUNCTION_MAP = {
    "F01": "clean_customer_names",
    "F02": "deduplicate_events",
    "F03": "calculate_monthly_revenue",
    "F04": "join_customers_orders",
    "F05": "validate_schema",
    "F06": "classify_payment_status",
}

# The integrity checks inspect the file system directly because the experiment
# relies on the repository layout itself, not only on importable behavior.
BUGGY_ROOT = Path(__file__).resolve().parents[1] / "src" / "ise26" / "implementations" / "buggy"


def test_correct_module_contains_all_expected_public_functions() -> None:
    """Verify that the correct implementation module exposes the six functions."""

    for function_name in FUNCTION_MAP.values():
        assert hasattr(correct, function_name), f"Missing correct implementation: {function_name}"


def test_each_function_has_exactly_three_buggy_variants() -> None:
    """Verify that each target function has exactly three buggy variants."""

    for function_id in FUNCTION_MAP:
        buggy_modules = sorted(BUGGY_ROOT.glob(f"{function_id.lower()}_bug*.py"))
        assert len(buggy_modules) == 3, f"{function_id} should have exactly three buggy variants"


def test_each_buggy_module_overrides_only_the_target_function_with_same_signature() -> None:
    """Verify buggy-module scope, signature parity, and bug documentation comments."""

    for function_id, function_name in FUNCTION_MAP.items():
        correct_signature = inspect.signature(getattr(correct, function_name))
        buggy_modules = sorted(BUGGY_ROOT.glob(f"{function_id.lower()}_bug*.py"))

        for buggy_module_path in buggy_modules:
            # Import the buggy module explicitly so the test can compare the
            # overridden function with the canonical signature from correct.py.
            module_name = f"ise26.implementations.buggy.{buggy_module_path.stem}"
            buggy_module = importlib.import_module(module_name)
            buggy_function = getattr(buggy_module, function_name)

            assert inspect.signature(buggy_function) == correct_signature
            assert buggy_function.__module__ == module_name

            source_code = buggy_module_path.read_text(encoding="utf-8")
            assert "# BUG:" in source_code, f"{buggy_module_path.name} should document the intentional bug"

            for other_function_name in FUNCTION_MAP.values():
                imported_function = getattr(buggy_module, other_function_name)

                if other_function_name == function_name:
                    continue

                # All non-target functions should still come from the correct
                # module because each buggy file is meant to isolate one defect.
                assert (
                    imported_function.__module__ == "ise26.implementations.correct"
                ), f"{buggy_module_path.name} should only override {function_name}"

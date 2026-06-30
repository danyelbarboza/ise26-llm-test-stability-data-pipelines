"""Tests for dynamic target resolution through `ise26.targets`."""

from __future__ import annotations

import importlib


def test_targets_defaults_to_correct_module(monkeypatch) -> None:
    """Verify that the correct implementation is used by default."""

    monkeypatch.delenv("ISE26_TARGET_MODULE", raising=False)
    module = importlib.import_module("ise26.targets")
    module = importlib.reload(module)

    assert module.get_target_module_name() == "ise26.implementations.correct"
    assert module.clean_customer_names.__module__ == "ise26.implementations.correct"


def test_targets_uses_environment_selected_module(monkeypatch) -> None:
    """Verify that the environment variable switches the implementation."""

    monkeypatch.setenv("ISE26_TARGET_MODULE", "ise26.implementations.buggy.f01_bug02")
    module = importlib.import_module("ise26.targets")
    module = importlib.reload(module)

    assert module.get_target_module_name() == "ise26.implementations.buggy.f01_bug02"
    assert module.clean_customer_names.__module__ == "ise26.implementations.buggy.f01_bug02"


def test_targets_exposes_all_ten_official_functions(monkeypatch) -> None:
    """Verify that the stable import surface includes the expanded function set."""

    monkeypatch.delenv("ISE26_TARGET_MODULE", raising=False)
    module = importlib.import_module("ise26.targets")
    module = importlib.reload(module)

    assert len(module.TARGET_FUNCTION_NAMES) == 10
    assert module.parse_order_items_json.__module__ == "ise26.implementations.correct"
    assert module.calculate_conversion_rate.__module__ == "ise26.implementations.correct"
    assert module.cap_outliers_iqr.__module__ == "ise26.implementations.correct"
    assert module.standardize_currency_values.__module__ == "ise26.implementations.correct"

"""Validation tests for runner and summary methodological metrics."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_generated_tests.py"
SUMMARY_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "summarize_results.py"


def load_module_from_path(module_name: str, path: Path):
    """Load a Python module directly from a file path."""

    specification = importlib.util.spec_from_file_location(module_name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def build_single_target_matrix() -> list[dict[str, str]]:
    """Build one correct target and one buggy target for F01."""

    return [
        {
            "function_id": "F01",
            "target_module": "ise26.implementations.correct",
            "target_type": "correct",
            "bug_id": "",
        },
        {
            "function_id": "F01",
            "target_module": "ise26.implementations.buggy.f01_bug01",
            "target_type": "buggy",
            "bug_id": "BUG01",
        },
    ]


def write_generated_test_file(base_path: Path, content: str, status: str | None = None) -> Path:
    """Write one generated test file inside an isolated temporary tree."""

    test_file = base_path / "experiments" / "generated_tests" / "F01" / "run_01" / "test_generated.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(content, encoding="utf-8")

    if status is not None:
        status_path = test_file.with_name("status.json")
        status_path.write_text(json.dumps({"status": status, "message": status}), encoding="utf-8")

    return test_file


def configure_runner_environment(monkeypatch, runner_module, base_path: Path, execute_pytest_result):
    """Redirect the runner to an isolated temporary directory."""

    monkeypatch.setattr(runner_module, "PROJECT_ROOT", base_path)
    monkeypatch.setattr(
        runner_module,
        "GENERATED_TESTS_ROOT",
        base_path / "experiments" / "generated_tests",
    )
    monkeypatch.setattr(runner_module, "RUN_IDS", ["run_01"])
    monkeypatch.setattr(runner_module, "build_target_matrix", build_single_target_matrix)
    monkeypatch.setattr(runner_module, "execute_pytest", execute_pytest_result)


def run_suite_scenario(monkeypatch, tmp_path: Path, content: str, execute_pytest_result, status: str | None = None):
    """Collect runner rows and summary rows for one isolated scenario."""

    runner_module = load_module_from_path("ise26_runner_metrics", RUNNER_SCRIPT_PATH)
    summary_module = load_module_from_path("ise26_summary_metrics", SUMMARY_SCRIPT_PATH)
    write_generated_test_file(tmp_path, content, status=status)
    configure_runner_environment(monkeypatch, runner_module, tmp_path, execute_pytest_result)

    rows = runner_module.collect_execution_rows()
    raw_frame = summary_module.prepare_raw_results(pd.DataFrame(rows))
    run_summary = summary_module.compute_run_level_metrics(raw_frame)
    return rows, run_summary


def build_ready_test_content() -> str:
    """Return a syntactically valid generated test file."""

    return (
        "from ise26.targets import clean_customer_names\n"
        "\n"
        "def test_placeholder():\n"
        "    assert True\n"
    )


def test_reliable_defect_detection(monkeypatch, tmp_path: Path) -> None:
    """Validate the reliable-detection path when the correct target passes."""

    def execute_pytest(test_file: Path, target_module: str) -> dict[str, object]:
        passed = target_module == "ise26.implementations.correct"
        return {
            "exit_code": 0 if passed else 1,
            "passed": passed,
            "stdout": "collected 1 item",
            "stderr": "",
            "duration_seconds": 0.01,
            "executable": True,
            "collected_tests": 1,
        }

    rows, run_summary = run_suite_scenario(monkeypatch, tmp_path, build_ready_test_content(), execute_pytest)

    correct_row = next(row for row in rows if row["target_type"] == "correct")
    buggy_row = next(row for row in rows if row["target_type"] == "buggy")

    assert correct_row["bug_failure"] is False
    assert correct_row["correct_passed_for_same_suite"] is True
    assert correct_row["reliable_defect_detection"] is False
    assert correct_row["contaminated_bug_failure"] is False

    assert buggy_row["bug_failure"] is True
    assert buggy_row["correct_passed_for_same_suite"] is True
    assert buggy_row["reliable_defect_detection"] is True
    assert buggy_row["false_positive"] is False
    assert buggy_row["contaminated_bug_failure"] is False

    assert run_summary.loc[0, "bug_failure_rate"] == 1.0
    assert run_summary.loc[0, "correct_pass_rate"] == 1.0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 1.0
    assert run_summary.loc[0, "false_positive_rate"] == 0.0
    assert run_summary.loc[0, "contaminated_bug_failure_count"] == 0


def test_contaminated_bug_failure(monkeypatch, tmp_path: Path) -> None:
    """Validate the contaminated path when the correct target fails too."""

    def execute_pytest(test_file: Path, target_module: str) -> dict[str, object]:
        return {
            "exit_code": 1,
            "passed": False,
            "stdout": "collected 1 item",
            "stderr": "",
            "duration_seconds": 0.01,
            "executable": True,
            "collected_tests": 1,
        }

    rows, run_summary = run_suite_scenario(monkeypatch, tmp_path, build_ready_test_content(), execute_pytest)

    correct_row = next(row for row in rows if row["target_type"] == "correct")
    buggy_row = next(row for row in rows if row["target_type"] == "buggy")

    assert correct_row["bug_failure"] is False
    assert correct_row["correct_passed_for_same_suite"] is False
    assert correct_row["reliable_defect_detection"] is False
    assert correct_row["false_positive"] is True

    assert buggy_row["bug_failure"] is True
    assert buggy_row["correct_passed_for_same_suite"] is False
    assert buggy_row["reliable_defect_detection"] is False
    assert buggy_row["false_positive"] is True
    assert buggy_row["contaminated_bug_failure"] is True

    assert run_summary.loc[0, "bug_failure_rate"] == 1.0
    assert run_summary.loc[0, "correct_pass_rate"] == 0.0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0
    assert run_summary.loc[0, "false_positive_rate"] == 1.0
    assert run_summary.loc[0, "contaminated_bug_failure_count"] == 1


def test_false_positive_without_bug_detection(monkeypatch, tmp_path: Path) -> None:
    """Validate the false-positive path when the bug target passes."""

    def execute_pytest(test_file: Path, target_module: str) -> dict[str, object]:
        passed = target_module != "ise26.implementations.correct"
        return {
            "exit_code": 0 if passed else 1,
            "passed": passed,
            "stdout": "collected 1 item",
            "stderr": "",
            "duration_seconds": 0.01,
            "executable": True,
            "collected_tests": 1,
        }

    rows, run_summary = run_suite_scenario(monkeypatch, tmp_path, build_ready_test_content(), execute_pytest)

    correct_row = next(row for row in rows if row["target_type"] == "correct")
    buggy_row = next(row for row in rows if row["target_type"] == "buggy")

    assert correct_row["bug_failure"] is False
    assert correct_row["correct_passed_for_same_suite"] is False
    assert correct_row["false_positive"] is True

    assert buggy_row["bug_failure"] is False
    assert buggy_row["reliable_defect_detection"] is False
    assert buggy_row["false_positive"] is True

    assert run_summary.loc[0, "bug_failure_rate"] == 0.0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0
    assert run_summary.loc[0, "false_positive_rate"] == 1.0


def test_weak_suite_passes_everything(monkeypatch, tmp_path: Path) -> None:
    """Validate that a weak suite does not count as defect detection."""

    def execute_pytest(test_file: Path, target_module: str) -> dict[str, object]:
        return {
            "exit_code": 0,
            "passed": True,
            "stdout": "collected 1 item",
            "stderr": "",
            "duration_seconds": 0.01,
            "executable": True,
            "collected_tests": 1,
        }

    rows, run_summary = run_suite_scenario(monkeypatch, tmp_path, build_ready_test_content(), execute_pytest)

    assert all(row["bug_failure"] is False for row in rows)
    assert all(row["correct_passed_for_same_suite"] is True for row in rows)
    assert all(row["reliable_defect_detection"] is False for row in rows)
    assert all(row["false_positive"] is False for row in rows)
    assert run_summary.loc[0, "bug_failure_rate"] == 0.0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0


def test_placeholder_is_not_executed(monkeypatch, tmp_path: Path) -> None:
    """Validate that placeholders stay out of the real-execution path."""

    runner_module = load_module_from_path("ise26_runner_placeholder", RUNNER_SCRIPT_PATH)
    summary_module = load_module_from_path("ise26_summary_placeholder", SUMMARY_SCRIPT_PATH)
    write_generated_test_file(
        tmp_path,
        '"""Placeholder file."""\n# GENERATED_TEST_PLACEHOLDER\n',
        status="placeholder",
    )
    configure_runner_environment(
        monkeypatch,
        runner_module,
        tmp_path,
        lambda *args, **kwargs: pytest.fail("Placeholder files must not be executed."),
    )

    rows = runner_module.collect_execution_rows()
    raw_frame = summary_module.prepare_raw_results(pd.DataFrame(rows))
    run_summary = summary_module.compute_run_level_metrics(raw_frame)

    assert all(row["suite_is_real_generated"] is False for row in rows)
    assert all(row["suite_is_placeholder"] is True for row in rows)
    assert all(row["executable"] is False for row in rows)
    assert run_summary.loc[0, "real_suite_count"] == 0
    assert run_summary.loc[0, "placeholder_suite_count"] == 1
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0


def test_syntax_invalid_file_is_reported_separately(monkeypatch, tmp_path: Path) -> None:
    """Validate that invalid syntax is classified separately from defect detection."""

    runner_module = load_module_from_path("ise26_runner_syntax_invalid", RUNNER_SCRIPT_PATH)
    summary_module = load_module_from_path("ise26_summary_syntax_invalid", SUMMARY_SCRIPT_PATH)
    write_generated_test_file(
        tmp_path,
        "def test_broken(:\n    assert True\n",
    )
    configure_runner_environment(
        monkeypatch,
        runner_module,
        tmp_path,
        lambda *args, **kwargs: pytest.fail("Invalid syntax files must not be executed."),
    )

    rows = runner_module.collect_execution_rows()
    raw_frame = summary_module.prepare_raw_results(pd.DataFrame(rows))
    run_summary = summary_module.compute_run_level_metrics(raw_frame)

    assert all(row["suite_generation_status"] == "syntax_invalid" for row in rows)
    assert all(row["executable"] is False for row in rows)
    assert all(row["bug_failure"] is False for row in rows)
    assert run_summary.loc[0, "suite_generation_status"] == "syntax_invalid"
    assert bool(run_summary.loc[0, "suite_is_real_generated"]) is False
    assert run_summary.loc[0, "real_target_executions"] == 0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0

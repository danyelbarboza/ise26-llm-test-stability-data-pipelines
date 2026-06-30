"""Execute generated pytest suites against correct and buggy implementations."""

from __future__ import annotations

import csv
from collections import defaultdict
import json
import os
import re
import subprocess
import sys
import time
import ast
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORRECT_MODULE_PATH = PROJECT_ROOT / "src" / "ise26" / "implementations" / "correct.py"
FUNCTIONS_METADATA_PATH = PROJECT_ROOT / "src" / "ise26" / "metadata" / "functions.json"
BUGS_METADATA_PATH = PROJECT_ROOT / "src" / "ise26" / "metadata" / "bugs.json"
GENERATED_TESTS_ROOT = PROJECT_ROOT / "experiments" / "generated_tests"
RAW_RESULTS_PATH = PROJECT_ROOT / "results" / "raw" / "generated_tests_results.csv"
PLACEHOLDER_MARKER = "GENERATED_TEST_PLACEHOLDER"
RUN_IDS = [f"run_{index:02d}" for index in range(1, 6)]


def load_json_records(path: Path) -> list[dict[str, Any]]:
    """Load a JSON file expected to contain a list of record dictionaries.

    Args:
        path: Path to the JSON file.

    Returns:
        A list of dictionaries loaded from the file.
    """

    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def build_target_matrix() -> list[dict[str, Any]]:
    """Create the full execution matrix for correct and buggy targets.

    Returns:
        A flat list of execution descriptors containing the function metadata
        and the corresponding target module information.
    """

    functions_metadata = load_json_records(FUNCTIONS_METADATA_PATH)
    bugs_metadata = load_json_records(BUGS_METADATA_PATH)

    bugs_by_function: dict[str, list[dict[str, Any]]] = {}
    for bug_record in bugs_metadata:
        bugs_by_function.setdefault(bug_record["function_id"], []).append(bug_record)

    target_matrix: list[dict[str, Any]] = []
    for function_record in functions_metadata:
        function_id = function_record["id"]
        target_matrix.append(
            {
                "function_id": function_id,
                "target_module": function_record["module"],
                "target_type": "correct",
                "bug_id": "",
            }
        )

        for bug_record in sorted(bugs_by_function.get(function_id, []), key=lambda item: item["bug_id"]):
            target_matrix.append(
                {
                    "function_id": function_id,
                    "target_module": bug_record["module"],
                    "target_type": "buggy",
                    "bug_id": bug_record["bug_id"],
                }
            )

    return target_matrix


def count_collected_tests(stdout: str) -> int | None:
    """Extract the collected-test count from pytest stdout when available.

    Args:
        stdout: Captured pytest standard output.

    Returns:
        The integer number of collected tests, or ``None`` when the pattern is
        not present in the output.
    """

    matches = re.findall(r"collected\s+(\d+)\s+items?", stdout)
    if matches:
        return int(matches[-1])
    return None


def count_assert_statements(content: str) -> int:
    """Return a rough count of assert statements in a test file.

    The value is intentionally approximate and is used only for descriptive
    metadata in the experimental scaffold.
    """

    return len(re.findall(r"\bassert\b", content))


def count_test_functions(content: str) -> int:
    """Return the number of pytest-style test functions in a file."""

    return len(re.findall(r"^\s*def\s+test_", content, flags=re.MULTILINE))


def detect_fixtures_import(content: str) -> bool:
    """Return whether the generated test imports the internal fixtures module."""

    return bool(re.search(r"^\s*(from|import)\s+tests\.fixtures\b", content, flags=re.MULTILINE))


def detect_targets_only_import(content: str) -> bool:
    """Return whether project imports are limited to `ise26.targets`.

    The file may still import third-party testing dependencies such as pandas
    and pytest. The check only constrains imports that come from within the
    repository itself.
    """

    forbidden_project_imports = [
        r"^\s*(from|import)\s+tests\.",
        r"^\s*(from|import)\s+ise26\.implementations\.",
        r"^\s*(from|import)\s+ise26\.metadata\.",
        r"^\s*(from|import)\s+ise26\.llm\.",
    ]

    if any(re.search(pattern, content, flags=re.MULTILINE) for pattern in forbidden_project_imports):
        return False

    return bool(re.search(r"^\s*from\s+ise26\.targets\s+import\s+", content, flags=re.MULTILINE))


def analyze_generated_test_file(test_file: Path, test_file_status: str) -> dict[str, Any]:
    """Collect static metadata for a generated test file.

    Args:
        test_file: Path to the generated test file.
        test_file_status: Status label returned by ``detect_test_presence``.

    Returns:
        A dictionary with rough static metrics and import-surface flags.
    """

    if not test_file.exists() or test_file_status != "ready":
        return {
            "generated_line_count": 0,
            "generated_test_function_count": 0,
            "generated_assert_count": 0,
            "imports_tests_fixtures": False,
            "imports_only_ise26_targets": False,
            "generated_has_real_suite": False,
        }

    content = test_file.read_text(encoding="utf-8")
    return {
        "generated_line_count": len(content.splitlines()),
        "generated_test_function_count": count_test_functions(content),
        "generated_assert_count": count_assert_statements(content),
        "imports_tests_fixtures": detect_fixtures_import(content),
        "imports_only_ise26_targets": detect_targets_only_import(content),
        "generated_has_real_suite": True,
    }


def detect_test_presence(test_file: Path) -> tuple[bool, str]:
    """Determine whether a generated test file contains executable tests.

    Args:
        test_file: Path to the generated test file.

    Returns:
        A tuple with a boolean flag and a short status label.
    """

    if not test_file.exists():
        return False, "missing"

    content = test_file.read_text(encoding="utf-8")
    status_path = test_file.with_name("status.json")
    if status_path.exists():
        with status_path.open("r", encoding="utf-8") as file_handle:
            status_payload = json.load(file_handle)

        status_value = str(status_payload.get("status", "")).strip()
        if status_value in {"not_generated", "api_error"}:
            return False, status_value

    if PLACEHOLDER_MARKER in content:
        return False, "placeholder"

    # A lightweight pattern check is enough here because the repository should
    # not execute arbitrary placeholder files when they do not actually define
    # pytest tests yet.
    try:
        ast.parse(content)
    except SyntaxError:
        return False, "syntax_invalid"

    test_patterns = [
        re.compile(r"^\s*def\s+test_", re.MULTILINE),
        re.compile(r"^\s*class\s+Test", re.MULTILINE),
    ]

    if any(pattern.search(content) for pattern in test_patterns):
        return True, "ready"

    if content.strip() == "":
        return False, "empty"

    return False, "no_tests_detected"


def execute_pytest(test_file: Path, target_module: str) -> dict[str, Any]:
    """Run pytest for a generated test file against a selected target module.

    Args:
        test_file: Path to the generated test file.
        target_module: Dotted Python module path selected for `ise26.targets`.

    Returns:
        A dictionary containing subprocess execution data and derived flags.
    """

    environment = os.environ.copy()
    environment["ISE26_TARGET_MODULE"] = target_module

    start_time = time.perf_counter()
    # Running pytest through the current interpreter keeps the environment
    # consistent with the one used for repository validation.
    completed_process = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    duration_seconds = time.perf_counter() - start_time

    executable = completed_process.returncode in {0, 1}
    passed = completed_process.returncode == 0

    return {
        "exit_code": completed_process.returncode,
        "passed": passed,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
        "duration_seconds": round(duration_seconds, 6),
        "executable": executable,
        "collected_tests": count_collected_tests(completed_process.stdout),
    }


def build_missing_test_result(test_file_status: str) -> dict[str, Any]:
    """Create a controlled result payload for missing or placeholder tests.

    Args:
        test_file_status: Short label describing why the test file was not run.

    Returns:
        A dictionary compatible with the CSV output schema.
    """

    message_map = {
        "missing": "Generated test file is missing.",
        "placeholder": "Generated test file is still a placeholder and was not executed.",
        "empty": "Generated test file is empty and was not executed.",
        "no_tests_detected": "Generated test file does not define pytest tests and was not executed.",
        "syntax_invalid": "Generated test file has invalid Python syntax and was not executed.",
        "api_error": "Generated test file was not executed because the API call failed.",
        "not_generated": "Generated test file was not executed because the suite was not generated yet.",
    }

    return {
        "exit_code": "",
        "passed": False,
        "stdout": "",
        "stderr": message_map.get(test_file_status, "Generated test file was not executed."),
        "duration_seconds": 0.0,
        "executable": False,
        "collected_tests": "",
    }


def write_results_csv(rows: list[dict[str, Any]]) -> None:
    """Persist execution rows to the raw-results CSV file.

    Args:
        rows: Execution rows to serialize.
    """

    RAW_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "function_id",
        "run_id",
        "test_file",
        "test_file_status",
        "target_module",
        "target_type",
        "bug_id",
        "exit_code",
        "passed",
        "stdout",
        "stderr",
        "duration_seconds",
        "executable",
        "collected_tests",
        "bug_failure",
        "correct_passed_for_same_suite",
        "reliable_defect_detection",
        "false_positive",
        "contaminated_bug_failure",
        "failure_detected",
        "suite_generation_status",
        "suite_is_real_generated",
        "suite_is_placeholder",
        "generated_line_count",
        "generated_test_function_count",
        "generated_assert_count",
        "imports_tests_fixtures",
        "imports_only_ise26_targets",
        "generated_has_real_suite",
    ]

    with RAW_RESULTS_PATH.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def collect_execution_rows() -> list[dict[str, Any]]:
    """Build raw execution rows for every configured function and run.

    Returns:
        A list of raw execution result dictionaries.
    """

    target_matrix = build_target_matrix()
    rows: list[dict[str, Any]] = []
    targets_by_function: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for target_row in target_matrix:
        targets_by_function[target_row["function_id"]].append(target_row)

    for function_id, function_targets in targets_by_function.items():
        for run_id in RUN_IDS:
            test_file = GENERATED_TESTS_ROOT / function_id / run_id / "test_generated.py"
            has_executable_tests, test_file_status = detect_test_presence(test_file)
            suite_static_analysis = analyze_generated_test_file(test_file, test_file_status)
            suite_rows: list[dict[str, Any]] = []

            for function_target in function_targets:
                if has_executable_tests:
                    execution_result = execute_pytest(test_file, function_target["target_module"])
                else:
                    # Missing, empty, or placeholder files are recorded as
                    # controlled outcomes so the runner remains usable before any
                    # real LLM-generated suites are added to the repository.
                    execution_result = build_missing_test_result(test_file_status)

                bug_failure = (
                    function_target["target_type"] == "buggy"
                    and execution_result["executable"]
                    and not execution_result["passed"]
                )

                row = {
                    "function_id": function_id,
                    "run_id": run_id,
                    "test_file": str(test_file.relative_to(PROJECT_ROOT)),
                    "test_file_status": test_file_status,
                    "target_module": function_target["target_module"],
                    "target_type": function_target["target_type"],
                    "bug_id": function_target["bug_id"],
                    **execution_result,
                    "bug_failure": bug_failure,
                    "failure_detected": bug_failure,
                    "suite_generation_status": test_file_status,
                    "suite_is_real_generated": test_file_status == "ready",
                    "suite_is_placeholder": test_file_status == "placeholder",
                    **suite_static_analysis,
                }
                suite_rows.append(row)

            correct_row = next((row for row in suite_rows if row["target_type"] == "correct"), None)
            correct_passed_for_same_suite = bool(correct_row and correct_row["passed"])
            false_positive = bool(test_file_status == "ready" and correct_row and not correct_row["passed"])

            for row in suite_rows:
                row["correct_passed_for_same_suite"] = correct_passed_for_same_suite
                row["reliable_defect_detection"] = bool(
                    row["bug_failure"] and correct_passed_for_same_suite
                )
                row["contaminated_bug_failure"] = bool(
                    row["bug_failure"] and false_positive
                )
                row["false_positive"] = false_positive

            rows.extend(suite_rows)

    return rows


def print_execution_summary(rows: list[dict[str, Any]]) -> None:
    """Print a short human-readable summary of the runner output.

    Args:
        rows: Raw execution rows produced by the runner.
    """

    executed_rows = sum(1 for row in rows if row["executable"])
    placeholder_rows = sum(1 for row in rows if row["test_file_status"] == "placeholder")
    missing_rows = sum(1 for row in rows if row["test_file_status"] == "missing")
    syntax_invalid_rows = sum(1 for row in rows if row["test_file_status"] == "syntax_invalid")
    real_suites = len({(row["function_id"], row["run_id"]) for row in rows if row["suite_is_real_generated"]})
    placeholder_suites = len({(row["function_id"], row["run_id"]) for row in rows if row["suite_is_placeholder"]})

    print(f"Saved raw results to: {RAW_RESULTS_PATH}")
    print(f"Total target executions recorded: {len(rows)}")
    print(f"Real suites detected: {real_suites}")
    print(f"Placeholder suites detected: {placeholder_suites}")
    print(f"Executable target executions: {executed_rows}")
    print(f"Placeholder target executions skipped: {placeholder_rows}")
    print(f"Missing target executions skipped: {missing_rows}")
    print(f"Syntax-invalid target executions skipped: {syntax_invalid_rows}")

    if executed_rows == 0:
        print("No executable generated tests were found.")


def main() -> int:
    """Run the generated-test execution workflow and write the raw CSV file.

    Returns:
        Process exit code suitable for command-line usage.
    """

    rows = collect_execution_rows()
    write_results_csv(rows)
    print_execution_summary(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

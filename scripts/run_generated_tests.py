"""Execute generated pytest suites against correct and buggy implementations."""

from __future__ import annotations

import csv
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
        "failure_detected",
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

    for function_target in target_matrix:
        function_id = function_target["function_id"]
        for run_id in RUN_IDS:
            test_file = GENERATED_TESTS_ROOT / function_id / run_id / "test_generated.py"
            has_executable_tests, test_file_status = detect_test_presence(test_file)

            if has_executable_tests:
                execution_result = execute_pytest(test_file, function_target["target_module"])
            else:
                # Missing, empty, or placeholder files are recorded as
                # controlled outcomes so the runner remains usable before any
                # real LLM-generated suites are added to the repository.
                execution_result = build_missing_test_result(test_file_status)

            failure_detected = (
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
                "failure_detected": failure_detected,
            }
            rows.append(row)

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

    print(f"Saved raw results to: {RAW_RESULTS_PATH}")
    print(f"Total target executions recorded: {len(rows)}")
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

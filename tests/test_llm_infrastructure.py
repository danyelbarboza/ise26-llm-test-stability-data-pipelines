"""Tests for the DeepSeek integration scaffold without real API calls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from ise26.llm.code_extraction import extract_python_code
from ise26.llm.deepseek_client import require_api_key
from ise26.llm.prompt_builder import build_prompt_bundle
from ise26.llm.reproducibility import (
    compute_file_hash,
    compute_json_hash,
    compute_text_hash,
    load_json_configuration,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATE_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_llm_tests.py"
RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_generated_tests.py"
CONFIG_PATH = PROJECT_ROOT / "experiments" / "config" / "deepseek_v4_flash.json"


def load_module_from_path(module_name: str, path: Path):
    """Load a Python module directly from a file path for testing."""

    specification = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(specification)
    assert specification is not None
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_prompt_builder_includes_targets_import_and_expected_behavior() -> None:
    """Verify that the built prompt keeps the stable import surface and rules."""

    prompt_bundle = build_prompt_bundle(
        function_id="F01",
        function_name="clean_customer_names",
        function_docstring="Normalize customer names.",
        function_code="def clean_customer_names(df):\n    return df\n",
        expected_behavior="Return a new DataFrame with normalized names.",
        function_description="Normalize customer names without mutating the input.",
    )

    assert "from ise26.targets import clean_customer_names" in prompt_bundle.user_prompt
    assert "Return a new DataFrame with normalized names." in prompt_bundle.user_prompt
    assert "Não altere" in prompt_bundle.user_prompt


def test_extract_python_code_from_python_fence() -> None:
    """Verify extraction from a fenced Python block."""

    result = extract_python_code("```python\ndef test_example():\n    assert 1 == 1\n```")

    assert result.code == "def test_example():\n    assert 1 == 1"
    assert result.syntax_valid is True
    assert result.extraction_mode == "markdown_python"


def test_extract_python_code_without_markdown() -> None:
    """Verify extraction when the response already contains raw code."""

    result = extract_python_code("def test_plain():\n    assert True\n")

    assert result.code == "def test_plain():\n    assert True"
    assert result.syntax_valid is True
    assert result.extraction_mode == "raw_text"


def test_extract_python_code_marks_invalid_syntax() -> None:
    """Verify syntax validation for invalid extracted code."""

    result = extract_python_code("```python\ndef test_broken(:\n    assert True\n```")

    assert result.syntax_valid is False
    assert result.syntax_error is not None


def test_compute_hashes_are_deterministic() -> None:
    """Verify deterministic SHA-256 generation for text and JSON."""

    first_text_hash = compute_text_hash("ise26")
    second_text_hash = compute_text_hash("ise26")
    first_json_hash = compute_json_hash({"b": 2, "a": 1})
    second_json_hash = compute_json_hash({"a": 1, "b": 2})

    assert first_text_hash == second_text_hash
    assert first_json_hash == second_json_hash


def test_compute_file_hash_matches_correct_module_contents() -> None:
    """Verify that hashing the full correct module stays deterministic."""

    correct_module_path = PROJECT_ROOT / "src" / "ise26" / "implementations" / "correct.py"

    assert compute_file_hash(correct_module_path) == compute_text_hash(
        correct_module_path.read_text(encoding="utf-8")
    )


def test_load_json_configuration_reads_deepseek_defaults() -> None:
    """Verify that the official DeepSeek configuration file loads correctly."""

    config = load_json_configuration(CONFIG_PATH)

    assert config["provider"] == "DeepSeek"
    assert config["model"] == "deepseek-v4-flash"
    assert config["runs_per_function"] == 5


def test_require_api_key_raises_clear_error_when_missing(monkeypatch) -> None:
    """Verify that missing API credentials produce a clear runtime error."""

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="Missing DeepSeek API key"):
        require_api_key()


def test_generate_llm_tests_dry_run_succeeds() -> None:
    """Verify that the official generation script runs safely in dry-run mode."""

    completed = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT_PATH), "--dry-run"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Generation mode: DRY-RUN" in completed.stdout
    assert "No API calls were made" in completed.stdout


def test_generate_llm_tests_rejects_dry_run_and_execute_together() -> None:
    """Verify that the generation script rejects conflicting mode flags."""

    completed = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT_PATH), "--dry-run", "--execute"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "not allowed with argument" in completed.stderr


def test_runner_detects_syntax_invalid_generated_test(tmp_path: Path) -> None:
    """Verify that the runner skips generated files with invalid syntax."""

    runner_module = load_module_from_path("ise26_runner_test", RUNNER_SCRIPT_PATH)
    test_file = tmp_path / "test_generated.py"
    test_file.write_text("def test_broken(:\n    assert True\n", encoding="utf-8")

    has_tests, status = runner_module.detect_test_presence(test_file)

    assert has_tests is False
    assert status == "syntax_invalid"


def test_runner_uses_status_file_for_api_error(tmp_path: Path) -> None:
    """Verify that the runner respects explicit API error status metadata."""

    runner_module = load_module_from_path("ise26_runner_test_api_error", RUNNER_SCRIPT_PATH)
    test_file = tmp_path / "test_generated.py"
    test_file.write_text("# GENERATED_TEST_PLACEHOLDER\n", encoding="utf-8")
    (tmp_path / "status.json").write_text(
        '{"status": "api_error", "message": "Synthetic API error for test."}',
        encoding="utf-8",
    )

    has_tests, status = runner_module.detect_test_presence(test_file)

    assert has_tests is False
    assert status == "api_error"


def test_runner_static_analysis_counts_tests_and_imports() -> None:
    """Verify the runner's static analysis helpers on a synthetic test file."""

    runner_module = load_module_from_path("ise26_runner_static_analysis", RUNNER_SCRIPT_PATH)
    content = (
        "from ise26.targets import clean_customer_names\n"
        "\n"
        "def test_clean_customer_names():\n"
        "    assert True\n"
    )

    assert runner_module.count_test_functions(content) == 1
    assert runner_module.count_assert_statements(content) == 1
    assert runner_module.detect_targets_only_import(content) is True
    assert runner_module.detect_fixtures_import(content) is False


def test_runner_static_analysis_detects_fixtures_import() -> None:
    """Verify that the runner flags generated files importing internal fixtures."""

    runner_module = load_module_from_path("ise26_runner_fixture_detection", RUNNER_SCRIPT_PATH)
    content = (
        "from tests.fixtures import customer_names_dirty_df\n"
        "from ise26.targets import clean_customer_names\n"
        "\n"
        "def test_clean_customer_names():\n"
        "    assert True\n"
    )

    assert runner_module.detect_fixtures_import(content) is True
    assert runner_module.detect_targets_only_import(content) is False


def test_summary_metrics_distinguish_reliable_detection_from_false_positive() -> None:
    """Verify that the summaries separate contaminated suites from reliable ones."""

    summarize_module = load_module_from_path("ise26_summary_metrics", PROJECT_ROOT / "scripts" / "summarize_results.py")
    raw_results = pd.DataFrame(
        [
            {
                "function_id": "F01",
                "run_id": "run_01",
                "test_file": "experiments/generated_tests/F01/run_01/test_generated.py",
                "test_file_status": "ready",
                "suite_generation_status": "ready",
                "suite_is_real_generated": True,
                "suite_is_placeholder": False,
                "target_type": "correct",
                "target_module": "ise26.implementations.correct",
                "bug_id": "",
                "exit_code": 1,
                "passed": False,
                "stdout": "",
                "stderr": "",
                "duration_seconds": 0.1,
                "executable": True,
                "collected_tests": 3,
                "bug_failure": False,
                "correct_passed_for_same_suite": False,
                "reliable_defect_detection": False,
                "false_positive": True,
                "contaminated_bug_failure": False,
                "failure_detected": False,
                "generated_line_count": 10,
                "generated_test_function_count": 2,
                "generated_assert_count": 3,
                "imports_tests_fixtures": False,
                "imports_only_ise26_targets": True,
            },
            {
                "function_id": "F01",
                "run_id": "run_01",
                "test_file": "experiments/generated_tests/F01/run_01/test_generated.py",
                "test_file_status": "ready",
                "suite_generation_status": "ready",
                "suite_is_real_generated": True,
                "suite_is_placeholder": False,
                "target_type": "buggy",
                "target_module": "ise26.implementations.buggy.f01_bug01",
                "bug_id": "BUG01",
                "exit_code": 1,
                "passed": False,
                "stdout": "",
                "stderr": "",
                "duration_seconds": 0.1,
                "executable": True,
                "collected_tests": 3,
                "bug_failure": True,
                "correct_passed_for_same_suite": False,
                "reliable_defect_detection": False,
                "false_positive": True,
                "contaminated_bug_failure": True,
                "failure_detected": True,
                "generated_line_count": 10,
                "generated_test_function_count": 2,
                "generated_assert_count": 3,
                "imports_tests_fixtures": False,
                "imports_only_ise26_targets": True,
            },
        ]
    )

    prepared_results = summarize_module.prepare_raw_results(raw_results)
    run_summary = summarize_module.compute_run_level_metrics(prepared_results)
    overall_summary = summarize_module.compute_overall_metrics(prepared_results, run_summary)

    assert run_summary.loc[0, "bug_failure_rate"] == 1.0
    assert run_summary.loc[0, "reliable_defect_detection_rate"] == 0.0
    assert run_summary.loc[0, "false_positive_rate"] == 1.0
    assert run_summary.loc[0, "contaminated_bug_failure_count"] == 1
    assert overall_summary.loc[0, "reliable_defect_detection_rate"] == 0.0
    assert overall_summary.loc[0, "false_positive_rate"] == 1.0

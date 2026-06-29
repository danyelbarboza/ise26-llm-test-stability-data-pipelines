"""Tests for the DeepSeek integration scaffold without real API calls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

from ise26.llm.code_extraction import extract_python_code
from ise26.llm.deepseek_client import require_api_key
from ise26.llm.prompt_builder import build_prompt_bundle
from ise26.llm.reproducibility import compute_json_hash, compute_text_hash, load_json_configuration


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

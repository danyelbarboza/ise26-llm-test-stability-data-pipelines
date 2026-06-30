"""Tests that isolate Flash and Pro model paths in the multi-model setup."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATE_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_llm_tests.py"
RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_generated_tests.py"
SUMMARY_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "summarize_results.py"
COMPARE_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compare_model_results.py"


def load_module_from_path(module_name: str, path: Path):
    """Load a Python module directly from a file path."""

    specification = importlib.util.spec_from_file_location(module_name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_flash_manifest_and_pro_manifest_are_separate() -> None:
    """Verify that Flash and Pro keep independent manifest files."""

    flash_manifest = PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_flash" / "manifest.csv"
    pro_manifest = PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_pro" / "manifest.csv"

    assert flash_manifest.exists()
    assert pro_manifest.exists()
    assert sum(1 for _ in flash_manifest.open(encoding="utf-8")) > 1
    assert sum(1 for _ in pro_manifest.open(encoding="utf-8")) > 1
    assert flash_manifest.parent != pro_manifest.parent


def test_generate_script_uses_flash_directory(monkeypatch) -> None:
    """Verify that the Flash config resolves to the Flash generated-tests tree."""

    generate_module = load_module_from_path("ise26_generate_flash_isolation", GENERATE_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_build_generation_plan(function_id, run_id, generated_tests_root):
        captured["generated_tests_root"] = generated_tests_root
        return []

    monkeypatch.setattr(generate_module, "build_generation_plan", fake_build_generation_plan)
    result = generate_module.main(["--dry-run", "--config", str(PROJECT_ROOT / "experiments" / "config" / "deepseek_v4_flash.json")])

    assert result == 0
    assert captured["generated_tests_root"] == PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_flash"


def test_generate_script_uses_pro_directory(monkeypatch) -> None:
    """Verify that the Pro config resolves to the Pro generated-tests tree."""

    generate_module = load_module_from_path("ise26_generate_pro_isolation", GENERATE_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_build_generation_plan(function_id, run_id, generated_tests_root):
        captured["generated_tests_root"] = generated_tests_root
        return []

    monkeypatch.setattr(generate_module, "build_generation_plan", fake_build_generation_plan)
    result = generate_module.main(["--dry-run", "--config", str(PROJECT_ROOT / "experiments" / "config" / "deepseek_v4_pro.json")])

    assert result == 0
    assert captured["generated_tests_root"] == PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_pro"


def test_runner_uses_flash_directory(monkeypatch) -> None:
    """Verify that the Flash runner reads and writes only Flash paths."""

    runner_module = load_module_from_path("ise26_runner_flash_isolation", RUNNER_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_collect_execution_rows(generated_tests_root=None):
        captured["generated_tests_root"] = generated_tests_root
        return []

    def fake_write_results_csv(rows, raw_results_path=None):
        captured["raw_results_path"] = raw_results_path

    def fake_print_execution_summary(rows, raw_results_path=None):
        captured["summary_path"] = raw_results_path

    monkeypatch.setattr(runner_module, "collect_execution_rows", fake_collect_execution_rows)
    monkeypatch.setattr(runner_module, "write_results_csv", fake_write_results_csv)
    monkeypatch.setattr(runner_module, "print_execution_summary", fake_print_execution_summary)

    result = runner_module.main(["--model", "deepseek_v4_flash"])

    assert result == 0
    assert captured["generated_tests_root"] == PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_flash"
    assert captured["raw_results_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_flash" / "raw" / "generated_tests_results.csv"
    assert captured["summary_path"] == captured["raw_results_path"]


def test_runner_uses_pro_directory(monkeypatch) -> None:
    """Verify that the Pro runner reads and writes only Pro paths."""

    runner_module = load_module_from_path("ise26_runner_pro_isolation", RUNNER_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_collect_execution_rows(generated_tests_root=None):
        captured["generated_tests_root"] = generated_tests_root
        return []

    def fake_write_results_csv(rows, raw_results_path=None):
        captured["raw_results_path"] = raw_results_path

    def fake_print_execution_summary(rows, raw_results_path=None):
        captured["summary_path"] = raw_results_path

    monkeypatch.setattr(runner_module, "collect_execution_rows", fake_collect_execution_rows)
    monkeypatch.setattr(runner_module, "write_results_csv", fake_write_results_csv)
    monkeypatch.setattr(runner_module, "print_execution_summary", fake_print_execution_summary)

    result = runner_module.main(["--model", "deepseek_v4_pro"])

    assert result == 0
    assert captured["generated_tests_root"] == PROJECT_ROOT / "experiments" / "generated_tests" / "deepseek_v4_pro"
    assert captured["raw_results_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_pro" / "raw" / "generated_tests_results.csv"
    assert captured["summary_path"] == captured["raw_results_path"]


def test_summary_uses_flash_directory(monkeypatch) -> None:
    """Verify that Flash summaries are written only inside the Flash results tree."""

    summary_module = load_module_from_path("ise26_summary_flash_isolation", SUMMARY_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_load_raw_results(raw_results_path=None):
        captured["raw_results_path"] = raw_results_path
        return pd.DataFrame()

    def fake_write_summary_outputs(function_summary, run_summary, overall_summary, *, summary_by_function_path=None, summary_by_run_path=None, summary_overall_path=None):
        captured["summary_by_function_path"] = summary_by_function_path
        captured["summary_by_run_path"] = summary_by_run_path
        captured["summary_overall_path"] = summary_overall_path

    def fake_print_summary_locations(*, summary_by_function_path=None, summary_by_run_path=None, summary_overall_path=None):
        captured["printed_summary_by_function_path"] = summary_by_function_path
        captured["printed_summary_by_run_path"] = summary_by_run_path
        captured["printed_summary_overall_path"] = summary_overall_path

    monkeypatch.setattr(summary_module, "load_raw_results", fake_load_raw_results)
    monkeypatch.setattr(summary_module, "write_summary_outputs", fake_write_summary_outputs)
    monkeypatch.setattr(summary_module, "print_summary_locations", fake_print_summary_locations)

    result = summary_module.main(["--model", "deepseek_v4_flash"])

    assert result == 0
    assert captured["raw_results_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_flash" / "raw" / "generated_tests_results.csv"
    assert captured["summary_by_function_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_flash" / "summary" / "summary_by_function.csv"
    assert captured["summary_by_run_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_flash" / "summary" / "summary_by_run.csv"
    assert captured["summary_overall_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_flash" / "summary" / "summary_overall.csv"


def test_summary_uses_pro_directory(monkeypatch) -> None:
    """Verify that Pro summaries are written only inside the Pro results tree."""

    summary_module = load_module_from_path("ise26_summary_pro_isolation", SUMMARY_SCRIPT_PATH)
    captured: dict[str, Path] = {}

    def fake_load_raw_results(raw_results_path=None):
        captured["raw_results_path"] = raw_results_path
        return pd.DataFrame()

    def fake_write_summary_outputs(function_summary, run_summary, overall_summary, *, summary_by_function_path=None, summary_by_run_path=None, summary_overall_path=None):
        captured["summary_by_function_path"] = summary_by_function_path
        captured["summary_by_run_path"] = summary_by_run_path
        captured["summary_overall_path"] = summary_overall_path

    def fake_print_summary_locations(*, summary_by_function_path=None, summary_by_run_path=None, summary_overall_path=None):
        captured["printed_summary_by_function_path"] = summary_by_function_path
        captured["printed_summary_by_run_path"] = summary_by_run_path
        captured["printed_summary_overall_path"] = summary_overall_path

    monkeypatch.setattr(summary_module, "load_raw_results", fake_load_raw_results)
    monkeypatch.setattr(summary_module, "write_summary_outputs", fake_write_summary_outputs)
    monkeypatch.setattr(summary_module, "print_summary_locations", fake_print_summary_locations)

    result = summary_module.main(["--model", "deepseek_v4_pro"])

    assert result == 0
    assert captured["raw_results_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_pro" / "raw" / "generated_tests_results.csv"
    assert captured["summary_by_function_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_pro" / "summary" / "summary_by_function.csv"
    assert captured["summary_by_run_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_pro" / "summary" / "summary_by_run.csv"
    assert captured["summary_overall_path"] == PROJECT_ROOT / "results" / "by_model" / "deepseek_v4_pro" / "summary" / "summary_overall.csv"


def test_comparison_is_controlled_when_pro_only_has_placeholders(monkeypatch, tmp_path: Path, capsys) -> None:
    """Verify that the comparison script refuses to invent a Pro comparison."""

    compare_module = load_module_from_path("ise26_compare_model_results", COMPARE_SCRIPT_PATH)

    flash_root = tmp_path / "results" / "by_model" / "deepseek_v4_flash"
    pro_root = tmp_path / "results" / "by_model" / "deepseek_v4_pro"
    for root in [
        flash_root / "summary",
        pro_root / "summary",
    ]:
        root.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {
                "executability_rate": 1.0,
                "correct_pass_rate": 0.41379310344827586,
                "bug_failure_rate": 1.0,
                "defect_detection_rate_raw": 1.0,
                "reliable_defect_detection_rate": 0.41379310344827586,
                "false_positive_rate": 0.5862068965517241,
                "contaminated_bug_failure_rate": 0.5862068965517241,
                "real_suite_count": 29,
                "placeholder_suite_count": 0,
                "target_executions": 120,
                "real_target_executions": 116,
            }
        ]
    ).to_csv(flash_root / "summary" / "summary_overall.csv", index=False)
    pd.DataFrame(
        [
            {
                "executability_rate": 0.0,
                "correct_pass_rate": 0.0,
                "bug_failure_rate": 0.0,
                "defect_detection_rate_raw": 0.0,
                "reliable_defect_detection_rate": 0.0,
                "false_positive_rate": 0.0,
                "contaminated_bug_failure_rate": 0.0,
                "real_suite_count": 0,
                "placeholder_suite_count": 30,
                "target_executions": 120,
                "real_target_executions": 0,
            }
        ]
    ).to_csv(pro_root / "summary" / "summary_overall.csv", index=False)
    pd.DataFrame([{"function_id": "F01", "correct_pass_rate": 0.4}]).to_csv(
        flash_root / "summary" / "summary_by_function.csv",
        index=False,
    )
    pd.DataFrame([{"function_id": "F01", "correct_pass_rate": 0.0}]).to_csv(
        pro_root / "summary" / "summary_by_function.csv",
        index=False,
    )

    monkeypatch.setattr(
        compare_module,
        "resolve_results_root",
        lambda model_name: flash_root if model_name == "deepseek_v4_flash" else pro_root,
    )

    exit_code = compare_module.compare_models("deepseek_v4_flash", "deepseek_v4_pro", tmp_path / "comparison")
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Comparison unavailable: no official results found for deepseek_v4_pro." in captured.out
    assert not (tmp_path / "comparison" / "model_overall_comparison.csv").exists()
    assert not (tmp_path / "comparison" / "model_by_function_comparison.csv").exists()

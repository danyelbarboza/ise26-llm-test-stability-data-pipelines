"""Summarize raw generated-test execution results into CSV reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ise26.experiment_paths import resolve_results_root


DEFAULT_MODEL_NAME = "deepseek_v4_flash"
RAW_RESULTS_PATH = resolve_results_root(DEFAULT_MODEL_NAME) / "raw" / "generated_tests_results.csv"
SUMMARY_BY_FUNCTION_PATH = resolve_results_root(DEFAULT_MODEL_NAME) / "summary" / "summary_by_function.csv"
SUMMARY_BY_RUN_PATH = resolve_results_root(DEFAULT_MODEL_NAME) / "summary" / "summary_by_run.csv"
SUMMARY_OVERALL_PATH = resolve_results_root(DEFAULT_MODEL_NAME) / "summary" / "summary_overall.csv"

BOOLEAN_COLUMNS = [
    "passed",
    "executable",
    "failure_detected",
    "bug_failure",
    "correct_passed_for_same_suite",
    "reliable_defect_detection",
    "false_positive",
    "contaminated_bug_failure",
    "suite_is_real_generated",
    "suite_is_placeholder",
    "imports_tests_fixtures",
    "imports_only_ise26_targets",
]

NUMERIC_COLUMNS = [
    "duration_seconds",
    "collected_tests",
    "generated_line_count",
    "generated_test_function_count",
    "generated_assert_count",
]

RUN_SUMMARY_COLUMNS = [
    "function_id",
    "run_id",
    "suite_generation_status",
    "suite_is_real_generated",
    "suite_is_placeholder",
    "suite_count",
    "real_suite_count",
    "placeholder_suite_count",
    "target_executions",
    "real_target_executions",
    "placeholder_target_executions",
    "correct_target_executions",
    "bug_target_executions",
    "executability_rate",
    "correct_pass_rate",
    "bug_failure_rate",
    "defect_detection_rate_raw",
    "reliable_defect_detection_rate",
    "false_positive_rate",
    "contaminated_bug_failure_rate",
    "failure_count",
    "bug_failure_count",
    "reliable_defect_detection_count",
    "false_positive_count",
    "contaminated_bug_failure_count",
    "correct_passed_for_same_suite_count",
    "generated_line_count",
    "generated_test_function_count",
    "generated_assert_count",
    "imports_tests_fixtures",
    "imports_only_ise26_targets",
]

FUNCTION_SUMMARY_COLUMNS = [
    "function_id",
    "suite_count",
    "real_suite_count",
    "placeholder_suite_count",
    "target_executions",
    "real_target_executions",
    "placeholder_target_executions",
    "correct_target_executions",
    "bug_target_executions",
    "executability_rate",
    "correct_pass_rate",
    "bug_failure_rate",
    "defect_detection_rate_raw",
    "reliable_defect_detection_rate",
    "false_positive_rate",
    "contaminated_bug_failure_rate",
    "failure_count",
    "bug_failure_count",
    "reliable_defect_detection_count",
    "false_positive_count",
    "contaminated_bug_failure_count",
    "correct_passed_for_same_suite_count",
    "run_count",
    "correct_pass_rate_range",
    "bug_failure_rate_range",
    "defect_detection_rate_raw_range",
    "reliable_defect_detection_rate_range",
    "false_positive_rate_range",
    "contaminated_bug_failure_rate_range",
    "executability_rate_range",
    "generated_line_count_mean",
    "generated_test_function_count_mean",
    "generated_assert_count_mean",
    "imports_tests_fixtures_rate",
    "imports_only_ise26_targets_rate",
]

OVERALL_SUMMARY_COLUMNS = [
    "executability_rate",
    "correct_pass_rate",
    "bug_failure_rate",
    "defect_detection_rate_raw",
    "reliable_defect_detection_rate",
    "false_positive_rate",
    "contaminated_bug_failure_rate",
    "failure_count",
    "bug_failure_count",
    "reliable_defect_detection_count",
    "false_positive_count",
    "contaminated_bug_failure_count",
    "correct_passed_for_same_suite_count",
    "suite_count",
    "real_suite_count",
    "placeholder_suite_count",
    "target_executions",
    "real_target_executions",
    "placeholder_target_executions",
    "correct_target_executions",
    "bug_target_executions",
    "function_count",
    "run_label_count",
    "function_run_count",
    "correct_pass_rate_range_across_runs",
    "bug_failure_rate_range_across_runs",
    "defect_detection_rate_raw_range_across_runs",
    "reliable_defect_detection_rate_range_across_runs",
    "false_positive_rate_range_across_runs",
    "contaminated_bug_failure_rate_range_across_runs",
    "executability_rate_range_across_runs",
    "generated_line_count_mean",
    "generated_test_function_count_mean",
    "generated_assert_count_mean",
    "imports_tests_fixtures_rate",
    "imports_only_ise26_targets_rate",
]


def ensure_summary_directory(summary_directory: Path | None = None) -> None:
    """Ensure that the summary output directory exists."""

    target_directory = summary_directory or SUMMARY_BY_FUNCTION_PATH.parent
    target_directory.mkdir(parents=True, exist_ok=True)


def build_empty_summary_frame(columns: list[str]) -> pd.DataFrame:
    """Create an empty DataFrame with a predefined column order.

    Args:
        columns: Column names for the empty DataFrame.

    Returns:
        An empty DataFrame using the requested columns.
    """

    return pd.DataFrame(columns=columns)


def normalize_boolean_column(series: pd.Series) -> pd.Series:
    """Normalize a possibly mixed boolean-like column into actual booleans.

    Args:
        series: Input Series that may contain strings, numbers, or booleans.

    Returns:
        A boolean Series.
    """

    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
        .fillna(False)
        .astype(bool)
    )


def prepare_raw_results(raw_results: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw CSV columns so the aggregations stay predictable."""

    if raw_results.empty:
        return raw_results

    prepared = raw_results.copy()

    if "bug_failure" not in prepared.columns and "failure_detected" in prepared.columns:
        prepared["bug_failure"] = prepared["failure_detected"]
    if "failure_detected" not in prepared.columns and "bug_failure" in prepared.columns:
        prepared["failure_detected"] = prepared["bug_failure"]

    default_boolean_columns = {
        "passed": False,
        "executable": False,
        "failure_detected": False,
        "bug_failure": False,
        "correct_passed_for_same_suite": False,
        "reliable_defect_detection": False,
        "false_positive": False,
        "contaminated_bug_failure": False,
        "suite_is_real_generated": False,
        "suite_is_placeholder": False,
        "imports_tests_fixtures": False,
        "imports_only_ise26_targets": False,
    }
    for column_name, default_value in default_boolean_columns.items():
        if column_name not in prepared.columns:
            prepared[column_name] = default_value

    default_numeric_columns = {
        "generated_line_count": 0,
        "generated_test_function_count": 0,
        "generated_assert_count": 0,
    }
    for column_name, default_value in default_numeric_columns.items():
        if column_name not in prepared.columns:
            prepared[column_name] = default_value

    for column_name in BOOLEAN_COLUMNS:
        if column_name in prepared.columns:
            prepared[column_name] = normalize_boolean_column(prepared[column_name])

    for column_name in NUMERIC_COLUMNS:
        if column_name in prepared.columns:
            prepared[column_name] = pd.to_numeric(prepared[column_name], errors="coerce").fillna(0.0)

    prepared["duration_seconds"] = pd.to_numeric(prepared["duration_seconds"], errors="coerce").fillna(0.0)
    prepared["collected_tests"] = pd.to_numeric(prepared["collected_tests"], errors="coerce")

    if "suite_generation_status" not in prepared.columns:
        prepared["suite_generation_status"] = prepared["test_file_status"]

    return prepared


def load_raw_results(raw_results_path: Path | None = None) -> pd.DataFrame:
    """Load raw execution results and normalize key analysis columns.

    Returns:
        A DataFrame ready for aggregation. Missing files yield an empty frame.
    """

    target_path = raw_results_path or RAW_RESULTS_PATH
    if not target_path.exists():
        return pd.DataFrame()

    raw_results = pd.read_csv(target_path)
    if raw_results.empty:
        return raw_results

    return prepare_raw_results(raw_results)


def mean_or_zero(series: pd.Series) -> float:
    """Return the mean of a series or ``0.0`` when it is empty."""

    if series.empty:
        return 0.0
    return float(series.mean())


def count_unique_suites(frame: pd.DataFrame) -> int:
    """Count unique function/run pairs inside a DataFrame."""

    if frame.empty:
        return 0
    return int(frame[["function_id", "run_id"]].drop_duplicates().shape[0])


def summarize_suite_group(group: pd.DataFrame) -> dict[str, object]:
    """Summarize one function/run execution group into a single row."""

    real_rows = group[group["suite_is_real_generated"]]
    placeholder_rows = group[group["suite_is_placeholder"]]
    correct_rows = real_rows[real_rows["target_type"] == "correct"]
    bug_rows = real_rows[real_rows["target_type"] == "buggy"]

    suite_generation_status = str(group["suite_generation_status"].iloc[0]) if not group.empty else ""
    suite_is_real_generated = bool(real_rows.shape[0])
    suite_is_placeholder = bool(placeholder_rows.shape[0])
    correct_passed_for_same_suite = bool(not correct_rows.empty and bool(correct_rows["passed"].iloc[0]))
    false_positive = bool(suite_is_real_generated and not correct_passed_for_same_suite)

    return {
        "function_id": str(group["function_id"].iloc[0]),
        "run_id": str(group["run_id"].iloc[0]),
        "suite_generation_status": suite_generation_status,
        "suite_is_real_generated": suite_is_real_generated,
        "suite_is_placeholder": suite_is_placeholder,
        "suite_count": 1,
        "real_suite_count": int(suite_is_real_generated),
        "placeholder_suite_count": int(suite_is_placeholder),
        "target_executions": int(len(group)),
        "real_target_executions": int(len(real_rows)),
        "placeholder_target_executions": int(len(placeholder_rows)),
        "correct_target_executions": int(len(correct_rows)),
        "bug_target_executions": int(len(bug_rows)),
        "executability_rate": mean_or_zero(real_rows["executable"]),
        "correct_pass_rate": mean_or_zero(correct_rows["passed"]),
        "bug_failure_rate": mean_or_zero(bug_rows["bug_failure"]),
        "defect_detection_rate_raw": mean_or_zero(bug_rows["bug_failure"]),
        "reliable_defect_detection_rate": mean_or_zero(bug_rows["reliable_defect_detection"]),
        "false_positive_rate": mean_or_zero(correct_rows["false_positive"]),
        "contaminated_bug_failure_rate": mean_or_zero(bug_rows["contaminated_bug_failure"]),
        "failure_count": int((real_rows["executable"] & ~real_rows["passed"]).sum()),
        "bug_failure_count": int(bug_rows["bug_failure"].sum()),
        "reliable_defect_detection_count": int(bug_rows["reliable_defect_detection"].sum()),
        "false_positive_count": int(correct_rows["false_positive"].sum()),
        "contaminated_bug_failure_count": int(bug_rows["contaminated_bug_failure"].sum()),
        "correct_passed_for_same_suite_count": int(correct_passed_for_same_suite),
        "generated_line_count": int(real_rows["generated_line_count"].max()) if not real_rows.empty else 0,
        "generated_test_function_count": int(real_rows["generated_test_function_count"].max()) if not real_rows.empty else 0,
        "generated_assert_count": int(real_rows["generated_assert_count"].max()) if not real_rows.empty else 0,
        "imports_tests_fixtures": bool(real_rows["imports_tests_fixtures"].any()) if not real_rows.empty else False,
        "imports_only_ise26_targets": bool(real_rows["imports_only_ise26_targets"].any()) if not real_rows.empty else False,
    }


def aggregate_suite_summary(group: pd.DataFrame, *, include_function_id: bool = False) -> dict[str, object]:
    """Aggregate suite-level rows into function-level or overall metrics."""

    real_rows = group[group["suite_is_real_generated"]]
    placeholder_rows = group[group["suite_is_placeholder"]]

    summary: dict[str, object] = {
        "suite_count": int(len(group)),
        "real_suite_count": int(real_rows["suite_count"].sum()) if not real_rows.empty else 0,
        "placeholder_suite_count": int(placeholder_rows["suite_count"].sum()) if not placeholder_rows.empty else 0,
        "target_executions": int(group["target_executions"].sum()),
        "real_target_executions": int(real_rows["real_target_executions"].sum()) if not real_rows.empty else 0,
        "placeholder_target_executions": int(placeholder_rows["placeholder_target_executions"].sum()) if not placeholder_rows.empty else 0,
        "correct_target_executions": int(real_rows["correct_target_executions"].sum()) if not real_rows.empty else 0,
        "bug_target_executions": int(real_rows["bug_target_executions"].sum()) if not real_rows.empty else 0,
        "executability_rate": mean_or_zero(real_rows["executability_rate"]),
        "correct_pass_rate": mean_or_zero(real_rows["correct_pass_rate"]),
        "bug_failure_rate": mean_or_zero(real_rows["bug_failure_rate"]),
        "defect_detection_rate_raw": mean_or_zero(real_rows["defect_detection_rate_raw"]),
        "reliable_defect_detection_rate": mean_or_zero(real_rows["reliable_defect_detection_rate"]),
        "false_positive_rate": mean_or_zero(real_rows["false_positive_rate"]),
        "contaminated_bug_failure_rate": mean_or_zero(real_rows["contaminated_bug_failure_rate"]),
        "failure_count": int(real_rows["failure_count"].sum()) if not real_rows.empty else 0,
        "bug_failure_count": int(real_rows["bug_failure_count"].sum()) if not real_rows.empty else 0,
        "reliable_defect_detection_count": int(real_rows["reliable_defect_detection_count"].sum()) if not real_rows.empty else 0,
        "false_positive_count": int(real_rows["false_positive_count"].sum()) if not real_rows.empty else 0,
        "contaminated_bug_failure_count": int(real_rows["contaminated_bug_failure_count"].sum()) if not real_rows.empty else 0,
        "correct_passed_for_same_suite_count": int(real_rows["correct_passed_for_same_suite_count"].sum()) if not real_rows.empty else 0,
        "run_count": int(group["run_id"].nunique()),
        "correct_pass_rate_range": float(real_rows["correct_pass_rate"].max() - real_rows["correct_pass_rate"].min()) if len(real_rows) > 1 else 0.0,
        "bug_failure_rate_range": float(real_rows["bug_failure_rate"].max() - real_rows["bug_failure_rate"].min()) if len(real_rows) > 1 else 0.0,
        "defect_detection_rate_raw_range": float(real_rows["defect_detection_rate_raw"].max() - real_rows["defect_detection_rate_raw"].min()) if len(real_rows) > 1 else 0.0,
        "reliable_defect_detection_rate_range": float(real_rows["reliable_defect_detection_rate"].max() - real_rows["reliable_defect_detection_rate"].min()) if len(real_rows) > 1 else 0.0,
        "false_positive_rate_range": float(real_rows["false_positive_rate"].max() - real_rows["false_positive_rate"].min()) if len(real_rows) > 1 else 0.0,
        "contaminated_bug_failure_rate_range": float(real_rows["contaminated_bug_failure_rate"].max() - real_rows["contaminated_bug_failure_rate"].min()) if len(real_rows) > 1 else 0.0,
        "executability_rate_range": float(real_rows["executability_rate"].max() - real_rows["executability_rate"].min()) if len(real_rows) > 1 else 0.0,
        "generated_line_count_mean": mean_or_zero(real_rows["generated_line_count"]),
        "generated_test_function_count_mean": mean_or_zero(real_rows["generated_test_function_count"]),
        "generated_assert_count_mean": mean_or_zero(real_rows["generated_assert_count"]),
        "imports_tests_fixtures_rate": mean_or_zero(real_rows["imports_tests_fixtures"].astype(float)),
        "imports_only_ise26_targets_rate": mean_or_zero(real_rows["imports_only_ise26_targets"].astype(float)),
    }

    if include_function_id:
        summary["function_id"] = str(group["function_id"].iloc[0])

    return summary


def compute_run_level_metrics(raw_results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate execution results by function and run identifier.

    Args:
        raw_results: Normalized raw results DataFrame.

    Returns:
        A run-level summary DataFrame.
    """

    if raw_results.empty:
        return build_empty_summary_frame(RUN_SUMMARY_COLUMNS)

    grouped_rows = [
        summarize_suite_group(group)
        for _, group in raw_results.groupby(["function_id", "run_id"], sort=True)
    ]

    return pd.DataFrame(grouped_rows, columns=RUN_SUMMARY_COLUMNS).sort_values(["function_id", "run_id"]).reset_index(drop=True)


def compute_function_level_metrics(
    raw_results: pd.DataFrame, run_summary: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate execution results by function identifier.

    Args:
        raw_results: Normalized raw results DataFrame.
        run_summary: Run-level summary used to compute between-run variation.

    Returns:
        A function-level summary DataFrame.
    """

    if raw_results.empty or run_summary.empty:
        return build_empty_summary_frame(FUNCTION_SUMMARY_COLUMNS)

    grouped_rows = [
        aggregate_suite_summary(group, include_function_id=True)
        for _, group in run_summary.groupby("function_id", sort=True)
    ]

    return pd.DataFrame(grouped_rows, columns=FUNCTION_SUMMARY_COLUMNS).sort_values("function_id").reset_index(drop=True)


def compute_overall_metrics(raw_results: pd.DataFrame, run_summary: pd.DataFrame) -> pd.DataFrame:
    """Aggregate execution results into a single overall summary row.

    Args:
        raw_results: Normalized raw results DataFrame.
        run_summary: Run-level summary used to compute overall variation.

    Returns:
        A one-row overall summary DataFrame.
    """

    if raw_results.empty or run_summary.empty:
        return build_empty_summary_frame(OVERALL_SUMMARY_COLUMNS)

    overall_row = aggregate_suite_summary(run_summary)
    overall_row["function_count"] = int(run_summary["function_id"].nunique())
    overall_row["run_label_count"] = int(run_summary["run_id"].nunique())
    overall_row["function_run_count"] = count_unique_suites(run_summary)

    real_rows = run_summary[run_summary["suite_is_real_generated"]]
    overall_row["correct_pass_rate_range_across_runs"] = (
        float(real_rows["correct_pass_rate"].max() - real_rows["correct_pass_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["bug_failure_rate_range_across_runs"] = (
        float(real_rows["bug_failure_rate"].max() - real_rows["bug_failure_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["defect_detection_rate_raw_range_across_runs"] = (
        float(real_rows["defect_detection_rate_raw"].max() - real_rows["defect_detection_rate_raw"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["reliable_defect_detection_rate_range_across_runs"] = (
        float(real_rows["reliable_defect_detection_rate"].max() - real_rows["reliable_defect_detection_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["false_positive_rate_range_across_runs"] = (
        float(real_rows["false_positive_rate"].max() - real_rows["false_positive_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["contaminated_bug_failure_rate_range_across_runs"] = (
        float(real_rows["contaminated_bug_failure_rate"].max() - real_rows["contaminated_bug_failure_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["executability_rate_range_across_runs"] = (
        float(real_rows["executability_rate"].max() - real_rows["executability_rate"].min())
        if len(real_rows) > 1
        else 0.0
    )
    overall_row["generated_line_count_mean"] = mean_or_zero(real_rows["generated_line_count"])
    overall_row["generated_test_function_count_mean"] = mean_or_zero(real_rows["generated_test_function_count"])
    overall_row["generated_assert_count_mean"] = mean_or_zero(real_rows["generated_assert_count"])
    overall_row["imports_tests_fixtures_rate"] = mean_or_zero(real_rows["imports_tests_fixtures"].astype(float))
    overall_row["imports_only_ise26_targets_rate"] = mean_or_zero(real_rows["imports_only_ise26_targets"].astype(float))

    return pd.DataFrame([overall_row], columns=OVERALL_SUMMARY_COLUMNS)


def write_summary_outputs(
    function_summary: pd.DataFrame,
    run_summary: pd.DataFrame,
    overall_summary: pd.DataFrame,
    *,
    summary_by_function_path: Path | None = None,
    summary_by_run_path: Path | None = None,
    summary_overall_path: Path | None = None,
) -> None:
    """Write the computed summary DataFrames to CSV files.

    Args:
        function_summary: Summary grouped by function.
        run_summary: Summary grouped by function and run.
        overall_summary: Overall summary row.
        summary_by_function_path: Optional destination for the function summary CSV.
        summary_by_run_path: Optional destination for the run summary CSV.
        summary_overall_path: Optional destination for the overall summary CSV.
    """

    function_summary.to_csv(summary_by_function_path or SUMMARY_BY_FUNCTION_PATH, index=False)
    run_summary.to_csv(summary_by_run_path or SUMMARY_BY_RUN_PATH, index=False)
    overall_summary.to_csv(summary_overall_path or SUMMARY_OVERALL_PATH, index=False)


def print_summary_locations(
    *,
    summary_by_function_path: Path | None = None,
    summary_by_run_path: Path | None = None,
    summary_overall_path: Path | None = None,
) -> None:
    """Print the output paths of the generated summary files."""

    print(f"Saved function summary to: {summary_by_function_path or SUMMARY_BY_FUNCTION_PATH}")
    print(f"Saved run summary to: {summary_by_run_path or SUMMARY_BY_RUN_PATH}")
    print(f"Saved overall summary to: {summary_overall_path or SUMMARY_OVERALL_PATH}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the summary workflow."""

    parser = argparse.ArgumentParser(description="Summarize generated-test results.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_NAME,
        help="Model key or model name used to resolve the raw-results and summary folders.",
    )
    parser.add_argument(
        "--experiment-id",
        help="Optional experiment identifier used to separate result folders.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional configuration file used to infer the model name.",
    )
    return parser.parse_args(argv)


def resolve_model_name(args: argparse.Namespace) -> str:
    """Resolve the target model name from CLI arguments."""

    if args.config is not None:
        with args.config.open("r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
        return str(config["model"])
    return str(args.model)


def resolve_experiment_id(args: argparse.Namespace) -> str | None:
    """Resolve the active experiment identifier from CLI or config settings."""

    config_experiment_id = None
    if args.config is not None:
        with args.config.open("r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
        config_experiment_id = str(config.get("experiment_id", "")).strip() or None

    cli_experiment_id = str(args.experiment_id).strip() if args.experiment_id else None

    if cli_experiment_id and config_experiment_id and cli_experiment_id != config_experiment_id:
        raise ValueError("The CLI experiment id does not match the configuration file.")

    return cli_experiment_id or config_experiment_id


def main(argv: list[str] | None = None) -> int:
    """Load raw results, compute summaries, and persist the CSV reports.

    Returns:
        Process exit code suitable for command-line usage.
    """

    args = parse_args(argv)
    model_name = resolve_model_name(args)
    experiment_id = resolve_experiment_id(args)
    results_root = resolve_results_root(model_name, experiment_id=experiment_id)
    raw_results_path = results_root / "raw" / "generated_tests_results.csv"
    summary_by_function_path = results_root / "summary" / "summary_by_function.csv"
    summary_by_run_path = results_root / "summary" / "summary_by_run.csv"
    summary_overall_path = results_root / "summary" / "summary_overall.csv"

    ensure_summary_directory(summary_by_function_path.parent)
    raw_results = load_raw_results(raw_results_path)
    run_summary = compute_run_level_metrics(raw_results)
    function_summary = compute_function_level_metrics(raw_results, run_summary)
    overall_summary = compute_overall_metrics(raw_results, run_summary)
    write_summary_outputs(
        function_summary,
        run_summary,
        overall_summary,
        summary_by_function_path=summary_by_function_path,
        summary_by_run_path=summary_by_run_path,
        summary_overall_path=summary_overall_path,
    )
    print_summary_locations(
        summary_by_function_path=summary_by_function_path,
        summary_by_run_path=summary_by_run_path,
        summary_overall_path=summary_overall_path,
    )

    if raw_results.empty:
        print("Raw results were empty or unavailable; empty summary files were created.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

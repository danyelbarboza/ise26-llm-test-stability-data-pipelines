"""Summarize raw generated-test execution results into CSV reports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_RESULTS_PATH = PROJECT_ROOT / "results" / "raw" / "generated_tests_results.csv"
SUMMARY_BY_FUNCTION_PATH = PROJECT_ROOT / "results" / "summary" / "summary_by_function.csv"
SUMMARY_BY_RUN_PATH = PROJECT_ROOT / "results" / "summary" / "summary_by_run.csv"
SUMMARY_OVERALL_PATH = PROJECT_ROOT / "results" / "summary" / "summary_overall.csv"


def ensure_summary_directory() -> None:
    """Ensure that the summary output directory exists."""

    SUMMARY_BY_FUNCTION_PATH.parent.mkdir(parents=True, exist_ok=True)


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


def load_raw_results() -> pd.DataFrame:
    """Load raw execution results and normalize key analysis columns.

    Returns:
        A DataFrame ready for aggregation. Missing files yield an empty frame.
    """

    if not RAW_RESULTS_PATH.exists():
        return pd.DataFrame()

    raw_results = pd.read_csv(RAW_RESULTS_PATH)
    if raw_results.empty:
        return raw_results

    # CSV values can arrive as strings when written by the runner. Normalizing
    # them here keeps the aggregation logic simple and predictable.
    raw_results["passed"] = normalize_boolean_column(raw_results["passed"])
    raw_results["executable"] = normalize_boolean_column(raw_results["executable"])
    raw_results["failure_detected"] = normalize_boolean_column(raw_results["failure_detected"])
    raw_results["duration_seconds"] = pd.to_numeric(raw_results["duration_seconds"], errors="coerce").fillna(0.0)
    raw_results["collected_tests"] = pd.to_numeric(raw_results["collected_tests"], errors="coerce")

    return raw_results


def compute_run_level_metrics(raw_results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate execution results by function and run identifier.

    Args:
        raw_results: Normalized raw results DataFrame.

    Returns:
        A run-level summary DataFrame.
    """

    if raw_results.empty:
        return build_empty_summary_frame(
            [
                "function_id",
                "run_id",
                "executability_rate",
                "correct_pass_rate",
                "defect_detection_rate",
                "failure_count",
                "target_executions",
                "executable_target_executions",
                "collected_tests_max",
            ]
        )

    grouped_rows: list[dict[str, object]] = []
    for (function_id, run_id), group in raw_results.groupby(["function_id", "run_id"], sort=True):
        correct_group = group[group["target_type"] == "correct"]
        buggy_group = group[group["target_type"] == "buggy"]

        # Run-level metrics summarize the outcome of one generated suite across
        # the four target modules associated with the same function.
        grouped_rows.append(
            {
                "function_id": function_id,
                "run_id": run_id,
                "executability_rate": group["executable"].mean(),
                "correct_pass_rate": correct_group["passed"].mean() if not correct_group.empty else 0.0,
                "defect_detection_rate": buggy_group["failure_detected"].mean() if not buggy_group.empty else 0.0,
                "failure_count": int((group["executable"] & ~group["passed"]).sum()),
                "target_executions": int(len(group)),
                "executable_target_executions": int(group["executable"].sum()),
                "collected_tests_max": int(group["collected_tests"].max()) if group["collected_tests"].notna().any() else 0,
            }
        )

    return pd.DataFrame(grouped_rows).sort_values(["function_id", "run_id"]).reset_index(drop=True)


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

    if raw_results.empty:
        return build_empty_summary_frame(
            [
                "function_id",
                "executability_rate",
                "correct_pass_rate",
                "defect_detection_rate",
                "failure_count",
                "target_executions",
                "run_count",
                "correct_pass_rate_range",
                "defect_detection_rate_range",
                "executability_rate_range",
            ]
        )

    grouped_rows: list[dict[str, object]] = []
    for function_id, group in raw_results.groupby("function_id", sort=True):
        function_runs = run_summary[run_summary["function_id"] == function_id]
        correct_group = group[group["target_type"] == "correct"]
        buggy_group = group[group["target_type"] == "buggy"]

        # The range fields capture cross-run variation, which is one of the
        # core study interests for generated test stability.
        grouped_rows.append(
            {
                "function_id": function_id,
                "executability_rate": group["executable"].mean(),
                "correct_pass_rate": correct_group["passed"].mean() if not correct_group.empty else 0.0,
                "defect_detection_rate": buggy_group["failure_detected"].mean() if not buggy_group.empty else 0.0,
                "failure_count": int((group["executable"] & ~group["passed"]).sum()),
                "target_executions": int(len(group)),
                "run_count": int(function_runs["run_id"].nunique()) if not function_runs.empty else 0,
                "correct_pass_rate_range": (
                    function_runs["correct_pass_rate"].max() - function_runs["correct_pass_rate"].min()
                    if not function_runs.empty
                    else 0.0
                ),
                "defect_detection_rate_range": (
                    function_runs["defect_detection_rate"].max() - function_runs["defect_detection_rate"].min()
                    if not function_runs.empty
                    else 0.0
                ),
                "executability_rate_range": (
                    function_runs["executability_rate"].max() - function_runs["executability_rate"].min()
                    if not function_runs.empty
                    else 0.0
                ),
            }
        )

    return pd.DataFrame(grouped_rows).sort_values("function_id").reset_index(drop=True)


def compute_overall_metrics(raw_results: pd.DataFrame, run_summary: pd.DataFrame) -> pd.DataFrame:
    """Aggregate execution results into a single overall summary row.

    Args:
        raw_results: Normalized raw results DataFrame.
        run_summary: Run-level summary used to compute overall variation.

    Returns:
        A one-row overall summary DataFrame.
    """

    if raw_results.empty:
        return build_empty_summary_frame(
            [
                "executability_rate",
                "correct_pass_rate",
                "defect_detection_rate",
                "failure_count",
                "target_executions",
                "function_count",
                "run_count",
                "correct_pass_rate_range_across_runs",
                "defect_detection_rate_range_across_runs",
                "executability_rate_range_across_runs",
            ]
        )

    correct_group = raw_results[raw_results["target_type"] == "correct"]
    buggy_group = raw_results[raw_results["target_type"] == "buggy"]

    # The overall view is intentionally compact so it can be inspected quickly
    # before moving into the more detailed per-function and per-run reports.
    overall_row = {
        "executability_rate": raw_results["executable"].mean(),
        "correct_pass_rate": correct_group["passed"].mean() if not correct_group.empty else 0.0,
        "defect_detection_rate": buggy_group["failure_detected"].mean() if not buggy_group.empty else 0.0,
        "failure_count": int((raw_results["executable"] & ~raw_results["passed"]).sum()),
        "target_executions": int(len(raw_results)),
        "function_count": int(raw_results["function_id"].nunique()),
        "function_run_count": int(run_summary[["function_id", "run_id"]].drop_duplicates().shape[0]) if not run_summary.empty else 0,
        "run_label_count": int(raw_results["run_id"].nunique()),
        "correct_pass_rate_range_across_runs": (
            run_summary["correct_pass_rate"].max() - run_summary["correct_pass_rate"].min()
            if not run_summary.empty
            else 0.0
        ),
        "defect_detection_rate_range_across_runs": (
            run_summary["defect_detection_rate"].max() - run_summary["defect_detection_rate"].min()
            if not run_summary.empty
            else 0.0
        ),
        "executability_rate_range_across_runs": (
            run_summary["executability_rate"].max() - run_summary["executability_rate"].min()
            if not run_summary.empty
            else 0.0
        ),
    }

    return pd.DataFrame([overall_row])


def write_summary_outputs(
    function_summary: pd.DataFrame,
    run_summary: pd.DataFrame,
    overall_summary: pd.DataFrame,
) -> None:
    """Write the computed summary DataFrames to CSV files.

    Args:
        function_summary: Summary grouped by function.
        run_summary: Summary grouped by function and run.
        overall_summary: Overall summary row.
    """

    function_summary.to_csv(SUMMARY_BY_FUNCTION_PATH, index=False)
    run_summary.to_csv(SUMMARY_BY_RUN_PATH, index=False)
    overall_summary.to_csv(SUMMARY_OVERALL_PATH, index=False)


def print_summary_locations() -> None:
    """Print the output paths of the generated summary files."""

    print(f"Saved function summary to: {SUMMARY_BY_FUNCTION_PATH}")
    print(f"Saved run summary to: {SUMMARY_BY_RUN_PATH}")
    print(f"Saved overall summary to: {SUMMARY_OVERALL_PATH}")


def main() -> int:
    """Load raw results, compute summaries, and persist the CSV reports.

    Returns:
        Process exit code suitable for command-line usage.
    """

    ensure_summary_directory()
    raw_results = load_raw_results()
    run_summary = compute_run_level_metrics(raw_results)
    function_summary = compute_function_level_metrics(raw_results, run_summary)
    overall_summary = compute_overall_metrics(raw_results, run_summary)
    write_summary_outputs(function_summary, run_summary, overall_summary)
    print_summary_locations()

    if raw_results.empty:
        print("Raw results were empty or unavailable; empty summary files were created.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

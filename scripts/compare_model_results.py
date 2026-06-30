"""Compare official results between DeepSeek models when both are available."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ise26.experiment_paths import resolve_results_root, resolve_comparison_root


DEFAULT_FLASH_MODEL = "deepseek_v4_flash"
DEFAULT_PRO_MODEL = "deepseek_v4_pro"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "paper_assets" / "model_comparison"

OVERALL_COLUMNS = [
    "metric",
    "deepseek_v4_flash",
    "deepseek_v4_pro",
    "difference_pro_minus_flash",
]

FUNCTION_COLUMNS = [
    "function_id",
    "metric",
    "deepseek_v4_flash",
    "deepseek_v4_pro",
    "difference_pro_minus_flash",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the comparison workflow."""

    parser = argparse.ArgumentParser(description="Compare model-level ISE26 results.")
    parser.add_argument("--flash-model", default=DEFAULT_FLASH_MODEL)
    parser.add_argument("--pro-model", default=DEFAULT_PRO_MODEL)
    parser.add_argument(
        "--experiment-id",
        help="Optional experiment identifier used to isolate comparison assets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where comparison tables will be written once both models exist.",
    )
    return parser.parse_args(argv)


def load_csv_if_available(path: Path) -> pd.DataFrame | None:
    """Load a CSV file when it exists and contains data."""

    if not path.exists():
        return None

    frame = pd.read_csv(path)
    if frame.empty:
        return None
    return frame


def load_overall_summary(model_name: str, experiment_id: str | None = None) -> pd.DataFrame | None:
    """Load the overall summary for one model."""

    if experiment_id is None:
        path = resolve_results_root(model_name) / "summary" / "summary_overall.csv"
    else:
        path = resolve_results_root(model_name, experiment_id) / "summary" / "summary_overall.csv"
    return load_csv_if_available(path)


def load_function_summary(model_name: str, experiment_id: str | None = None) -> pd.DataFrame | None:
    """Load the function summary for one model."""

    if experiment_id is None:
        path = resolve_results_root(model_name) / "summary" / "summary_by_function.csv"
    else:
        path = resolve_results_root(model_name, experiment_id) / "summary" / "summary_by_function.csv"
    return load_csv_if_available(path)


def has_real_results(overall_summary: pd.DataFrame | None) -> bool:
    """Return whether a summary contains real, non-placeholder experimental data."""

    if overall_summary is None or overall_summary.empty:
        return False

    if "real_suite_count" in overall_summary.columns:
        return int(overall_summary.iloc[0]["real_suite_count"]) > 0

    if "real_target_executions" in overall_summary.columns:
        return int(overall_summary.iloc[0]["real_target_executions"]) > 0

    return False


def build_overall_comparison(flash_summary: pd.DataFrame, pro_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a compact overall comparison table."""

    metrics = [
        "correct_pass_rate",
        "false_positive_rate",
        "bug_failure_rate",
        "defect_detection_rate_raw",
        "reliable_defect_detection_rate",
        "contaminated_bug_failure_rate",
        "real_suite_count",
        "placeholder_suite_count",
        "target_executions",
        "real_target_executions",
    ]

    rows: list[dict[str, Any]] = []
    flash_row = flash_summary.iloc[0]
    pro_row = pro_summary.iloc[0]
    for metric in metrics:
        flash_value = flash_row.get(metric, "")
        pro_value = pro_row.get(metric, "")
        try:
            difference = float(pro_value) - float(flash_value)
        except (TypeError, ValueError):
            difference = ""
        rows.append(
            {
                "metric": metric,
                "deepseek_v4_flash": flash_value,
                "deepseek_v4_pro": pro_value,
                "difference_pro_minus_flash": difference,
            }
        )

    return pd.DataFrame(rows, columns=OVERALL_COLUMNS)


def build_function_comparison(
    flash_functions: pd.DataFrame,
    pro_functions: pd.DataFrame,
) -> pd.DataFrame:
    """Build a function-level comparison table."""

    metrics = [
        "correct_pass_rate",
        "false_positive_rate",
        "reliable_defect_detection_rate",
        "contaminated_bug_failure_rate",
        "real_suite_count",
    ]

    flash_map = flash_functions.set_index("function_id")
    pro_map = pro_functions.set_index("function_id")
    common_functions = sorted(set(flash_map.index).intersection(set(pro_map.index)))
    rows: list[dict[str, Any]] = []

    for function_id in common_functions:
        flash_row = flash_map.loc[function_id]
        pro_row = pro_map.loc[function_id]
        for metric in metrics:
            flash_value = flash_row.get(metric, "")
            pro_value = pro_row.get(metric, "")
            try:
                difference = float(pro_value) - float(flash_value)
            except (TypeError, ValueError):
                difference = ""
            rows.append(
                {
                    "function_id": function_id,
                    "metric": metric,
                    "deepseek_v4_flash": flash_value,
                    "deepseek_v4_pro": pro_value,
                    "difference_pro_minus_flash": difference,
                }
            )

    return pd.DataFrame(rows, columns=FUNCTION_COLUMNS)


def write_markdown_table(frame: pd.DataFrame, path: Path, title: str) -> None:
    """Write a Markdown summary with a compact table."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(f"# {title}\n\n")
        if frame.empty:
            file_handle.write("No comparable official results are available yet.\n")
            return
        headers = list(frame.columns)
        file_handle.write("| " + " | ".join(headers) + " |\n")
        file_handle.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for _, row in frame.iterrows():
            values = [str(row.get(column, "")) for column in headers]
            file_handle.write("| " + " | ".join(values) + " |\n")


def compare_models(
    flash_model: str,
    pro_model: str,
    output_dir: Path,
    experiment_id: str | None = None,
) -> int:
    """Compare both models when their official results are available."""

    flash_overall = load_overall_summary(flash_model, experiment_id=experiment_id)
    pro_overall = load_overall_summary(pro_model, experiment_id=experiment_id)
    flash_functions = load_function_summary(flash_model, experiment_id=experiment_id)
    pro_functions = load_function_summary(pro_model, experiment_id=experiment_id)

    if not has_real_results(flash_overall):
        print(f"Comparison unavailable: no official results found for {flash_model}.")
        return 0

    if not has_real_results(pro_overall):
        print(f"Comparison unavailable: no official results found for {pro_model}.")
        return 0

    if flash_functions is None or pro_functions is None:
        print("Comparison unavailable: function summaries are missing.")
        return 0

    overall_comparison = build_overall_comparison(flash_overall, pro_overall)
    function_comparison = build_function_comparison(flash_functions, pro_functions)

    resolved_output_dir = output_dir
    if experiment_id:
        resolved_output_dir = resolve_comparison_root(experiment_id)

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    overall_csv = resolved_output_dir / "model_overall_comparison.csv"
    overall_md = resolved_output_dir / "model_overall_comparison.md"
    function_csv = resolved_output_dir / "model_by_function_comparison.csv"
    function_md = resolved_output_dir / "model_by_function_comparison.md"
    summary_md = resolved_output_dir / "model_comparison_summary.md"

    overall_comparison.to_csv(overall_csv, index=False)
    function_comparison.to_csv(function_csv, index=False)
    write_markdown_table(overall_comparison, overall_md, "Model overall comparison")
    write_markdown_table(function_comparison, function_md, "Model-by-function comparison")
    write_markdown_table(
        overall_comparison.head(1),
        summary_md,
        "Model comparison summary",
    )

    print(f"Saved overall comparison to: {overall_csv}")
    print(f"Saved function comparison to: {function_csv}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for the comparison workflow."""

    args = parse_args(argv)
    return compare_models(args.flash_model, args.pro_model, args.output_dir, experiment_id=args.experiment_id)


if __name__ == "__main__":
    raise SystemExit(main())

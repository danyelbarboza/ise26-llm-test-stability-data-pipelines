"""Generate reproducible LLM-based pytest suites for the ISE26 experiment."""

from __future__ import annotations

import argparse
import csv
import inspect
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ise26.experiment_paths import (
    resolve_generated_tests_root,
    resolve_functions_metadata_path,
)
from ise26.implementations import correct
from ise26.llm.code_extraction import extract_python_code
from ise26.llm.deepseek_client import call_deepseek
from ise26.llm.prompt_builder import build_prompt_bundle
from ise26.llm.reproducibility import (
    build_environment_snapshot,
    build_request_payload,
    compute_file_hash,
    compute_json_hash,
    compute_text_hash,
    load_json_configuration,
)

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "experiments" / "config" / "deepseek_v4_flash.json"
CORRECT_MODULE_PATH = PROJECT_ROOT / "src" / "ise26" / "implementations" / "correct.py"
PLACEHOLDER_MARKER = "GENERATED_TEST_PLACEHOLDER"
RUN_IDS = [f"run_{index:02d}" for index in range(1, 6)]
MANIFEST_FIELDNAMES = [
    "function_id",
    "function_name",
    "run_id",
    "provider",
    "model",
    "temperature",
    "top_p",
    "max_tokens",
    "timestamp_utc",
    "status",
    "syntax_valid",
    "prompt_hash",
    "function_code_hash",
    "correct_module_hash",
    "config_hash",
    "response_hash",
    "output_path",
    "error_summary",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "overwrite_used",
    "experiment_id",
]


def load_environment_file() -> None:
    """Load local environment variables from `.env` when supported."""

    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the generation workflow."""

    parser = argparse.ArgumentParser(
        description="Generate Pytest suites with DeepSeek for the ISE26 experiment."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the model configuration JSON file.",
    )
    parser.add_argument(
        "--experiment-id",
        help="Optional experiment identifier used to separate generated-test trees.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Build prompts and show the execution plan without calling the API.",
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Perform real API calls. This flag is required for non-dry execution.",
    )
    parser.add_argument(
        "--function-id",
        choices=[f"F0{index}" for index in range(1, 10)] + ["F10"],
        help="Restrict generation to a single function identifier.",
    )
    parser.add_argument(
        "--run-id",
        choices=RUN_IDS,
        help="Restrict generation to a single run identifier.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing previously generated artifacts for the selected target.",
    )

    return parser.parse_args(argv)


def resolve_experiment_id(config: dict[str, Any], cli_experiment_id: str | None) -> str | None:
    """Resolve the active experiment identifier from CLI and config values."""

    config_experiment_id = str(config.get("experiment_id", "")).strip() or None
    if cli_experiment_id and config_experiment_id and cli_experiment_id != config_experiment_id:
        raise ValueError(
            "The experiment id provided on the command line does not match the configuration file."
        )

    return cli_experiment_id or config_experiment_id


def load_functions_metadata(experiment_id: str | None) -> list[dict[str, Any]]:
    """Load the function metadata used by the experiment."""

    metadata_path = resolve_functions_metadata_path(experiment_id)
    with metadata_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def select_functions(
    function_id: str | None,
    functions_metadata: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Select the function records to be processed by the current command."""

    if function_id is None:
        return functions_metadata

    selected_functions = [record for record in functions_metadata if record["id"] == function_id]
    if not selected_functions:
        raise ValueError(f"Unknown function identifier: {function_id}")

    return selected_functions


def select_run_ids(run_id: str | None) -> list[str]:
    """Select the run labels to be processed by the current command."""

    return [run_id] if run_id else RUN_IDS


def get_function_object(function_name: str) -> Any:
    """Return the function object from the correct implementation module."""

    return getattr(correct, function_name)


def build_generation_plan(
    function_id: str | None,
    run_id: str | None,
    generated_tests_root: Path,
    functions_metadata: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build the list of generation attempts for the selected filters."""

    selected_functions = select_functions(function_id, functions_metadata)
    selected_runs = select_run_ids(run_id)
    plan: list[dict[str, Any]] = []

    for function_record in selected_functions:
        function_name = function_record["function_name"]
        function_object = get_function_object(function_name)
        function_code = inspect.getsource(function_object)
        function_docstring = inspect.getdoc(function_object) or ""

        for selected_run_id in selected_runs:
            output_directory = generated_tests_root / function_record["id"] / selected_run_id
            plan.append(
                {
                    "function_record": function_record,
                    "function_name": function_name,
                    "function_docstring": function_docstring,
                    "function_code": function_code,
                    "run_id": selected_run_id,
                    "output_directory": output_directory,
                }
            )

    return plan


def is_placeholder_test_file(test_file_path: Path) -> bool:
    """Return whether a test file is an ungenerated placeholder."""

    if not test_file_path.exists():
        return False

    content = test_file_path.read_text(encoding="utf-8")
    return PLACEHOLDER_MARKER in content


def outputs_already_generated(output_directory: Path) -> bool:
    """Check whether a target directory already contains non-placeholder outputs."""

    test_file_path = output_directory / "test_generated.py"
    metadata_path = output_directory / "metadata.json"
    status_path = output_directory / "status.json"

    if metadata_path.exists():
        return True

    if status_path.exists():
        try:
            status_payload = json.loads(status_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return True

        status_value = str(status_payload.get("status", "")).strip()
        if status_value not in {"placeholder", "not_generated"}:
            return True
        return False

    if test_file_path.exists() and not is_placeholder_test_file(test_file_path):
        return True

    return False


def ensure_output_directory(output_directory: Path) -> None:
    """Ensure the selected output directory exists."""

    output_directory.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text content to a file."""

    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON data with stable formatting."""

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_placeholder_test_file(status: str, error: str | None = None) -> str:
    """Build a controlled placeholder test file for non-generated executions."""

    lines = [
        '"""Placeholder file created by the LLM generation infrastructure."""',
        "",
        f"# Generation status: {status}",
    ]
    if error:
        lines.append(f"# Error: {error}")
    lines.append(f"# {PLACEHOLDER_MARKER}")
    lines.append("")
    return "\n".join(lines)


def build_status_payload(status: str, message: str) -> dict[str, Any]:
    """Build the status payload saved for each generation attempt."""

    return {
        "status": status,
        "message": message,
    }


def build_metadata_payload(
    *,
    function_record: dict[str, Any],
    run_id: str,
    config: dict[str, Any],
    experiment_id: str | None,
    prompt_hash: str,
    function_code_hash: str,
    correct_module_hash: str,
    config_hash: str,
    response_hash: str | None,
    syntax_valid: bool,
    overwrite_used: bool,
    call_result: dict[str, Any],
    environment_snapshot: dict[str, Any],
    extraction_mode: str | None,
    syntax_error: str | None,
) -> dict[str, Any]:
    """Build the metadata payload stored beside each generated test."""

    return {
        "function_id": function_record["id"],
        "function_name": function_record["function_name"],
        "run_id": run_id,
        "provider": config["provider"],
        "model": config["model"],
        "experiment_id": experiment_id or "",
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "max_tokens": config["max_tokens"],
        "timestamp_utc": environment_snapshot["timestamp_utc"],
        "prompt_hash": prompt_hash,
        "function_code_hash": function_code_hash,
        "correct_module_hash": correct_module_hash,
        "config_hash": config_hash,
        "response_hash": response_hash,
        "syntax_valid": syntax_valid,
        "overwrite_used": overwrite_used,
        "success": call_result["success"],
        "error": call_result["error"],
        "usage": call_result["usage"],
        "generated_by": "LLM-generated pytest suite for the ISE26 experiment",
        "request_messages": call_result["request_messages"],
        "parameters": call_result["parameters"],
        "python_version": environment_snapshot["python_version"],
        "python_implementation": environment_snapshot["python_implementation"],
        "dependency_versions": environment_snapshot["dependency_versions"],
        "git_commit": environment_snapshot["git_commit"],
        "command_executed": environment_snapshot["command_executed"],
        "extraction_mode": extraction_mode,
        "syntax_error": syntax_error,
    }


def rewrite_manifest_with_current_schema(manifest_path: Path) -> None:
    """Rewrite the manifest so older rows follow the current column layout."""

    if not manifest_path.exists():
        return

    with manifest_path.open("r", encoding="utf-8", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        existing_rows = list(reader)
        existing_fieldnames = reader.fieldnames or []

    if existing_fieldnames == MANIFEST_FIELDNAMES:
        return

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=MANIFEST_FIELDNAMES)
        writer.writeheader()
        for row in existing_rows:
            writer.writerow({field: row.get(field, "") for field in MANIFEST_FIELDNAMES})


def append_manifest_row(manifest_path: Path, row: dict[str, Any]) -> None:
    """Append one generation-attempt row to the manifest CSV."""

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    rewrite_manifest_with_current_schema(manifest_path)
    write_header = not manifest_path.exists()

    with manifest_path.open("a", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=MANIFEST_FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def summarize_plan(
    plan: list[dict[str, Any]],
    config: dict[str, Any],
    execute: bool,
    experiment_id: str | None,
) -> None:
    """Print a concise summary of the generation plan."""

    function_ids = sorted({item["function_record"]["id"] for item in plan})
    run_ids = sorted({item["run_id"] for item in plan})
    mode_label = "EXECUTE" if execute else "DRY-RUN"

    print(f"Generation mode: {mode_label}")
    print(f"Provider: {config['provider']}")
    print(f"Model: {config['model']}")
    print(f"Experiment id: {experiment_id or 'legacy'}")
    print(f"Temperature: {config['temperature']}")
    print(f"Top-p: {config['top_p']}")
    print(f"Max tokens: {config['max_tokens']}")
    print(f"Total planned calls: {len(plan)}")
    print(f"Functions: {', '.join(function_ids)}")
    print(f"Runs: {', '.join(run_ids)}")


def execute_generation_attempt(
    plan_item: dict[str, Any],
    config: dict[str, Any],
    experiment_id: str | None,
    command_executed: str,
    overwrite_used: bool,
) -> dict[str, Any]:
    """Execute one real generation attempt and persist its artifacts."""

    function_record = plan_item["function_record"]
    run_id = plan_item["run_id"]
    output_directory = plan_item["output_directory"]
    ensure_output_directory(output_directory)

    prompt_bundle = build_prompt_bundle(
        function_id=function_record["id"],
        function_name=plan_item["function_name"],
        function_docstring=plan_item["function_docstring"],
        function_code=plan_item["function_code"],
        expected_behavior=function_record["expected_behavior"],
        function_description=function_record["description"],
    )

    request_payload = build_request_payload(
        provider=config["provider"],
        base_url=config["base_url"],
        model=config["model"],
        request_messages=[
            {"role": "system", "content": prompt_bundle.system_prompt},
            {"role": "user", "content": prompt_bundle.user_prompt},
        ],
        parameters={
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "max_tokens": config["max_tokens"],
            "stream": config["stream"],
            "history_policy": config["history_policy"],
        },
    )

    write_text(output_directory / "system_prompt.txt", prompt_bundle.system_prompt)
    write_text(output_directory / "prompt.txt", prompt_bundle.user_prompt)
    write_json(output_directory / "request.json", request_payload)

    prompt_hash = compute_text_hash(
        f"{prompt_bundle.system_prompt}\n\n---ISE26-USER-PROMPT---\n\n{prompt_bundle.user_prompt}"
    )
    function_code_hash = compute_text_hash(plan_item["function_code"])
    correct_module_hash = compute_file_hash(CORRECT_MODULE_PATH)
    config_hash = compute_json_hash(config)
    environment_snapshot = build_environment_snapshot(PROJECT_ROOT, command_executed)

    call_result = call_deepseek(
        system_prompt=prompt_bundle.system_prompt,
        user_prompt=prompt_bundle.user_prompt,
        model=config["model"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        max_tokens=config["max_tokens"],
        stream=config["stream"],
        base_url=config["base_url"],
    ).to_dict()

    write_text(output_directory / "raw_response.txt", call_result["response_text"])

    if not call_result["success"]:
        placeholder_content = build_placeholder_test_file("api_error", call_result["error"])
        write_text(output_directory / "test_generated.py", placeholder_content)
        metadata_payload = build_metadata_payload(
            function_record=function_record,
            run_id=run_id,
            config=config,
            experiment_id=experiment_id,
            prompt_hash=prompt_hash,
            function_code_hash=function_code_hash,
            correct_module_hash=correct_module_hash,
            config_hash=config_hash,
            response_hash=None,
            syntax_valid=False,
            overwrite_used=overwrite_used,
            call_result=call_result,
            environment_snapshot=environment_snapshot,
            extraction_mode=None,
            syntax_error=None,
        )
        write_json(output_directory / "metadata.json", metadata_payload)
        write_json(
            output_directory / "status.json",
            build_status_payload("api_error", call_result["error"] or "Unknown API error."),
        )

        return {
            "function_id": function_record["id"],
            "function_name": function_record["function_name"],
            "run_id": run_id,
            "provider": config["provider"],
            "model": config["model"],
            "experiment_id": experiment_id or "",
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "max_tokens": config["max_tokens"],
            "timestamp_utc": metadata_payload["timestamp_utc"],
            "status": "api_error",
            "syntax_valid": False,
            "prompt_hash": prompt_hash,
            "function_code_hash": function_code_hash,
            "correct_module_hash": correct_module_hash,
            "config_hash": config_hash,
            "response_hash": "",
            "output_path": str(output_directory.relative_to(PROJECT_ROOT)),
            "error_summary": call_result["error"] or "",
            "input_tokens": "",
            "output_tokens": "",
            "total_tokens": "",
            "overwrite_used": overwrite_used,
        }

    extraction_result = extract_python_code(call_result["response_text"])
    write_text(output_directory / "test_generated.py", extraction_result.code)

    status = "generated_syntax_valid" if extraction_result.syntax_valid else "generated_syntax_invalid"
    status_message = (
        "Generated code parsed successfully."
        if extraction_result.syntax_valid
        else "Generated code was saved, but Python syntax validation failed."
    )
    response_hash = compute_text_hash(call_result["response_text"])

    metadata_payload = build_metadata_payload(
        function_record=function_record,
        run_id=run_id,
        config=config,
        experiment_id=experiment_id,
        prompt_hash=prompt_hash,
        function_code_hash=function_code_hash,
        correct_module_hash=correct_module_hash,
        config_hash=config_hash,
        response_hash=response_hash,
        syntax_valid=extraction_result.syntax_valid,
        overwrite_used=overwrite_used,
        call_result=call_result,
        environment_snapshot=environment_snapshot,
        extraction_mode=extraction_result.extraction_mode,
        syntax_error=extraction_result.syntax_error,
    )
    write_json(output_directory / "metadata.json", metadata_payload)
    write_json(output_directory / "status.json", build_status_payload(status, status_message))

    usage = call_result["usage"] or {}

    return {
        "function_id": function_record["id"],
        "function_name": function_record["function_name"],
        "run_id": run_id,
        "provider": config["provider"],
        "model": config["model"],
        "experiment_id": experiment_id or "",
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "max_tokens": config["max_tokens"],
        "timestamp_utc": metadata_payload["timestamp_utc"],
        "status": status,
        "syntax_valid": extraction_result.syntax_valid,
        "prompt_hash": prompt_hash,
        "function_code_hash": function_code_hash,
        "correct_module_hash": correct_module_hash,
        "config_hash": config_hash,
        "response_hash": response_hash,
        "output_path": str(output_directory.relative_to(PROJECT_ROOT)),
        "error_summary": extraction_result.syntax_error or "",
        "input_tokens": usage.get("prompt_tokens", ""),
        "output_tokens": usage.get("completion_tokens", ""),
        "total_tokens": usage.get("total_tokens", ""),
        "overwrite_used": overwrite_used,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the LLM test-generation workflow."""

    args = parse_args(argv)
    load_environment_file()
    config_path = args.config
    config = load_json_configuration(config_path)
    experiment_id = resolve_experiment_id(config, args.experiment_id)
    generated_tests_root = resolve_generated_tests_root(config["model"], experiment_id=experiment_id)
    manifest_path = generated_tests_root / "manifest.csv"
    functions_metadata = load_functions_metadata(experiment_id)
    plan = build_generation_plan(args.function_id, args.run_id, generated_tests_root, functions_metadata)
    execute = bool(args.execute)
    dry_run = bool(args.dry_run or not execute)
    overwrite_used = bool(args.overwrite)

    if overwrite_used:
        print("Overwrite mode is enabled. Existing artifacts may be replaced for matching targets.")
    summarize_plan(plan, config, execute=execute, experiment_id=experiment_id)

    if dry_run and not execute:
        print("Dry-run mode active. No API calls were made and no files were changed.")
        return 0

    command_executed = " ".join([sys.executable, *sys.argv])
    manifest_rows: list[dict[str, Any]] = []

    for plan_item in plan:
        output_directory = plan_item["output_directory"]
        relative_output = output_directory.relative_to(PROJECT_ROOT)

        if outputs_already_generated(output_directory) and not args.overwrite:
            print(f"Skipping existing generated artifacts at: {relative_output}")
            continue

        manifest_row = execute_generation_attempt(
            plan_item,
            config,
            experiment_id,
            command_executed,
            overwrite_used,
        )
        manifest_rows.append(manifest_row)
        append_manifest_row(manifest_path, manifest_row)
        print(
            f"Recorded generation for {manifest_row['function_id']} {manifest_row['run_id']}: "
            f"{manifest_row['status']}"
        )

    if not manifest_rows:
        print("No generation attempts were executed.")
    else:
        print(f"Manifest updated at: {manifest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

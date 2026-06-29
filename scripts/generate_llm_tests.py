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

from ise26.implementations import correct
from ise26.llm.code_extraction import extract_python_code
from ise26.llm.deepseek_client import call_deepseek
from ise26.llm.prompt_builder import build_prompt_bundle
from ise26.llm.reproducibility import (
    build_environment_snapshot,
    build_request_payload,
    compute_json_hash,
    compute_text_hash,
    load_json_configuration,
)

CONFIG_PATH = PROJECT_ROOT / "experiments" / "config" / "deepseek_v4_flash.json"
FUNCTIONS_METADATA_PATH = PROJECT_ROOT / "src" / "ise26" / "metadata" / "functions.json"
GENERATED_TESTS_ROOT = PROJECT_ROOT / "experiments" / "generated_tests"
MANIFEST_PATH = GENERATED_TESTS_ROOT / "manifest.csv"
PLACEHOLDER_MARKER = "GENERATED_TEST_PLACEHOLDER"
RUN_IDS = [f"run_{index:02d}" for index in range(1, 6)]


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
        "--dry-run",
        action="store_true",
        help="Build prompts and show the execution plan without calling the API.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform real API calls. This flag is required for non-dry execution.",
    )
    parser.add_argument(
        "--function-id",
        choices=[f"F0{index}" for index in range(1, 7)],
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


def load_functions_metadata() -> list[dict[str, Any]]:
    """Load the function metadata used by the experiment."""

    with FUNCTIONS_METADATA_PATH.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def select_functions(function_id: str | None) -> list[dict[str, Any]]:
    """Select the function records to be processed by the current command."""

    functions_metadata = load_functions_metadata()
    if function_id is None:
        return functions_metadata

    return [record for record in functions_metadata if record["id"] == function_id]


def select_run_ids(run_id: str | None) -> list[str]:
    """Select the run labels to be processed by the current command."""

    return [run_id] if run_id else RUN_IDS


def get_function_object(function_name: str) -> Any:
    """Return the function object from the correct implementation module."""

    return getattr(correct, function_name)


def build_generation_plan(
    function_id: str | None,
    run_id: str | None,
) -> list[dict[str, Any]]:
    """Build the list of generation attempts for the selected filters."""

    selected_functions = select_functions(function_id)
    selected_runs = select_run_ids(run_id)
    plan: list[dict[str, Any]] = []

    for function_record in selected_functions:
        function_name = function_record["function_name"]
        function_object = get_function_object(function_name)
        function_code = inspect.getsource(function_object)
        function_docstring = inspect.getdoc(function_object) or ""

        for selected_run_id in selected_runs:
            output_directory = GENERATED_TESTS_ROOT / function_record["id"] / selected_run_id
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

    if metadata_path.exists() or status_path.exists():
        return True

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
    prompt_hash: str,
    function_code_hash: str,
    config_hash: str,
    response_hash: str | None,
    syntax_valid: bool,
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
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "max_tokens": config["max_tokens"],
        "timestamp_utc": environment_snapshot["timestamp_utc"],
        "prompt_hash": prompt_hash,
        "function_code_hash": function_code_hash,
        "config_hash": config_hash,
        "response_hash": response_hash,
        "syntax_valid": syntax_valid,
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


def append_manifest_row(row: dict[str, Any]) -> None:
    """Append one generation-attempt row to the manifest CSV."""

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
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
        "response_hash",
        "output_path",
        "error_summary",
        "input_tokens",
        "output_tokens",
        "total_tokens",
    ]
    write_header = not MANIFEST_PATH.exists()

    with MANIFEST_PATH.open("a", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def summarize_plan(plan: list[dict[str, Any]], config: dict[str, Any], execute: bool) -> None:
    """Print a concise summary of the generation plan."""

    function_ids = sorted({item["function_record"]["id"] for item in plan})
    run_ids = sorted({item["run_id"] for item in plan})
    mode_label = "EXECUTE" if execute else "DRY-RUN"

    print(f"Generation mode: {mode_label}")
    print(f"Provider: {config['provider']}")
    print(f"Model: {config['model']}")
    print(f"Temperature: {config['temperature']}")
    print(f"Top-p: {config['top_p']}")
    print(f"Max tokens: {config['max_tokens']}")
    print(f"Total planned calls: {len(plan)}")
    print(f"Functions: {', '.join(function_ids)}")
    print(f"Runs: {', '.join(run_ids)}")


def execute_generation_attempt(
    plan_item: dict[str, Any],
    config: dict[str, Any],
    command_executed: str,
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
            prompt_hash=prompt_hash,
            function_code_hash=function_code_hash,
            config_hash=config_hash,
            response_hash=None,
            syntax_valid=False,
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
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "max_tokens": config["max_tokens"],
            "timestamp_utc": metadata_payload["timestamp_utc"],
            "status": "api_error",
            "syntax_valid": False,
            "prompt_hash": prompt_hash,
            "response_hash": "",
            "output_path": str(output_directory.relative_to(PROJECT_ROOT)),
            "error_summary": call_result["error"] or "",
            "input_tokens": "",
            "output_tokens": "",
            "total_tokens": "",
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
        prompt_hash=prompt_hash,
        function_code_hash=function_code_hash,
        config_hash=config_hash,
        response_hash=response_hash,
        syntax_valid=extraction_result.syntax_valid,
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
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "max_tokens": config["max_tokens"],
        "timestamp_utc": metadata_payload["timestamp_utc"],
        "status": status,
        "syntax_valid": extraction_result.syntax_valid,
        "prompt_hash": prompt_hash,
        "response_hash": response_hash,
        "output_path": str(output_directory.relative_to(PROJECT_ROOT)),
        "error_summary": extraction_result.syntax_error or "",
        "input_tokens": usage.get("prompt_tokens", ""),
        "output_tokens": usage.get("completion_tokens", ""),
        "total_tokens": usage.get("total_tokens", ""),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the LLM test-generation workflow."""

    args = parse_args(argv)
    load_environment_file()
    config = load_json_configuration(CONFIG_PATH)
    plan = build_generation_plan(args.function_id, args.run_id)
    execute = bool(args.execute)
    dry_run = bool(args.dry_run or not execute)

    summarize_plan(plan, config, execute=execute)

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

        manifest_row = execute_generation_attempt(plan_item, config, command_executed)
        manifest_rows.append(manifest_row)
        append_manifest_row(manifest_row)
        print(
            f"Recorded generation for {manifest_row['function_id']} {manifest_row['run_id']}: "
            f"{manifest_row['status']}"
        )

    if not manifest_rows:
        print("No generation attempts were executed.")
    else:
        print(f"Manifest updated at: {MANIFEST_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

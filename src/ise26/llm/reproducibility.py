"""Reproducibility helpers for prompt, configuration, and environment metadata."""

from __future__ import annotations

import hashlib
import json
from importlib import metadata as importlib_metadata
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


def compute_text_hash(value: str) -> str:
    """Return the SHA-256 hash of a text value."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_json_hash(data: Any) -> str:
    """Return the SHA-256 hash of JSON-serializable data."""

    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return compute_text_hash(serialized)


def get_current_utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""

    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_dependency_versions(package_names: list[str]) -> dict[str, str | None]:
    """Collect installed versions for a selected set of packages.

    Args:
        package_names: Package names to query from the current environment.

    Returns:
        A mapping from package name to version string or ``None`` when missing.
    """

    versions: dict[str, str | None] = {}
    for package_name in package_names:
        try:
            versions[package_name] = importlib_metadata.version(package_name)
        except importlib_metadata.PackageNotFoundError:
            versions[package_name] = None

    return versions


def get_git_commit(project_root: Path) -> str | None:
    """Return the current git commit hash when available.

    Args:
        project_root: Repository root used to run the git command.

    Returns:
        The commit hash, or ``None`` when unavailable.
    """

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None

    return completed.stdout.strip() or None


def build_environment_snapshot(project_root: Path, command_executed: str) -> dict[str, Any]:
    """Collect environment metadata relevant to reproducibility.

    Args:
        project_root: Repository root path.
        command_executed: Exact command-line invocation used for generation.

    Returns:
        A dictionary with Python, dependency, and git metadata.
    """

    return {
        "timestamp_utc": get_current_utc_timestamp(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "dependency_versions": get_dependency_versions(
            ["openai", "python-dotenv", "pandas", "pytest"]
        ),
        "git_commit": get_git_commit(project_root),
        "command_executed": command_executed,
        "sys_executable": sys.executable,
    }


def build_request_payload(
    provider: str,
    base_url: str,
    model: str,
    request_messages: list[dict[str, str]],
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Build a serializable request record without secret data."""

    return {
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "messages": request_messages,
        "parameters": parameters,
    }


def load_json_configuration(config_path: Path) -> dict[str, Any]:
    """Load a JSON configuration file from disk.

    Args:
        config_path: Path to the JSON file.

    Returns:
        The parsed JSON object as a dictionary.
    """

    with config_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)

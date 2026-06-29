"""Mechanical extraction helpers for code returned by LLM responses."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import re


PYTHON_FENCE_PATTERN = re.compile(r"```python\s*(.*?)```", re.IGNORECASE | re.DOTALL)
GENERIC_FENCE_PATTERN = re.compile(r"```\s*(.*?)```", re.DOTALL)


@dataclass(slots=True)
class ExtractedCodeResult:
    """Represent mechanically extracted code and syntax-validation metadata.

    Attributes:
        code: Extracted Python code after removing outer Markdown fences.
        syntax_valid: Whether the extracted code parses successfully with ``ast``.
        syntax_error: Error text captured when syntax validation fails.
        extraction_mode: How the content was extracted from the raw response.
    """

    code: str
    syntax_valid: bool
    syntax_error: str | None
    extraction_mode: str


def _extract_code_block(raw_response: str) -> tuple[str, str]:
    """Extract the code portion from a raw LLM response without rewriting logic.

    Args:
        raw_response: Full raw response text returned by the model.

    Returns:
        A tuple containing the extracted code text and the extraction mode.
    """

    python_match = PYTHON_FENCE_PATTERN.search(raw_response)
    if python_match:
        return python_match.group(1).strip(), "markdown_python"

    generic_match = GENERIC_FENCE_PATTERN.search(raw_response)
    if generic_match:
        return generic_match.group(1).strip(), "markdown_generic"

    return raw_response.strip(), "raw_text"


def extract_python_code(raw_response: str) -> ExtractedCodeResult:
    """Extract Python code mechanically and validate its syntax.

    Args:
        raw_response: Full raw response text returned by the model.

    Returns:
        A structured extraction result. The code is preserved even when syntax
        validation fails.
    """

    code, extraction_mode = _extract_code_block(raw_response)

    try:
        ast.parse(code)
    except SyntaxError as error:
        return ExtractedCodeResult(
            code=code,
            syntax_valid=False,
            syntax_error=str(error),
            extraction_mode=extraction_mode,
        )

    return ExtractedCodeResult(
        code=code,
        syntax_valid=True,
        syntax_error=None,
        extraction_mode=extraction_mode,
    )

"""Prompt-construction helpers for reproducible Pytest generation requests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROMPT_TEMPLATE_PATH = PROJECT_ROOT / "experiments" / "prompts" / "test_generation_prompt_template.md"

DEFAULT_SYSTEM_PROMPT = (
    "You generate pytest suites for Python data-transformation functions. "
    "Return only valid Python code for the test file and do not include Markdown fences."
)


@dataclass(slots=True)
class PromptBundle:
    """Store the system and user prompts used for one independent generation."""

    system_prompt: str
    user_prompt: str
    template_path: str


def load_prompt_template(template_path: Path = PROMPT_TEMPLATE_PATH) -> str:
    """Load the shared prompt template from disk.

    Args:
        template_path: Path to the template file used by the experiment.

    Returns:
        The template content as UTF-8 text.
    """

    return template_path.read_text(encoding="utf-8")


def build_prompt_bundle(
    function_id: str,
    function_name: str,
    function_docstring: str,
    function_code: str,
    expected_behavior: str,
    function_description: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> PromptBundle:
    """Build the prompt pair for a single function and run.

    Args:
        function_id: Experiment function identifier such as ``F01``.
        function_name: Public function name exposed through ``ise26.targets``.
        function_docstring: Docstring extracted from the correct implementation.
        function_code: Source code of the correct function.
        expected_behavior: Behavioral summary used in the experiment protocol.
        function_description: Short human-readable function description.
        system_prompt: Global system instruction for the model.

    Returns:
        A prompt bundle containing the shared system prompt and the fully
        formatted user prompt.
    """

    template = load_prompt_template()
    user_prompt = template.format(
        function_id=function_id,
        function_name=function_name,
        function_description=function_description,
        function_docstring=function_docstring.strip(),
        function_code=function_code.rstrip(),
        expected_behavior=expected_behavior.strip(),
    )

    return PromptBundle(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        template_path=str(PROMPT_TEMPLATE_PATH),
    )

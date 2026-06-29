"""DeepSeek client helpers for reproducible single-call test generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any

from ise26.llm.reproducibility import get_current_utc_timestamp


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
API_KEY_ENV_VAR = "DEEPSEEK_API_KEY"


@dataclass(slots=True)
class LLMCallResult:
    """Store a normalized record of one LLM API call attempt.

    Attributes:
        provider: Provider name used by the experiment.
        model: Model identifier sent to the API.
        request_messages: Serialized request messages without secret data.
        response_text: Extracted textual content returned by the model.
        raw_response_serialized: Full serialized SDK response when available.
        usage: Token usage data returned by the API, when present.
        created_at_utc: UTC timestamp captured for the call result.
        parameters: Request parameters excluding the API key.
        error: Error message when the call fails.
        success: Whether the call completed without a client or API error.
    """

    provider: str
    model: str
    request_messages: list[dict[str, str]]
    response_text: str
    raw_response_serialized: dict[str, Any] | None
    usage: dict[str, Any] | None
    created_at_utc: str
    parameters: dict[str, Any]
    error: str | None
    success: bool

    def to_dict(self) -> dict[str, Any]:
        """Return the dataclass content as a regular dictionary."""

        return asdict(self)


def require_api_key(env_var: str = API_KEY_ENV_VAR) -> str:
    """Read and validate the DeepSeek API key from the environment.

    Args:
        env_var: Environment variable expected to contain the secret key.

    Returns:
        The API key string stripped of surrounding whitespace.

    Raises:
        RuntimeError: If the environment variable is missing or blank.
    """

    api_key = os.getenv(env_var, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Missing DeepSeek API key. Set the {env_var} environment variable before using --execute."
        )

    return api_key


def _import_openai_client() -> Any:
    """Import and return the OpenAI-compatible client class lazily.

    Returns:
        The ``OpenAI`` client class from the installed SDK.

    Raises:
        RuntimeError: If the dependency is not installed.
    """

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "The 'openai' package is required for DeepSeek API calls. Install dependencies from requirements.txt."
        ) from error

    return OpenAI


def _serialize_sdk_object(value: Any) -> dict[str, Any] | None:
    """Serialize an SDK response object into JSON-compatible data when possible.

    Args:
        value: SDK object to serialize.

    Returns:
        A dictionary representation when supported, otherwise ``None``.
    """

    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    return None


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    top_p: float = 1.0,
    max_tokens: int = 4096,
    stream: bool = False,
    base_url: str = DEFAULT_BASE_URL,
) -> LLMCallResult:
    """Call the DeepSeek chat-completions API through the OpenAI-compatible SDK.

    The function is intentionally stateless and accepts a complete prompt pair
    for a single independent call. No history is reused across invocations.

    Args:
        system_prompt: System instruction for the model.
        user_prompt: User prompt containing the function-specific request.
        model: Model name sent to the provider.
        temperature: Sampling temperature.
        top_p: Nucleus sampling parameter.
        max_tokens: Maximum number of output tokens requested.
        stream: Streaming flag. The experiment keeps this disabled.
        base_url: Provider base URL compatible with the OpenAI SDK.

    Returns:
        A normalized call result with messages, response text, usage, and
        serialized raw response data when available.
    """

    api_key = require_api_key()
    openai_client_class = _import_openai_client()
    client = openai_client_class(api_key=api_key, base_url=base_url)

    request_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    parameters = {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": stream,
        "base_url": base_url,
    }
    created_at_utc = get_current_utc_timestamp()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=request_messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream,
        )
    except Exception as error:
        return LLMCallResult(
            provider="DeepSeek",
            model=model,
            request_messages=request_messages,
            response_text="",
            raw_response_serialized=None,
            usage=None,
            created_at_utc=created_at_utc,
            parameters=parameters,
            error=str(error),
            success=False,
        )

    response_text = ""
    if getattr(response, "choices", None):
        message = response.choices[0].message
        response_text = message.content or ""

    return LLMCallResult(
        provider="DeepSeek",
        model=model,
        request_messages=request_messages,
        response_text=response_text,
        raw_response_serialized=_serialize_sdk_object(response),
        usage=_serialize_sdk_object(getattr(response, "usage", None)),
        created_at_utc=created_at_utc,
        parameters=parameters,
        error=None,
        success=True,
    )

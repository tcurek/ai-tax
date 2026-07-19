"""LLM client adapters for OCR and graph workflows.

The application needs two different integration shapes:

* markitdown-ocr expects an OpenAI-compatible SDK client with
  ``client.chat.completions.create(...)`` plus a vision-capable model name.
* LangGraph typically works with LangChain chat models.

This module keeps those adapters behind one application-level client so future
providers can add equivalent adapter methods without changing callers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field

LLMProviderName = Literal["openai"]


class LLMConfig(BaseModel):
    """Configuration for the application LLM provider."""

    provider: LLMProviderName = "openai"
    chat_model: str = Field(
        default="gpt-4o-mini",
        description="Text/chat model used by LangGraph workflows.",
    )
    vision_model: str = Field(
        default="gpt-4o-mini",
        description="Vision-capable model used by markitdown-ocr.",
    )
    api_key_env_var: str = Field(
        default="OPENAI_API_KEY",
        description="Environment variable containing the provider API key.",
    )
    base_url: str | None = Field(
        default=None,
        description="Optional OpenAI-compatible API base URL.",
    )
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    timeout_seconds: float | None = Field(default=60.0, gt=0.0)


@dataclass(frozen=True)
class MarkitdownOCRAdapter:
    """Arguments needed by ``MarkItDown(enable_plugins=True, ...)``."""

    llm_client: Any
    llm_model: str

    def as_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments accepted by MarkItDown/markitdown-ocr."""
        return {"llm_client": self.llm_client, "llm_model": self.llm_model}


@runtime_checkable
class LLMProviderClient(Protocol):
    """Provider adapter contract for app LLM integrations."""

    def for_markitdown_ocr(self) -> MarkitdownOCRAdapter:
        """Return an OpenAI-compatible client/model pair for markitdown-ocr."""
        ...

    def for_langgraph(self) -> Any:
        """Return a LangChain chat model suitable for LangGraph nodes."""
        ...


class MissingLLMCredentialsError(RuntimeError):
    """Raised when an LLM provider cannot be constructed without credentials."""


@dataclass(frozen=True)
class OpenAILLMClient:
    """OpenAI-backed implementation of the app LLM client."""

    config: LLMConfig = field(default_factory=LLMConfig)

    def _api_key(self) -> str:
        api_key = os.environ.get(self.config.api_key_env_var)
        if not api_key:
            raise MissingLLMCredentialsError(
                f"Set {self.config.api_key_env_var} before creating the "
                "OpenAI LLM client. Do not store API keys in config files."
            )
        return api_key

    def _openai_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"api_key": self._api_key()}
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url
        if self.config.timeout_seconds is not None:
            kwargs["timeout"] = self.config.timeout_seconds
        return kwargs

    def for_markitdown_ocr(self) -> MarkitdownOCRAdapter:
        """Return the OpenAI SDK client shape required by markitdown-ocr."""
        from openai import OpenAI

        return MarkitdownOCRAdapter(
            llm_client=OpenAI(**self._openai_kwargs()),
            llm_model=self.config.vision_model,
        )

    def for_langgraph(self) -> Any:
        """Return a LangChain chat model usable inside LangGraph workflows."""
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.config.chat_model,
            temperature=self.config.temperature,
            **self._openai_kwargs(),
        )


def create_llm_client(config: LLMConfig | None = None) -> LLMProviderClient:
    """Create the configured application LLM client.

    The provider branch is intentionally centralized so adding Anthropic,
    Azure OpenAI, Gemini, or local OpenAI-compatible providers later does not
    require changes in OCR or LangGraph call sites.
    """
    resolved_config = config or LLMConfig()

    if resolved_config.provider == "openai":
        return OpenAILLMClient(resolved_config)

    # Kept as a defensive guard in case validation is bypassed.
    raise ValueError(f"Unsupported LLM provider: {resolved_config.provider}")

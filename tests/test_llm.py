import pytest

from ai_tax.llm import (
    LLMConfig,
    MarkitdownOCRAdapter,
    MissingLLMCredentialsError,
    OpenAILLMClient,
    create_llm_client,
)


def test_create_llm_client_returns_openai_client() -> None:
    client = create_llm_client(LLMConfig(provider="openai"))

    assert isinstance(client, OpenAILLMClient)


def test_missing_openai_api_key_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = OpenAILLMClient()

    with pytest.raises(MissingLLMCredentialsError, match="OPENAI_API_KEY"):
        client.for_markitdown_ocr()


def test_markitdown_ocr_adapter_returns_openai_compatible_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = OpenAILLMClient(LLMConfig(vision_model="gpt-4o-mini"))

    adapter = client.for_markitdown_ocr()

    assert isinstance(adapter, MarkitdownOCRAdapter)
    assert adapter.llm_model == "gpt-4o-mini"
    assert hasattr(adapter.llm_client, "chat")
    assert hasattr(adapter.llm_client.chat, "completions")
    assert adapter.as_kwargs() == {
        "llm_client": adapter.llm_client,
        "llm_model": "gpt-4o-mini",
    }


def test_langgraph_adapter_returns_langchain_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = OpenAILLMClient(LLMConfig(chat_model="gpt-4o-mini"))

    model = client.for_langgraph()

    assert model.__class__.__name__ == "ChatOpenAI"
    assert model.model_name == "gpt-4o-mini"

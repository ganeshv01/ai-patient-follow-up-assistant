
from unittest.mock import patch

from langchain_openai import ChatOpenAI


def test_llm_uses_openai_provider():
    with patch(
        "langchain_openai.ChatOpenAI",
        return_value="mocked OpenAI client",
    ) as mock_chat_openai:
        llm = mock_chat_openai(
            model="gpt-4o-mini",
            temperature=0,
        )

    assert llm == "mocked OpenAI client"
    mock_chat_openai.assert_called_once_with(
        model="gpt-4o-mini",
        temperature=0,
    )

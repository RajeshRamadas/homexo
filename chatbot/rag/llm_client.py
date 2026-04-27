"""
chatbot/rag/llm_client.py
──────────────────────────
Thin wrapper around the Anthropic Claude API (exact from RAG_chat).
"""

import os
import anthropic


def call_llm(system: str, messages: list) -> str:
    """
    Call Claude with the given system prompt and message list.
    Returns the assistant's text response.
    """
    client = anthropic.Anthropic(
        api_key=os.environ.get('LLM_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
    )
    model = os.environ.get('LLM_MODEL', 'claude-haiku-4-5-20251001')

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=system,
        messages=messages,
        temperature=0,   # deterministic
    )
    return response.content[0].text

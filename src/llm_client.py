"""
Single entry point for LLM calls.

Everything upstream calls call_llm(prompt) and does not know or care which
provider answers. The seam was written as a contingency against a named
risk (AWS Bedrock account verification), and the risk fired: verification
requires business documentation we do not have. Switching cost one config
change and no code above this file.

The client and model id are read lazily, not at import: app.py imports this
module at startup, and a hard import-time env read would crash the whole demo
before any UI renders if .env had not loaded. Deferring the read turns that
into a caught, readable error at the point of the first call.
"""
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Create a .env in the project "
                "root (see .env.example) and run from the project root."
            )
        _client = anthropic.Anthropic()
    return _client


def call_llm(prompt: str, max_tokens: int = 1024) -> tuple[str, dict]:
    """Send one prompt. Return (text, usage).

    Usage is returned rather than discarded so cost can be measured from
    real token counts instead of estimated.
    """
    model = os.environ.get("ANTHROPIC_MODEL_ID")
    if not model:
        raise RuntimeError(
            "ANTHROPIC_MODEL_ID is not set. Add it to your .env "
            "(see .env.example)."
        )
    msg = _get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text, {
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }
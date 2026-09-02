"""
Single entry point for LLM calls.

Everything upstream calls call_llm(prompt) and does not know or care which
provider answers. The seam was written as a contingency against a named
risk (AWS Bedrock account verification), and the risk fired: verification
requires business documentation we do not have. Switching cost one config
change and no code above this file.
"""
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = anthropic.Anthropic()
_MODEL = os.environ["ANTHROPIC_MODEL_ID"]


def call_llm(prompt: str, max_tokens: int = 1024) -> tuple[str, dict]:
    """Send one prompt. Return (text, usage).

    Usage is returned rather than discarded so cost can be measured from
    real token counts instead of estimated.
    """
    msg = _client.messages.create(
        model=_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text, {
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }
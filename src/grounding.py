"""Evidence grounding: is the quoted evidence actually in the posting?

This proves the model did not invent its citation. It does NOT prove the
attribution is correct — those are different claims and conflating them
would overstate what the check delivers.

Normalisation is applied to both sides equally: lowercase, collapse
whitespace, strip common typographic substitutions. Without it, a model that
quotes correctly but reflows a line break fails for no useful reason.
"""
import re

_WS = re.compile(r"\s+")
_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'",
                         "\u201c": '"', "\u201d": '"',
                         "\u2013": "-", "\u2014": "-"})


def normalise(text: str) -> str:
    return _WS.sub(" ", text.translate(_QUOTES).lower()).strip()


def is_grounded(evidence: str, description: str) -> bool:
    """True if evidence appears in description, ignoring whitespace entirely.

    The corpus contains fused words where HTML block tags were removed
    without substitution ("developmentusing", "azureweb"). A model quoting
    that text correctly inserts the missing space, which a strict substring
    check would reject. Removing whitespace from both sides makes the check
    insensitive to that corruption while still requiring the same characters
    in the same order.
    """
    if not evidence or not description:
        return False
    strip_ws = str.maketrans("", "", " \t\n\r")
    return (normalise(evidence).translate(strip_ws)
            in normalise(description).translate(strip_ws))

def strip_fences(text: str) -> str:
    """Remove markdown code fences the model adds despite instructions.

    Models wrap JSON in ```json ... ``` reliably enough that stripping is
    more robust than prompting against it. Cheaper than a retry.
    """
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
    if t.endswith("```"):
        t = t.rsplit("```", 1)[0]
    return t.strip()
"""
Canonical technology matching. Pure Python, no Spark.

Kept separate from the Spark job so it can be tested in a second without
starting a JVM, and so the matching logic is readable on its own.

Matching is case-insensitive with word boundaries. Substring matching would
find "R" inside "your" and "Go" inside "Google"; word boundaries are not
optional here.
"""
import re
from functools import lru_cache

import yaml

GAZETTEER_PATH = "config/gazetteer.yaml"


def _build_pattern(term: str) -> str:
    """Word-boundary regex for one term.

    \\b asserts a boundary between a word and non-word character. It fails
    for terms ending in punctuation (C++, C#) because there is no word
    character at the end to form a boundary with, so those get an explicit
    lookahead instead.
    """
    escaped = re.escape(term)
    if term[-1].isalnum():
        return r"\b" + escaped + r"\b"
    # Ends in punctuation: assert the next char is not alphanumeric.
    return r"\b" + escaped + r"(?![\w+#])"

@lru_cache(maxsize=1)
def load_gazetteer(path: str = GAZETTEER_PATH):
    """Return [(canonical, compiled_regex), ...].

    Cached because in Spark this is called once per executor process, not
    once per row. Recompiling 111 regexes for each of 121,842 rows would
    dominate the runtime.
    """
    with open(path, encoding="utf-8") as f:
        entries = yaml.safe_load(f)

    compiled = []
    for entry in entries:
        canonical = entry["canonical"]
                # Four terms are lexically ambiguous in prose: "Go" matches "go to",
        # "R" matches "R&D", "Express" matches "express interest", "dbt"
        # matches DBT (Dialectical Behaviour Therapy). For these the bare
        # canonical form is excluded and only qualified aliases are matched.
        # The change is reported: it trades recall on these four terms for
        # precision, because this list also defines the study population.
        if entry.get("requires_context"):
            surface_forms = list(entry.get("aliases") or [])
        else:
            surface_forms = [canonical] + list(entry.get("aliases") or [])
        pattern = "|".join(_build_pattern(t) for t in surface_forms)
        compiled.append((canonical, re.compile(pattern, re.IGNORECASE)))
    return compiled


def extract_skills(text: str) -> list:
    """Return sorted canonical terms present in text. COMPUTED, not generated."""
    if not text:
        return []
    found = [canon for canon, rx in load_gazetteer() if rx.search(text)]
    return sorted(found)


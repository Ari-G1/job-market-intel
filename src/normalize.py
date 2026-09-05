"""Maps LLM skill strings onto gazetteer canonical terms.

Exact case-insensitive match against canonical names and aliases, plus three
hand-listed rules for strings the model produced that denote a canonical term
under a different name. Deliberately no fuzzy matching: every fuzzy rule is a
judgement that would have to be defended, and unmatched mentions are excluded
from scoring rather than guessed at.

Returns a list because one string can denote two terms ("C/C++").
"""
import yaml

_entries = yaml.safe_load(open("config/gazetteer.yaml", encoding="utf-8"))

LOOKUP = {}
for _e in _entries:
    LOOKUP[_e["canonical"].lower()] = [_e["canonical"]]
    for _a in _e.get("aliases") or []:
        LOOKUP[_a.lower()] = [_e["canonical"]]

# Hand-listed rules, each justified in the write-up:
#   C/C++          - one string denoting two canonical terms
#   .NET Framework - product editions of the canonical .NET
#   .NET Core      - same
EXTRA = {
    "c/c++": ["C", "C++"],
    ".net framework": [".NET"],
    ".net core": [".NET"],
}
for _k, _v in EXTRA.items():
    LOOKUP[_k] = _v


def normalize(skill):
    """Return the canonical terms this string denotes, or [] if unmapped."""
    return LOOKUP.get(skill.strip().lower(), [])
"""Pydantic schema for LLM output. Validation, not generation.

The schema is strict by design: an extra field or a bad attribution value is
a validation failure, not something silently accepted. That strictness is
what makes "validated, never trusted" a real claim rather than a slogan.
"""
from typing import Literal

from pydantic import BaseModel, Field

ATTRIBUTIONS = ("required", "preferred", "boilerplate", "not_expected")


class SkillMention(BaseModel):
    model_config = {"extra": "forbid"}

    skill: str = Field(min_length=1, max_length=60)
    attribution: Literal["required", "preferred", "boilerplate", "not_expected"]
    evidence: str = Field(min_length=1, max_length=400)


class Extraction(BaseModel):
    model_config = {"extra": "forbid"}

    skills: list[SkillMention]
    seniority: Literal["junior", "mid", "senior", "unspecified"]
    years_experience_min: int | None = Field(default=None, ge=0, le=50)
"""The extraction prompt. Iterated against the 10 dev postings only.

The verbatim-evidence instruction is not decoration: the grounding check in
grounding.py tests exactly this, and the rule is only coherent if the
requested behaviour matches what is validated.
"""

TEMPLATE = """You are extracting technology requirements from a job posting.

For every technology, tool, language, framework, platform or database that
appears in the posting, output one entry with an attribution:

- "required"     - the posting states the candidate must have this skill.
- "preferred"    - the posting states it is desirable but not mandatory
                   ("a plus", "nice to have", "preferred", "ideally").
- "boilerplate"  - it appears in company, team, product or stack description
                   without being presented as a candidate requirement.
- "not_expected" - the posting explicitly says it is NOT needed.

Rules:
1. Evidence must be copied character-for-character from the posting.
   Pick a span that starts and ends at a word boundary in the ORIGINAL text.
   Do not join text across a gap. Do not drop words from the middle.
   Do not re-order. Do not fix typos or spacing.
   If you cannot find a contiguous span under 15 words, use a longer one.
2. Keep evidence under 25 words. Quote the smallest CONTIGUOUS span that
   shows the attribution. When several skills share one sentence, it is
   correct to give them the same evidence.
3. If a skill appears more than once with different attributions, use this
   precedence and give evidence for the winning one:
   required > preferred > boilerplate > not_expected
4. Only technologies. No soft skills, methodologies, certifications or degrees.
5. seniority is one of: junior, mid, senior, unspecified.
6. years_experience_min is the SMALLEST years figure stated as a requirement
   anywhere in the posting. If the posting says "7+ years of X" and "3+ years
   of Y", the answer is 3. Null if no figure is stated.
7. Extract at most 25 skills. If the posting lists more, keep the most
   specific and skip generic infrastructure terms.

Return ONLY a JSON object. No markdown fences, no commentary.

{{
  "skills": [
    {{"skill": "...", "attribution": "...", "evidence": "..."}}
  ],
  "seniority": "...",
  "years_experience_min": null
}}

POSTING TITLE: {title}

POSTING:
{description}
"""

MAX_CHARS = 12000


def build(title: str, description: str) -> str:
    return TEMPLATE.format(title=title, description=description[:MAX_CHARS])
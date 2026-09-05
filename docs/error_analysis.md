# Error analysis — LLM attribution vs hand-labelled gold set

Gold set: 40 postings, 255 hand-labelled mentions (249 scorable, 6 spurious).
Common set: 229 mentions detected by both the gazetteer and the LLM.

| | Correct | Accuracy |
|---|---|---|
| Majority-class baseline (all `required`) | 175/229 | 76.4% |
| LLM | 200/229 | 87.3% |

29 disagreements. This document is a reading of all 29.

**No labels were revised after seeing model output.** Where the review below
finds the human label wrong, it is reported rather than corrected, so the
87.3% is if anything an understatement.

## The disagreements cluster; they are not 29 independent judgements

The 29 disagreements come from 11 postings, and they are concentrated: four
postings supply 22 of the 29, and three shared-context passages alone account
for 16 (five, five and six disagreements — Cases 1, 2 and 4 below). In each of
those passages a single sentence or heading listed several technologies, and
the human and the model read that one framing differently, producing five or
six disagreements that are really one judgement.

This matters for interpreting the headline number: mentions within a posting
are not independent, so the effective sample behind these errors is closer to
the number of distinct ambiguous passages than to 29.

## Case 1 — posting 3902355613: the model was right

Five disagreements (Bash, Java, Python, SQL, Spark), all human `required`,
model `preferred`. All five appear in one sentence, which introduces the list
as an example of technologies the candidate might be proficient in, hedged
with "open to", "for example" and "and the like".

The other five gazetteer terms in the same posting (AWS, Azure, Data
warehousing, ETL, Machine learning) appear in firm experience bullets and were
labelled `required` by both systems. The model therefore discriminated
*within* a single Qualifications block rather than applying one label to the
section. The human label followed the section heading; the model followed the
sentence. On review the model's reading is the better one.

## Case 2 — posting 3891283386: genuinely undecidable

Five disagreements (Excel, Python, SAS, SQL, Tableau), all human `required`,
model `preferred`, all from one sentence under Qualifications asking for
"reasonable familiarity with some statistical tools" and visualization tools
"such as" the named products.

The labelling protocol states that the section heading governs and that softer
phrasing inside a requirements block does not by itself demote a skill, so the
human label follows the protocol as written. The model read the hedging
instead. The posting does not decide between the two readings. This is
recorded as protocol ambiguity rather than as an error by either system.

## Case 3 — posting 3903440960: the model misapplied precedence

One disagreement: C#, human `preferred`, model `not_expected`. The source
sentence describes familiarity with C# or Visual Basic .NET as beneficial but
not required — both attributions apply to the same span.

The prompt states the precedence order `required > preferred > boilerplate >
not_expected`, which resolves this to `preferred`. The model detected the
negation correctly and then failed to apply the tie-break rule it was given.
This is a rule-following failure rather than a comprehension failure, and it
is the only instance of `not_expected` produced anywhere in the gold set.

## Case 4 — posting 3901905766: the model over-escalated a "Preferred" list

Eight disagreements, the largest cluster in the gold set, and they split into
two groups.

Six (AWS, Azure, Databricks, Kafka, SQL Server, Snowflake) are all human
`preferred`, model `required`. All six sit in one sentence under an explicit
**"Preferred Background:"** heading: "Strong ability to drive connections with
a wide variety of data platforms including AWS (Databricks, Teradata,
Snowflake, Kafka), Azure, DB2 and SQL Server, etc." The human label followed
the heading, as the protocol requires; the model read the strong action verb
("Strong ability to drive connections with…") as a hard requirement and ran
past the heading. Here the protocol backs the human, and the model
over-escalated — the mirror image of Case 1.

This one passage supplies six of the seven `preferred → required` transitions
in the entire gold set. The model's tendency to be *stricter* than the human
is therefore not a distributed pattern; it is concentrated in this single
posting.

The remaining two (Excel, SQL) are human `required`, model `boilerplate`, from
a bare "Tooling: Excel, SQL knowledge … desired" line. A tooling list with no
requirement verb is genuinely ambiguous between the two labels; this pair is
recorded as such rather than scored against either system.

## Aggregate direction

The 29 disagreements, by exact transition (gold → LLM):

| Transition | Count | Reading |
|---|---|---|
| `required` → `preferred` | 14 | model softer |
| `required` → `boilerplate` | 5 | model softer |
| `preferred` → `required` | 7 | model stricter |
| `boilerplate` → `required` | 2 | model stricter |
| `preferred` → `not_expected` | 1 | precedence misfire (Case 3) |

Grouped: the model is **softer** than the human label in 19 of 29
disagreements (it calls a gold-`required` skill `preferred` or `boilerplate`)
and **stricter** in 9. The split is directional, not balanced — but it is not
evidence that the model is worse. Ten of the 14 `required → preferred`
disagreements are Cases 1 and 2, where the model followed sentence-level
hedging that the human read past from the section heading; on review the model
is right in Case 1 and the text is undecidable in Case 2. And six of the nine
"stricter" disagreements are the single Case-4 passage.

The honest summary: the disagreements are almost entirely about the
`required` / `preferred` boundary on ambiguously-framed lists. The model
tracks sentence-level framing where the human tracks section headings. That
produces a lean toward demotion in raw counts, but once the errors are
grouped by the passage that caused them, neither system is systematically
stricter — they read the same definitions differently on genuinely ambiguous
text.

## Limits of this analysis

- `boilerplate` has 7 instances in the gold set and 6 in the common set, of
  which 4 were correct. Reported as a count; no accuracy is computed.
- `not_expected` has 0 gold instances. The class occurred 3 times in 55,088
  corpus mentions and could not be scored here.
- 282 of the LLM's 547 gold-set mentions (51.6%) are technologies outside the
  111-term gazetteer and are excluded from scoring in both directions.
- n=40 postings. Categorical results at this scale are indicative, not precise.
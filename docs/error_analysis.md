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

## The disagreements are sentence-level, not posting-level

The 29 disagreements are not spread evenly across skills or postings. Three
single sentences account for 15 of them. In each case one ambiguous sentence
listed several technologies, and the human and the model read that sentence's
framing differently — producing five or more disagreements that are really one
judgement.

This matters for interpreting the headline number: mentions within a posting
are not independent, so the effective sample behind these errors is closer to
the number of distinct ambiguous sentences than to 29.

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

## Aggregate direction

| Direction | Count |
|---|---|
| Human stricter than model (`required` → `preferred`/`boilerplate`) | 14 |
| Model stricter than human | 13 |
| `boilerplate` confusions in both directions | 2 |

The disagreements are close to balanced. A systematic bias in one direction
would suggest the two systems were working from different definitions; the
balance suggests they were working from the same definitions on genuinely
ambiguous text.

## Limits of this analysis

- `boilerplate` has 7 instances in the gold set and 6 in the common set, of
  which 4 were correct. Reported as a count; no accuracy is computed.
- `not_expected` has 0 gold instances. The class occurred 3 times in 55,088
  corpus mentions and could not be scored here.
- 282 of the LLM's 547 gold-set mentions (51.6%) are technologies outside the
  111-term gazetteer and are excluded from scoring in both directions.
- n=40 postings. Categorical results at this scale are indicative, not precise.
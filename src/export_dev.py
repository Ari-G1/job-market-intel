"""Writes docs/dev_postings.txt. The 10 prompt-development postings.

Disjoint from the gold 40 by construction (see freeze_sample.py). All prompt
iteration happens against these; the gold set is never read until evaluation.
"""
import textwrap

import pyarrow.parquet as pq

ids = [l.strip() for l in open("config/dev_ids.txt") if l.strip()]

df = pq.read_table(
    "data/silver_gazetteer",
    columns=["job_id", "title", "description_clean", "n_skills",
             "skills_gazetteer"],
).to_pandas()

g = df[df.job_id.isin(ids)].set_index("job_id").loc[ids].reset_index()

with open("docs/dev_postings.txt", "w", encoding="utf-8") as f:
    for i, r in g.iterrows():
        f.write("=" * 90 + "\n")
        f.write(f"[{i+1}/10] {r.job_id} | {r.title}\n")
        f.write(f"gazetteer ({r.n_skills}): {list(r.skills_gazetteer)}\n")
        f.write("=" * 90 + "\n")
        f.write(textwrap.fill(r.description_clean[:12000], width=90) + "\n\n")

print(f"wrote {len(g)} dev postings")
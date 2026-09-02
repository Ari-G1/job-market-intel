"""Writes docs/gold_postings.txt for hand-labelling. Wrapped for readability."""
import textwrap

import pyarrow.parquet as pq

ids = [l.strip() for l in open("config/gold_ids.txt") if l.strip()]

df = pq.read_table(
    "data/silver_gazetteer",
    columns=["job_id", "title", "description_clean", "n_skills",
             "skills_gazetteer", "formatted_experience_level"],
).to_pandas()

g = df[df.job_id.isin(ids)].set_index("job_id").loc[ids].reset_index()

with open("docs/gold_postings.txt", "w", encoding="utf-8") as f:
    for i, r in g.iterrows():
        f.write("=" * 90 + "\n")
        f.write(f"[{i+1}/40] {r.job_id} | {r.title}\n")
        f.write(f"exp={r.formatted_experience_level!r}\n")
        f.write(f"LABEL THESE ({r.n_skills}): {list(r.skills_gazetteer)}\n")
        f.write("=" * 90 + "\n")
        f.write(textwrap.fill(r.description_clean[:12000], width=90) + "\n\n")

print(f"wrote {len(g)} postings to docs/gold_postings.txt")
"""Draws the ~4,000-posting enrichment sample from the technical subset.

Excludes the 40 gold and 10 dev IDs. The gold set is enriched separately at
evaluation time so that its enrichment can be traced to a specific run; the
dev set is excluded because the prompt was tuned on it.

Proportional allocation here, unlike the gold set. This sample carries the
representativeness; the gold set carries the per-band measurement.
"""
import pyarrow.parquet as pq

SEED = 42
TARGET = 4000
MIN_SKILLS = 3

BANDS = {
    "Internship": "junior", "Entry level": "junior",
    "Associate": "mid", "Mid-Senior level": "mid",
    "Director": "senior", "Executive": "senior",
    "": "unspecified",
}

frozen = set()
for path in ("config/gold_ids.txt", "config/dev_ids.txt"):
    frozen |= {l.strip() for l in open(path) if l.strip()}
print(f"excluded (gold + dev): {len(frozen)}")

df = pq.read_table(
    "data/silver_gazetteer",
    columns=["job_id", "formatted_experience_level", "n_skills"],
).to_pandas()

sub = df[(df.n_skills >= MIN_SKILLS) & (~df.job_id.isin(frozen))].copy()
sub["band"] = sub.formatted_experience_level.map(BANDS)
print(f"eligible: {len(sub):,}")

frac = TARGET / len(sub)
sample = (sub.groupby("band", group_keys=False)
             .apply(lambda g: g.sample(max(1, round(len(g) * frac)),
                                       random_state=SEED)))

print(f"sampled: {len(sample):,}")
print(sample.band.value_counts().to_string())

sample.job_id.to_csv("config/enrich_ids.txt", index=False, header=False)
print("-> config/enrich_ids.txt")
"""
Freezes the gold and prompt-development sample IDs.

Run ONCE. The output files are committed to the repo and never regenerated.
Re-running with a different seed after seeing results would invalidate the
evaluation, so the seed is a constant in this file rather than an argument.

Selection happens before any prompt exists and before any result is seen.
That ordering is the point.
"""
import pyarrow.parquet as pq

SEED = 42
GOLD_PER_BAND = 10          # 4 bands x 10 = 40
DEV_TOTAL = 10              # disjoint from gold
MIN_SKILLS = 3

BANDS = {
    "Internship": "junior",
    "Entry level": "junior",
    "Associate": "mid",
    "Mid-Senior level": "mid",
    "Director": "senior",
    "Executive": "senior",
    "": "unspecified",
}

df = pq.read_table(
    "data/silver_gazetteer",
    columns=["job_id", "title", "formatted_experience_level", "n_skills"],
).to_pandas()

sub = df[df.n_skills >= MIN_SKILLS].copy()
sub["band"] = sub.formatted_experience_level.map(BANDS)

print(f"technical subset: {len(sub):,}")
print(sub.band.value_counts().to_string())
print()

# Equal allocation across bands, not proportional. At n=40 proportional
# allocation would leave ~2 senior postings, which supports no claim.
# The gold set measures attribution accuracy, not corpus composition.
gold = (sub.groupby("band", group_keys=False)
           .apply(lambda g: g.sample(GOLD_PER_BAND, random_state=SEED))
           .sort_values(["band", "job_id"]))

# Dev set drawn from what remains, so the two are disjoint by construction.
remaining = sub[~sub.job_id.isin(gold.job_id)]
dev = remaining.sample(DEV_TOTAL, random_state=SEED).sort_values("job_id")

assert len(gold) == 40, f"expected 40 gold postings, got {len(gold)}"
assert set(gold.job_id) & set(dev.job_id) == set(), "gold and dev overlap"

gold.job_id.to_csv("config/gold_ids.txt", index=False, header=False)
dev.job_id.to_csv("config/dev_ids.txt", index=False, header=False)

print(f"gold: {len(gold)} postings -> config/gold_ids.txt")
print(gold.band.value_counts().to_string())
print()
print(f"dev:  {len(dev)} postings -> config/dev_ids.txt")
print()
print("--- gold set ---")
for _, r in gold.iterrows():
    print(f"  {r.job_id}  {r.band:12s} {r.n_skills:2d}  {r.title[:50]}")
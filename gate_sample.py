"""Draw 20 postings for manual gate check 3. Seed and IDs are recorded."""
import pandas as pd

df = pd.read_csv("data/raw/postings.csv", dtype=str, keep_default_na=False,
                 na_values=[], usecols=["job_id", "title", "description",
                                        "formatted_experience_level"])
sample = df.sample(20, random_state=42)
sample[["job_id"]].to_csv("config/gate_sample_ids.txt", index=False, header=False)

for i, (_, r) in enumerate(sample.iterrows(), 1):
    print("=" * 78)
    print(f"[{i}]  {r['title']}  |  exp={r['formatted_experience_level']!r}  |  id={r['job_id']}")
    print("=" * 78)
    print(r["description"][:3000])
    print()
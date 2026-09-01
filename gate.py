"""Day 0 gate. Answers: does the four-class attribution premise hold?"""
import pandas as pd

CSV = "data/raw/postings.csv"

# --- 1. Column inventory. Sampled, because we only need names and shapes. ---
print("=" * 70)
print("COLUMN INVENTORY (first 5,000 rows)")
print("=" * 70)
head = pd.read_csv(CSV, dtype=str, keep_default_na=False, na_values=[], nrows=5000)
print(f"{len(head.columns)} columns\n")
for c in sorted(head.columns):
    nonblank = head[c].str.strip().ne("")
    ex = head.loc[nonblank, c].iloc[0][:65] if nonblank.any() else ""
    print(f"  {c:32s} blank={1 - nonblank.mean():6.1%}  eg={ex!r}")

# --- 2. Full load, only the columns the design depends on. ---
COLS = ["job_id", "title", "description", "formatted_experience_level"]
df = pd.read_csv(CSV, dtype=str, keep_default_na=False, na_values=[],
                 usecols=COLS, on_bad_lines="warn")

print("\n" + "=" * 70)
print("KEY FIELDS (full corpus)")
print("=" * 70)
print(f"rows parsed         : {len(df):,}")
print(f"blank descriptions  : {(df['description'].str.strip() == '').sum():,}")
print(f"duplicate job_ids   : {df['job_id'].duplicated().sum():,}")
print("\nformatted_experience_level:")
print(df["formatted_experience_level"].value_counts(dropna=False).to_string())
blank_exp = (df["formatted_experience_level"].str.strip() == "").mean()
print(f"\n  blank rate: {blank_exp:.1%}")

# --- 3. Description length + gate check 2. ---
d = df.loc[df["description"].str.strip() != "", "description"]
print("\n" + "=" * 70)
print("DESCRIPTION LENGTH")
print("=" * 70)
print(f"median chars: {d.str.len().median():,.0f}")
print(f"median words: {d.str.split().str.len().median():,.0f}")

PREFERRED = r"\b(a plus|nice[- ]to[- ]have|bonus|desirable|preferred|would be great|ideally)\b"
hits = d.str.contains(PREFERRED, case=False, regex=True)
print("\n" + "=" * 70)
print("GATE CHECK 2 - preferred-signal phrases")
print("=" * 70)
print(f"{hits.sum():,} / {len(d):,} = {hits.mean():.1%}")

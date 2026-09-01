"""Decompose the preferred-signal number. Is 56.2% real, or is 'bonus' compensation?"""
import pandas as pd

df = pd.read_csv("data/raw/postings.csv", dtype=str, keep_default_na=False,
                 na_values=[], usecols=["description"])
d = df.loc[df["description"].str.strip() != "", "description"]
n = len(d)

TERMS = {
    "a plus":         r"\ba plus\b",
    "nice to have":   r"\bnice[- ]to[- ]have\b",
    "bonus":          r"\bbonus\b",
    "desirable":      r"\bdesirable\b",
    "preferred":      r"\bpreferred\b",
    "would be great": r"\bwould be great\b",
    "ideally":        r"\bideally\b",
}

masks = {name: d.str.contains(pat, case=False, regex=True)
         for name, pat in TERMS.items()}

print(f"corpus: {n:,}\n")
for name, m in masks.items():
    print(f"  {name:16s} {m.sum():>7,}  {m.mean():6.1%}")

strict = ["a plus", "nice to have", "desirable", "would be great", "ideally"]
any_strict = masks[strict[0]].copy()
for t in strict[1:]:
    any_strict |= masks[t]

print("\nexcluding 'bonus' and 'preferred':")
print(f"  {any_strict.sum():,} / {n:,} = {any_strict.mean():.1%}")

only_bonus = masks["bonus"] & ~any_strict & ~masks["preferred"]
print(f"\nmatched ONLY by 'bonus' (likely compensation): {only_bonus.sum():,}")

print("\n--- 5 contexts around 'bonus' ---")
for s in d[masks["bonus"]].head(5):
    i = s.lower().find("bonus")
    print(" ..." + s[max(0, i - 90):i + 60].replace("\n", " ") + "...")

print("\n--- description length ---")
print(d.str.len().describe(percentiles=[.5, .9, .95, .99]).to_string())
print("over 20k chars:", (d.str.len() > 20000).sum())
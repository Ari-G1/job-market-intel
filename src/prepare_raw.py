"""
CSV -> JSONL. Source-format conversion only.

Deliberately does NOT clean: no HTML stripping, no dedupe, no language filter,
no whitespace normalisation. All of that belongs in the Spark stage between
bronze and silver. If cleaning leaks in here, Spark becomes a file-format
converter and the pipeline loses its transformation stage.
"""
import json
import pandas as pd

CSV_IN = "data/raw/postings.csv"
JSONL_OUT = "data/raw/postings.jsonl"

KEEP = [
    "job_id",
    "title",
    "company_name",
    "description",
    "location",
    "formatted_experience_level",
    "formatted_work_type",
    "remote_allowed",
    "listed_time",
]


def main():
    df = pd.read_csv(
        CSV_IN,
        dtype=str,                 # see note 1
        keep_default_na=False,     # see note 2
        na_values=[],
        usecols=KEEP,              # see note 3
        on_bad_lines="warn",
    )
    print(f"rows read: {len(df):,}")

    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        raise SystemExit(f"expected columns absent: {missing}")

    df = df[KEEP]

    # remote_allowed: "1.0" means remote, blank means not remote (not unknown).
    # Coerce to 0/1 int so the ES mapping gets a clean boolean-ish field
    # instead of a mix of "1.0" and "".
    df["remote_allowed"] = (df["remote_allowed"].str.strip() != "").astype(int)

    written = 0
    with open(JSONL_OUT, "w", encoding="utf-8") as f:
        for rec in df.to_dict(orient="records"):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1

    print(f"rows written: {written:,}")
    print(f"output: {JSONL_OUT}")


if __name__ == "__main__":
    main()
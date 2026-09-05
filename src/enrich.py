"""Enriches postings via the LLM. Writes one JSON file per posting.

Design notes:

- One file per posting, not one Parquet. A crash mid-run loses one posting,
  not the whole run, and a rerun skips what already exists. The Parquet is
  assembled afterwards from the files.
- Failures are written too, with an "error" field. A silently missing file
  and a failed call would otherwise be indistinguishable.
- Threaded because 4,000 sequential calls at ~3s each is over three hours.
  Eight workers is conservative; the bottleneck is the API, not the client.
"""
import os
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, "src")

import pyarrow.parquet as pq

from grounding import is_grounded, strip_fences
from llm_client import call_llm
from prompt import build
from schema import Extraction

OUT = Path(os.environ.get("ENRICH_OUT", "data/enriched_json"))
WORKERS = 8
MAX_TOKENS = 2500

def enrich_one(row) -> dict:
    """One posting -> one result dict. Never raises; failures are recorded."""
    out_path = OUT / f"{row.job_id}.json"
    if out_path.exists():
        return {"job_id": row.job_id, "status": "cached"}

    result = {"job_id": row.job_id, "title": row.title}

    for attempt in (1, 2):
        try:
            raw, usage = call_llm(build(row.title, row.description_clean),
                                  max_tokens=MAX_TOKENS)
            data = json.loads(strip_fences(raw))
            ext = Extraction(**data)
        except Exception as e:
            if attempt == 2:
                result |= {"status": "failed", "error": f"{type(e).__name__}: {e}"[:300]}
                out_path.write_text(json.dumps(result), encoding="utf-8")
                return result
            time.sleep(2)
            continue

        # Grounding is checked per mention. Ungrounded mentions are kept and
        # flagged, not dropped: the grounding rate is a reported result, and
        # discarding the failures would erase the number being reported.
        skills = []
        for s in ext.skills:
            skills.append({
                "skill": s.skill,
                "attribution": s.attribution,
                "evidence": s.evidence,
                "grounded": is_grounded(s.evidence, row.description_clean),
            })

        result |= {
            "status": "ok",
            "attempt": attempt,
            "skills": skills,
            "seniority": ext.seniority,
            "years_experience_min": ext.years_experience_min,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
        }
        out_path.write_text(json.dumps(result), encoding="utf-8")
        return result

    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    ids_file = os.environ.get("ENRICH_IDS", "config/enrich_ids.txt")
    ids = [l.strip() for l in open(ids_file) if l.strip()]
    df = pq.read_table(
        "data/silver_gazetteer",
        columns=["job_id", "title", "description_clean"],
    ).to_pandas()
    rows = list(df[df.job_id.isin(ids)].itertuples())
    print(f"to enrich: {len(rows):,}  (workers={WORKERS})", flush=True)

    counts = {"ok": 0, "failed": 0, "cached": 0}
    tok_in = tok_out = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(enrich_one, r) for r in rows]
        for i, f in enumerate(as_completed(futures), 1):
            res = f.result()
            counts[res["status"]] = counts.get(res["status"], 0) + 1
            tok_in += res.get("input_tokens", 0)
            tok_out += res.get("output_tokens", 0)
            if i % 100 == 0:
                el = time.time() - start
                rate = i / el
                eta = (len(rows) - i) / rate / 60
                print(f"{i:5,}/{len(rows):,}  ok={counts['ok']:,} "
                      f"failed={counts['failed']} cached={counts['cached']:,}  "
                      f"{rate:.1f}/s  eta {eta:.0f}m", flush=True)

    el = time.time() - start
    print()
    print(f"done in {el/60:.1f} min")
    print(f"ok={counts['ok']:,}  failed={counts['failed']}  cached={counts['cached']:,}")
    print(f"tokens: in={tok_in:,}  out={tok_out:,}")


if __name__ == "__main__":
    main()
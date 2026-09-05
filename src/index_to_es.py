"""Indexes enriched postings into Elasticsearch.

The sole writer to Elasticsearch. Spark writes Parquet only; mixing
elasticsearch-hadoop into a Spark job means matching connector JARs to the
Spark and ES versions, which is avoidable risk for no gain at this scale.

Three sources are joined here and kept distinct in the document:
  - silver_gazetteer Parquet : computed metadata and gazetteer skills
  - enriched_json            : LLM-generated attributions and seniority
  - embeddings/vectors.npy   : MiniLM vectors, normalized at encode time
"""
import glob
import json
import os

import numpy as np
import pyarrow.parquet as pq
from elasticsearch import Elasticsearch, helpers

INDEX = "postings"
SILVER = "data/silver_gazetteer"
ENRICHED = "data/enriched_json"
EMB_DIR = "data/embeddings"

vectors = np.load(os.path.join(EMB_DIR, "vectors.npy"))
emb_ids = [l.strip() for l in open(os.path.join(EMB_DIR, "job_ids.txt"))]
emb = dict(zip(emb_ids, vectors))
print("vectors loaded: %d" % len(emb))

cols = pq.read_table(SILVER).to_pydict()
meta = {}
for i in range(len(cols["job_id"])):
    job_id = str(cols["job_id"][i])
    if job_id not in emb:
        continue
    meta[job_id] = {
        "title": cols["title"][i],
        "description": cols["description_clean"][i],
        "company": cols["company_name"][i],
        "location": cols["location"][i],
        "work_type": cols["formatted_work_type"][i],
        "experience_level_source": cols["formatted_experience_level"][i],
        "skills_gazetteer": list(cols["skills_gazetteer"][i] or []),
        "n_skills": int(cols["n_skills"][i] or 0),
    }
print("metadata rows matched: %d" % len(meta))

def build_docs():
    n_skipped = 0
    for path in sorted(glob.glob(os.path.join(ENRICHED, "*.json"))):
        rec = json.load(open(path, encoding="utf-8"))
        if rec.get("status") != "ok":
            continue
        job_id = str(rec["job_id"])
        if job_id not in meta or job_id not in emb:
            n_skipped += 1
            continue
        buckets = {"required": [], "preferred": [],
                   "boilerplate": [], "not_expected": []}
        for s in rec.get("skills", []):
            buckets[s["attribution"]].append(s["skill"])
        doc = dict(meta[job_id])
        doc["job_id"] = job_id
        doc["seniority_llm"] = rec.get("seniority")
        doc["years_experience_min"] = rec.get("years_experience_min")
        doc["skills_required"] = buckets["required"]
        doc["skills_preferred"] = buckets["preferred"]
        doc["skills_boilerplate"] = buckets["boilerplate"]
        doc["skills_not_expected"] = buckets["not_expected"]
        doc["embedding"] = emb[job_id].tolist()
        yield {"_index": INDEX, "_id": job_id, "_source": doc}
    print("skipped for missing metadata or vector: %d" % n_skipped)

es = Elasticsearch("http://localhost:9200")
print("cluster reachable: %s" % es.ping())

ok, errors = helpers.bulk(es, build_docs(), chunk_size=200, raise_on_error=False)
print("indexed %d documents" % ok)
print("errors: %d" % len(errors))
for err in errors[:3]:
    print("  %s" % json.dumps(err)[:400])

es.indices.refresh(index=INDEX)
print("document count: %d" % es.count(index=INDEX)["count"])

hit = es.search(index=INDEX, size=1, source_excludes=["embedding", "description"])
print("")
print("sample document:")
print(json.dumps(hit["hits"]["hits"][0]["_source"], indent=2)[:800])
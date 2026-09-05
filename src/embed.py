"""Embeds enriched postings for kNN retrieval.

Embedded text is the title plus the LLM-extracted skill names, not the full
description: MiniLM truncates at 256 word-pieces and the median description is
far longer, so embedding raw descriptions would silently encode whichever
paragraph a posting happens to open with. Title plus skills fits the window and
is the content that determines whether a candidate matches.

Vectors are normalized at encode time so that cosine similarity in
Elasticsearch is a dot product over unit vectors.
"""
import glob
import json
import os

import numpy as np
from sentence_transformers import SentenceTransformer

SRC = "data/enriched_json"
OUT = "data/embeddings"
MODEL = "all-MiniLM-L6-v2"

records = []
for path in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    rec = json.load(open(path, encoding="utf-8"))
    if rec.get("status") != "ok":
        continue
    skills = [s["skill"] for s in rec.get("skills", [])]
    text = "%s. Skills: %s" % (rec.get("title", ""), ", ".join(skills))
    records.append((str(rec["job_id"]), text))

print("postings to embed: %d" % len(records))
print("example text: %s" % records[0][1][:160])

model = SentenceTransformer(MODEL)
texts = [t for _, t in records]
vectors = model.encode(
    texts,
    batch_size=64,
    normalize_embeddings=True,
    show_progress_bar=True,
)
print("vector shape: %s" % (vectors.shape,))

norms = np.linalg.norm(vectors, axis=1)
print("norm min %.4f max %.4f" % (norms.min(), norms.max()))

os.makedirs(OUT, exist_ok=True)
np.save(os.path.join(OUT, "vectors.npy"), vectors.astype("float32"))
with open(os.path.join(OUT, "job_ids.txt"), "w", encoding="utf-8") as f:
    for job_id, _ in records:
        f.write(job_id + "\n")
print("wrote %d vectors to %s" % (len(records), OUT))
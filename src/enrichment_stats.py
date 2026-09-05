"""Recompute enrichment statistics over data/enriched_json/.

One JSON file per posting. Aggregates status, grounding, attribution and token
counts, and dumps the distinct skill strings the model produced so the
unmapped-skill check can run against the gazetteer as a separate step.
"""
import json
import os
from collections import Counter

ENRICHED_DIR = "data/enriched_json"
OUT_DIR = "data/stats"
LABELS = ["required", "preferred", "boilerplate", "not_expected"]

n_files = 0
n_ok = 0
n_error = 0
n_mentions = 0
n_grounded = 0
n_zero_skill_postings = 0
input_tokens = 0
output_tokens = 0
attributions = Counter()
skill_strings = Counter()
error_ids = []

for name in sorted(os.listdir(ENRICHED_DIR)):
    if not name.endswith(".json"):
        continue
    with open(os.path.join(ENRICHED_DIR, name), "r", encoding="utf-8") as f:
        rec = json.load(f)
    n_files += 1
    if rec.get("status") != "ok":
        n_error += 1
        error_ids.append(str(rec.get("job_id", name)))
        continue
    n_ok += 1
    input_tokens += rec.get("input_tokens", 0)
    output_tokens += rec.get("output_tokens", 0)
    skills = rec.get("skills", [])
    if not skills:
        n_zero_skill_postings += 1
    for s in skills:
        n_mentions += 1
        attributions[s["attribution"]] += 1
        skill_strings[s["skill"]] += 1
        if s.get("grounded"):
            n_grounded += 1


def pct(part, whole):
    if whole == 0:
        return "n/a"
    return "%.1f%%" % (100.0 * part / whole)

print("files read              %d" % n_files)
print("status ok               %d" % n_ok)
print("status error            %d" % n_error)
print("postings with 0 skills  %d" % n_zero_skill_postings)
print("")
print("mentions                %d" % n_mentions)
print("grounded                %d   %s" % (n_grounded, pct(n_grounded, n_mentions)))
print("ungrounded              %d" % (n_mentions - n_grounded))
print("mean mentions/posting   %.2f" % (n_mentions / float(n_ok)))
print("")
print("attribution distribution, denominator %d mentions" % n_mentions)
for label in LABELS:
    print("  %-13s %6d   %s" % (label, attributions[label],
                                pct(attributions[label], n_mentions)))
off_schema = [k for k in attributions if k not in LABELS]
print("labels outside the schema: %s" % (off_schema if off_schema else "none"))
top = max(LABELS, key=lambda k: attributions[k])
print("majority class          %s at %.4f" % (top, attributions[top] / float(n_mentions)))
print("")
print("input tokens            %d" % input_tokens)
print("output tokens           %d" % output_tokens)
print("distinct skill strings  %d" % len(skill_strings))

os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "skill_strings.tsv"), "w", encoding="utf-8") as f:
    f.write("skill\tcount\n")
    for skill, count in skill_strings.most_common():
        f.write("%s\t%d\n" % (skill, count))
with open(os.path.join(OUT_DIR, "error_ids.txt"), "w", encoding="utf-8") as f:
    for jid in error_ids:
        f.write(jid + "\n")
print("")
print("wrote skill_strings.tsv and error_ids.txt to %s" % OUT_DIR)
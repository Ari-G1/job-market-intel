"""Scores LLM attributions against the hand-labelled gold set.

The gold universe is gazetteer-bounded: docs/gold_labels.tsv contains exactly
the terms the gazetteer detected in the 40 gold postings, so the gazetteer's
detections are read from that file rather than recomputed. Rows labelled
"spurious" are gazetteer matches that do not refer to the technology at all;
they count as baseline false positives and are excluded from attribution.
"""
import glob
import json
import os

from normalize import normalize

GOLD = "docs/gold_labels.tsv"
LLM_DIR = "data/gold"
OUT_PATH = "docs/results.txt"
CLASSES = ["required", "preferred", "boilerplate", "not_expected"]
PRECEDENCE = {c: i for i, c in enumerate(CLASSES)}

lines = []


def say(text=""):
    print(text)
    lines.append(text)


def pct(part, whole):
    if whole == 0:
        return "n/a"
    return "%.1f%%" % (100.0 * part / whole)

gold = {}
with open(GOLD, encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        job_id, skill, label = [p.strip() for p in line.split("|")]
        gold[(job_id, skill)] = label

gold_scorable = dict((k, v) for k, v in gold.items() if v in CLASSES)
gold_spurious = [k for k, v in gold.items() if v == "spurious"]
gold_ids = sorted(set(j for j, _ in gold))

llm = {}
llm_mentions = 0
llm_unmapped = 0
for path in sorted(glob.glob(os.path.join(LLM_DIR, "*.json"))):
    rec = json.load(open(path, encoding="utf-8"))
    job_id = str(rec["job_id"])
    for s in rec.get("skills", []):
        llm_mentions += 1
        terms = normalize(s["skill"])
        if not terms:
            llm_unmapped += 1
            continue
        for term in terms:
            key = (job_id, term)
            prev = llm.get(key)
            if prev is None or PRECEDENCE[s["attribution"]] < PRECEDENCE[prev]:
                llm[key] = s["attribution"]

say("=" * 64)
say("EVALUATION - %d gold postings, %d labelled mentions" % (len(gold_ids), len(gold)))
say("=" * 64)
say("")
say("gold: %d scorable, %d spurious (gazetteer false positives)"
    % (len(gold_scorable), len(gold_spurious)))
say("LLM:  %d mentions, %d mapped, %d unmapped (%s)"
    % (llm_mentions, llm_mentions - llm_unmapped, llm_unmapped,
       pct(llm_unmapped, llm_mentions)))
say("Unmapped mentions fall outside the gazetteer-bounded universe and are")
say("scored neither for nor against the LLM.")
say("")

gaz_tp, gaz_fp, gaz_fn = len(gold_scorable), len(gold_spurious), 0
llm_keys = set(llm)
llm_tp = len([k for k in gold_scorable if k in llm_keys])
llm_fn = len(gold_scorable) - llm_tp
llm_fp = len([k for k in llm_keys if k not in gold])


def prf(tp, fp, fn):
    p = tp / float(tp + fp) if tp + fp else 0.0
    r = tp / float(tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f

say("1. DETECTION over the gazetteer-bounded universe")
say("")
say("  %-11s %5s %5s %5s   %-10s %-10s %s"
    % ("system", "TP", "FP", "FN", "precision", "recall", "F1"))
for name, tp, fp, fn in [("gazetteer", gaz_tp, gaz_fp, gaz_fn),
                         ("LLM", llm_tp, llm_fp, llm_fn)]:
    p, r, f1 = prf(tp, fp, fn)
    say("  %-11s %5d %5d %5d   %-10.3f %-10.3f %.3f" % (name, tp, fp, fn, p, r, f1))
say("")
say("  The gazetteer's recall is 1.0 by construction - the universe is its own")
say("  output. Its %d false positives are the spurious rows. LLM detections of"
    % gaz_fp)
say("  canonical terms absent from the universe count against it.")
say("")

common = sorted([k for k in gold_scorable if k in llm])
base_correct = len([k for k in common if gold_scorable[k] == "required"])
llm_correct = len([k for k in common if llm[k] == gold_scorable[k]])

say("2. ATTRIBUTION ACCURACY on the common set (headline)")
say("")
say("  common set: %d mentions detected by both systems" % len(common))
say("  %-28s %4d/%-4d %s" % ("majority-class baseline", base_correct,
                             len(common), pct(base_correct, len(common))))
say("  %-28s %4d/%-4d %s" % ("LLM", llm_correct, len(common),
                             pct(llm_correct, len(common))))
say("")

e2e_base = len([k for k in gold_scorable if gold_scorable[k] == "required"])
e2e_llm = len([k for k in gold_scorable if k in llm and llm[k] == gold_scorable[k]])
say("3. END-TO-END ACCURACY over all %d scorable gold mentions" % len(gold_scorable))
say("")
say("  %-28s %4d/%-4d %s" % ("gazetteer + majority class", e2e_base,
                             len(gold_scorable), pct(e2e_base, len(gold_scorable))))
say("  %-28s %4d/%-4d %s" % ("LLM", e2e_llm, len(gold_scorable),
                             pct(e2e_llm, len(gold_scorable))))
say("")

say("4. CONFUSION MATRIX on the common set - gold down, LLM across")
say("")
say("  %-14s%s" % ("", "".join("%-14s" % c for c in CLASSES)))
for g in CLASSES:
    row = ""
    for pred in CLASSES:
        row += "%-14d" % len([k for k in common
                              if gold_scorable[k] == g and llm[k] == pred])
    say("  %-14s%s" % (g, row))
say("")
for c in CLASSES:
    n_gold = len([k for k in gold_scorable if gold_scorable[k] == c])
    n_com = len([k for k in common if gold_scorable[k] == c])
    n_hit = len([k for k in common if gold_scorable[k] == c and llm[k] == c])
    say("  %-13s gold %3d, in common set %3d, correct %3d" % (c, n_gold, n_com, n_hit))
say("")
say("n=%d postings, %d labelled mentions. Mentions within a posting are not"
    % (len(gold_ids), len(gold)))
say("independent; categorical results at this scale are indicative, not precise.")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
with open("docs/disagreements.tsv", "w", encoding="utf-8") as f:
    f.write("job_id\tskill\tgold\tllm\n")
    for key in common:
        if gold_scorable[key] != llm[key]:
            f.write("%s\t%s\t%s\t%s\n" % (key[0], key[1], gold_scorable[key], llm[key]))
print("")
print("wrote %s and docs/disagreements.tsv" % OUT_PATH)
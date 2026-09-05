# Job Market Intelligence & Semantic CV Matching

An end-to-end big-data pipeline that extracts each technology mention from job postings
**with its attribution** — required, preferred, boilerplate, or not-expected — evaluates that
against a keyword baseline, and uses the result to match a CV to postings and compute the
missing required skills.

Built for the Big Data and AI course. Pipeline: Kafka → Spark (medallion Bronze/Silver) →
gazetteer + LLM enrichment → Elasticsearch (`dense_vector` kNN) → Streamlit demo.

---

## Dataset

LinkedIn Job Postings (~124k rows, 493 MB CSV), from Kaggle:
<https://www.kaggle.com/datasets/arshkon/linkedin-job-postings>

Credit: dataset by Arsh Koneru (Kaggle, `arshkon/linkedin-job-postings`). Used under its Kaggle
licence for coursework.

The full dataset is **not** committed (it is gitignored). Download it from the link above and
place `postings.csv` under `data/raw/`. A small sample is included at `docs/sample_postings.jsonl`
so the format is visible without the full download.

---

## Prerequisites

- Windows + WSL2, Ubuntu 22.04 (the pipeline is developed and run inside WSL, not native Windows)
- Python 3.10
- Java 17 (`JAVA_HOME` set; PySpark 3.5 does not run on Java 21+)
- Docker Desktop with WSL integration enabled (runs Kafka and Elasticsearch)
- An Anthropic API key with available credit (for the enrichment step)

Keep the project on the Linux filesystem (`~/job-market-intel`), **not** under `/mnt/c/` —
crossing the Windows/Linux boundary is 10–20× slower for the repeated Parquet I/O.

---

## Setup

```bash
cd ~/job-market-intel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_ID=<model-id>      # read at import by src/llm_client.py
```

Start the infrastructure:

```bash
docker compose up -d          # Kafka + Elasticsearch
docker compose ps             # both services should be "running"/"healthy"
```

---

## Running the pipeline

Run from the project root with the virtualenv active. Each step writes to disk (Parquet/JSON) or
to Elasticsearch, so a later step can be re-run without repeating earlier ones. The evaluation
branch is deliberately separate from the product path — see below.

### 1 · Ingest → Bronze → Silver

```bash
python src/prepare_raw.py                 # format-only conversion: source CSV -> JSONL
python src/producer.py                    # publish all records to the Kafka topic jobs.raw
                                          #   (append a number, e.g. `python src/producer.py 100`,
                                          #    to publish a capped batch for a quick test)
python src/streaming_job.py               # Kafka -> Bronze (Spark Structured Streaming) -> data/bronze
python src/write_silver.py                # clean Bronze -> Silver (drop blank/short/non-English) -> data/silver
python src/gazetteer_udf.py               # deterministic 111-term match over Silver -> data/silver_gazetteer
```

The gazetteer output is both the keyword **baseline** and the technical study population
(postings with three or more matched terms).

### 2 · Freeze the label sets (before any prompt work)

```bash
python src/freeze_sample.py               # freezes the gold/dev selection by seed -> config/gold_ids.txt
python src/export_gold.py                 # exports the 40 gold postings for hand-labelling
python src/export_dev.py                  # exports the disjoint 10-posting prompt-development set
```

These are frozen first so the gold set is fixed before the prompt is tuned on the dev set.

### 3 · Sample & enrich

```bash
python src/sample_4k.py                   # draws the 4,000-posting enrichment subset from the technical population
python src/enrich.py                      # LLM attribution on the 4k subset -> data/enriched_json
```

### 4 · Product path (demo backend)

```bash
python src/embed.py                       # embed title + extracted skills with MiniLM (384-d, normalized) -> data/embeddings
python src/index_to_es.py                 # load enriched + embedded documents into Elasticsearch
```

> **Re-running from scratch:** delete `checkpoints/` before re-running the streaming step. Spark
> Structured Streaming records committed Kafka offsets there; a rerun that finds them will
> correctly believe it has already consumed the topic and silently produce nothing.

---

## Evaluation (separate from the product path)

Enrich the frozen gold set with the same code, then score it:

```bash
ENRICH_IDS=config/gold_ids.txt ENRICH_OUT=data/gold python src/enrich.py
python src/evaluate.py
```

`evaluate.py` prints detection F1, attribution accuracy on the common set, and end-to-end
accuracy — each alongside the majority-class baseline and with raw counts — and writes
`docs/results.txt` and `docs/disagreements.tsv`.

---

## Demo

```bash
streamlit run app.py
```

Paste or upload a CV, confirm the skills the LLM extracted, and the app retrieves the most
similar postings by vector kNN and shows, per posting, the missing **required** skills.

The skill gap is `required − confirmed_cv_skills` — deterministic set arithmetic (**computed**).
Any written advice is LLM output (**generated**), validated, and shown in a separate labelled
region. The distinction is kept visible throughout the UI.

---

## Responsible use

- The demo is exercised with a **synthetic / redacted CV**. No real personal data is sent to the
  Anthropic API.
- LLM output is validated, never trusted: a Pydantic schema (`extra: forbid`), a grounding check
  that the evidence span appears in the source text, and one retry before the record is dropped
  and logged.
- All results describe *this dataset*, not the labour market.

---

## Repository layout

```
job-market-intel/
├── docker-compose.yml          # Kafka + Elasticsearch
├── requirements.txt            # pinned (numpy<2, pyspark==3.5.1, kafka-python-ng, streamlit==1.36.0, ...)
├── .env                        # LLM_PROVIDER, ANTHROPIC_API_KEY, ANTHROPIC_MODEL_ID (gitignored)
├── config/
│   └── gold_ids.txt            # frozen 40-posting gold selection
├── src/
│   ├── prepare_raw.py  producer.py  streaming_job.py
│   ├── write_silver.py  gazetteer.py  gazetteer_udf.py
│   ├── freeze_sample.py  export_gold.py  export_dev.py  sample_4k.py
│   ├── enrich.py  llm_client.py  prompt.py  schema.py  grounding.py  normalize.py
│   ├── embed.py  index_to_es.py
│   ├── evaluate.py  enrichment_stats.py
│   └── (gate*.py — Day-0 milestone checks, not part of a normal run)
├── app.py                      # Streamlit demo
├── data/                       # gitignored
│   ├── raw/  (postings.csv, companies/ jobs/ mappings/)
│   ├── bronze/  silver/  silver_gazetteer/
│   ├── enriched/  enriched_json/  embeddings/
│   ├── gold/                    # gold-set enrichment output
│   └── stats/
└── docs/
    ├── sample_postings.jsonl
    ├── design_doc.md
    └── results.txt              # evaluation output
```

Gitignored: `.venv/`, `data/`, `.env`, `scratch/`, `spark-warehouse/`, `checkpoints/`,
`__pycache__/`.
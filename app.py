"""Streamlit demo: semantic CV -> job matching with a computed skill gap.

Flow:
  1. An LLM parses a CV into a skill list (reuses src/llm_client.call_llm).
  2. The user confirms/unchecks skills.
  3. The confirmed skills are embedded with the SAME model and text format as
     src/embed.py, and matched against the `postings` index by native
     Elasticsearch dense_vector kNN (cosine).
  4. Per matched posting, the missing required skills are computed as a set
     difference: skills_required - confirmed_skills. Deterministic, not generated.

The computed / generated boundary is kept visible: the skill gap is set
arithmetic (computed); the optional advice panel is LLM output (generated) and
is labelled as such.

Run from the project root:  streamlit run app.py
Requires: Elasticsearch up on localhost:9200 with the `postings` index loaded,
and .env present (ANTHROPIC_API_KEY, ANTHROPIC_MODEL_ID) for the CV parse.
"""
import os
import sys
import json

import numpy as np
import streamlit as st

# The pipeline scripts run as `python src/x.py`, which puts src/ on the path and
# imports siblings flat (e.g. `from llm_client import call_llm`). Mirror that so
# this app reuses the exact same LLM entry point rather than opening a second one.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from llm_client import call_llm  # noqa: E402

from sentence_transformers import SentenceTransformer  # noqa: E402
from elasticsearch import Elasticsearch  # noqa: E402

INDEX = "postings"
MODEL = "all-MiniLM-L6-v2"          # identical to src/embed.py; query and docs must share a model
ES_URL = "http://localhost:9200"
TOP_K = 8

# A synthetic CV. The brief forbids sending real personal data to a third-party
# API, so the demo ships with fabricated text and no real PII.
SYNTHETIC_CV = """Backend software engineer, 4 years experience building web services.
Built REST APIs in Python with Django and Flask. Data stored in PostgreSQL and
Redis. Containerised services with Docker and deployed on AWS. Comfortable with
Git, Linux, and writing unit tests. Some exposure to Kafka for event streaming."""

CV_PARSE_PROMPT = (
    "You extract technical skills from a CV.\n"
    "Return ONLY a JSON object, with no prose and no markdown fences, of the form:\n"
    '{"role": "<short role or headline, may be empty>", "skills": ["skill1", "skill2"]}\n'
    "List concrete technologies, languages, frameworks, databases and tools the person "
    "claims. Do not invent skills that are not in the text.\n\n"
    "CV:\n"
)


@st.cache_resource
def get_model():
    # cache_resource: load the model once per server process, not per rerun.
    return SentenceTransformer(MODEL)


@st.cache_resource
def get_es():
    return Elasticsearch(ES_URL)


def parse_json(text):
    """The model returns raw text; extract the JSON object defensively.

    Handles a plain object, one wrapped in ```json fences, or one with prose
    around it, by taking the first '{' through the last '}'. This is a lighter
    check than the pipeline's strict Pydantic schema -- adequate for a demo, and
    honestly labelled as such.
    """
    t = text.strip()
    i, j = t.find("{"), t.rfind("}")
    if i == -1 or j == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(t[i:j + 1])


def embed_query(role, skills):
    """Build the query text the SAME way src/embed.py built each document
    ("<title>. Skills: <comma-joined skills>") so the query vector lives in the
    same region of the space as the indexed documents, then normalize so cosine
    is a dot product over unit vectors."""
    if role:
        text = "%s. Skills: %s" % (role, ", ".join(skills))
    else:
        text = "Skills: %s" % ", ".join(skills)
    vec = get_model().encode([text], normalize_embeddings=True)[0]
    return vec.tolist()


def knn_search(qvec, k=TOP_K):
    """Native ES 8.x approximate kNN over the HNSW-indexed dense_vector field.
    num_candidates > k lets HNSW explore more nodes before returning the top k;
    source_excludes drops the 384-d vector so it isn't shipped back to the UI.
    Fetches extra hits so that filtering out empty-required postings still leaves
    roughly k results."""
    resp = get_es().search(
        index=INDEX,
        knn={
            "field": "embedding",
            "query_vector": qvec,
            "k": k * 2,
            "num_candidates": 100,
        },
        source_excludes=["embedding"],
        size=k * 2,
    )
    hits = resp["hits"]["hits"]
    # (a) drop postings with no extracted requirements — see note above.
    hits = [h for h in hits if h["_source"].get("skills_required")]
    return hits[:k]


# --------------------------------------------------------------------------- UI
st.set_page_config(page_title="Semantic CV Matching", layout="wide")
st.title("Semantic CV Matching")
st.caption(
    "MiniLM 384-d vectors, cosine kNN in Elasticsearch. "
    "The skill gap is computed set arithmetic; any advice is generated and labelled."
)

if "skills" not in st.session_state:
    st.session_state.skills = None
    st.session_state.role = ""

cv_text = st.text_area(
    "CV text  (synthetic sample provided — do not paste real personal data)",
    value=SYNTHETIC_CV,
    height=200,
)

if st.button("Extract skills"):
    with st.spinner("Parsing CV with the LLM…"):
        raw, _usage = call_llm(CV_PARSE_PROMPT + cv_text)
    try:
        parsed = parse_json(raw)
        st.session_state.skills = [s for s in parsed.get("skills", []) if isinstance(s, str)]
        st.session_state.role = parsed.get("role", "") or ""
    except Exception as e:  # noqa: BLE001
        st.session_state.skills = None
        st.error("Could not parse the LLM output as JSON: %s" % e)

if st.session_state.skills is not None:
    if not st.session_state.skills:
        st.warning("The LLM returned no skills. Try a CV with explicit technologies.")
    else:
        st.subheader("Confirm your skills")
        st.write(
            "The LLM extracted these. Uncheck anything you don't actually have — "
            "matches and gaps recompute automatically."
        )
        # Streamlit reruns the whole script on any widget change, so unchecking a
        # box recomputes the query, the kNN search, and every gap for free.
        confirmed = []
        cols = st.columns(3)
        for i, skill in enumerate(st.session_state.skills):
            with cols[i % 3]:
                if st.checkbox(skill, value=True, key="chk_%d" % i):
                    confirmed.append(skill)

        st.divider()

        if not confirmed:
            st.info("Confirm at least one skill to search.")
        else:
            qvec = embed_query(st.session_state.role, confirmed)
            try:
                hits = knn_search(qvec)
            except Exception as e:  # noqa: BLE001
                hits = []
                st.error("Elasticsearch query failed — is the cluster up on %s? %s" % (ES_URL, e))

            if hits:
                st.subheader("Top matches")
                confirmed_lower = {c.lower() for c in confirmed}
                for h in hits:
                    src = h["_source"]
                    required = src.get("skills_required", []) or []
                    # COMPUTED: set difference, case-insensitive on names.
                    missing = [s for s in required if s.lower() not in confirmed_lower]
                    have = [s for s in required if s.lower() in confirmed_lower]

                    with st.container(border=True):
                        st.markdown(
                            "**%s** — %s · %s"
                            % (src.get("title", ""), src.get("company", ""), src.get("location", ""))
                        )
                        st.caption("cosine score %.3f" % h["_score"])
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Required you have** (%d / %d)" % (len(have), len(required)))
                            st.write(", ".join(have) if have else "—")
                        with c2:
                            st.markdown("**Missing required**  ·  _computed: required − your skills_")
                            st.write(", ".join(missing) if missing else "none — full match on required")

                # -------------------------------------------------- generated panel
                with st.expander("Generated career advice (LLM output — not computed)"):
                    st.caption(
                        "This panel is generated by the LLM from the computed gap above. "
                        "It is kept visibly separate from the computed results."
                    )
                    if st.button("Generate advice for the top match"):
                        top = hits[0]["_source"]
                        top_missing = [
                            s for s in (top.get("skills_required", []) or [])
                            if s.lower() not in confirmed_lower
                        ]
                        prompt = (
                            "A candidate is applying for the role '%s'. They are missing these "
                            "required skills: %s. In 3 short bullet points, suggest how to close "
                            "the gap. Be concrete and brief."
                            % (top.get("title", ""), ", ".join(top_missing) or "none")
                        )
                        with st.spinner("Generating…"):
                            advice, _u = call_llm(prompt)
                        st.markdown(advice)
import json
import re
from pathlib import Path
import pickle
import hashlib
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util

# ==================================================
# Tokenizer
# ==================================================
STOPWORDS = {
    "the","a","an","to","be","is","are",
    "should","can","could","may","must",
    "of","for","on","in","at","by","with",
    "from","into","that","this","these",
    "those","please","whenever","possible"
}

def tokenize(text):

    if not text:
        return []

    tokens = re.findall(r"[A-Za-z0-9_]+", str(text).lower())

    return [
        t for t in tokens
        if t not in STOPWORDS
    ]

# def tokenize(text: str):
#     """
#     Tokenizer used by BM25.

#     Preserves identifiers like
#     E1
#     T10
#     Employee_ID
#     Task_ID
#     """
#     return re.findall(r"[A-Za-z0-9_]+", text.lower())


# ==================================================
# Load Examples
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
EXAMPLE_FILE = BASE_DIR / "dsl" / "examples.json"

with open(EXAMPLE_FILE, "r", encoding="utf-8") as f:
    EXAMPLES = json.load(f)


# ==================================================
# Build BM25 Index
# ==================================================

bm25_documents = []

for ex in EXAMPLES:

    document = f"""
    Family:
    {ex["family"]}

    Tags:
    {" ".join(ex["tags"])}

    User:
    {ex["user"]}

    DSL:
    {ex["dsl"]}
    """

    bm25_documents.append(tokenize(document))

bm25 = BM25Okapi(bm25_documents)


# ==================================================
# Build Embedding Index
# ==================================================

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

embedding_texts = []

for ex in EXAMPLES:

    embedding_texts.append(
        f"""
Family:
{ex["family"]}

Tags:
{" ".join(ex["tags"])}

User:
{ex["user"]}

DSL:
{ex["dsl"]}
"""
    )

example_embeddings = embedding_model.encode(
    embedding_texts,
    convert_to_tensor=True,
    normalize_embeddings=True,
)


# ==================================================
# Utilities
# ==================================================

def normalize(scores):
    """
    Min-Max normalization.
    """

    scores = np.asarray(scores, dtype=float)

    if scores.max() == scores.min():
        return np.ones_like(scores)

    return (scores - scores.min()) / (scores.max() - scores.min())


# ==================================================
# Hybrid Retrieval
# ==================================================

def retrieve_examples(
    user_query: str,
    top_k: int = 3,
    semantic_weight: float = 0.5,
    bm25_weight: float = 0.5,
):
    """
    Returns the top-k most relevant examples using
    Hybrid Retrieval (Semantic + BM25).
    """

    # ---------- BM25 ----------

    query_tokens = tokenize(user_query)

    bm25_scores = bm25.get_scores(query_tokens)

    bm25_scores = normalize(bm25_scores)

    # ---------- Semantic ----------

    query_embedding = embedding_model.encode(
        user_query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    semantic_scores = util.cos_sim(
        query_embedding,
        example_embeddings,
    )[0].cpu().numpy()

    semantic_scores = normalize(semantic_scores)

    # ---------- Hybrid Score ----------

    final_scores = (
        semantic_weight * semantic_scores
        + bm25_weight * bm25_scores
    )

    top_indices = np.argsort(final_scores)[::-1][:top_k]

    retrieved = []

    for idx in top_indices:

        example = EXAMPLES[idx].copy()

        example["score"] = round(float(final_scores[idx]), 4)

        retrieved.append(example)

    return retrieved


# ==================================================
# Prompt Formatting
# ==================================================

def format_examples(examples):
    """
    Converts retrieved examples into prompt text.
    """

    sections = []

    for i, ex in enumerate(examples, start=1):

        sections.append(
f"""
Example {i}

Family:
{ex["family"]}

Tags:
{", ".join(ex["tags"])}

User:
{ex["user"]}

DSL:
{ex["dsl"]}
"""
        )

    return "\n--------------------------------------------\n".join(sections)
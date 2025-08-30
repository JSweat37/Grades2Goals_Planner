"""
This file acts as our toolbox as it contains functions that are commonly used in the project
so that we do not have to copy/paste it across notebooks. 
"""

# Libraries
from pathlib import Path
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
from openai import OpenAI

#--- Project Paths
PROJECT_ROOT = Path("..").resolve()
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

SLIDES_CHUNKS_PATH = PROCESSED_FOLDER/ "slides_chunks.parquet"
LABS_CHUNKS_PATH   = PROCESSED_FOLDER / "labs_chunks.parquet"

CATALOG      = PROJECT_ROOT / "catalog"
RESOURCES_CATALOG = CATALOG / "resources_catalog.csv"
TOPIC_MASTER      = CATALOG / "topic_master.csv" 

FAISS_SLIDES_PATH  = PROCESSED_FOLDER / "faiss_slides.index"
FAISS_LABS_PATH    = PROCESSED_FOLDER / "faiss_labs.index"

 
# Additional Data Files 
DATA_RAW     = PROJECT_ROOT / "data" / "raw"
DATA_PROC    = PROJECT_ROOT / "data" / "processed"
DB_DIR       = PROJECT_ROOT / "db"


# --- Load data
def load_chunks():
    """Load processed slide and lab chunks into DataFrames."""
    slides_df = pd.read_parquet(SLIDES_CHUNKS_PATH).dropna(subset=["text"]).reset_index(drop=True)
    labs_df   = pd.read_parquet(LABS_CHUNKS_PATH).dropna(subset=["text"]).reset_index(drop=True)
    return slides_df, labs_df


# --- Embedding model
_embedder = SentenceTransformer("all-MiniLM-L6-v2")

def encode_texts(texts):
    """Turn text into vectors we can search with FAISS."""
    embeddings = _embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(embeddings, dtype="float32")


# --- Load FAISS indexes
def load_index(path):
    """Load a FAISS index (error if file not found)."""
    if not path.exists():
        raise FileNotFoundError(f"Missing index: {path}")
    return faiss.read_index(path.as_posix())


# --- Search helpers
def search_slides(slides_index, slides_df, query, top_k=5):
    """Search the slides index and return top matches as DataFrame."""
    query_vec = encode_texts([query])
    scores, idxs = slides_index.search(query_vec, top_k)

    rows = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0: 
            continue
        row = slides_df.iloc[idx]
        rows.append({
            "source": "slide",
            "file": row.get("file", ""),
            "page": row.get("page", ""),
            "text": row.get("text", ""),
            "score": float(score)
        })
    return pd.DataFrame(rows)


def search_labs(labs_index, labs_df, query, top_k=5):
    """Search the labs index and return top matches as DataFrame."""
    query_vec = encode_texts([query])
    scores, idxs = labs_index.search(query_vec, top_k)

    rows = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0: 
            continue
        row = labs_df.iloc[idx]
        rows.append({
            "source": "lab",
            "file": row.get("file", ""),
            "text": row.get("text", ""),
            "score": float(score)
        })
    return pd.DataFrame(rows)



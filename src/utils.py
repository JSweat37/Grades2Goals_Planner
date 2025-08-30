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
from dotenv import load_dotenv


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


def make_context(lab_matches, slide_matches):
    """
    Combine lab and slide search results into a single text block 
    that we can pass to the language model.
    
    Args:
        lab_matches (pd.DataFrame): results from search_labs()
        slide_matches (pd.DataFrame): results from search_slides()
    
    Returns:
        str: formatted context with numbered [CITATION] markers
    """

    # List to hold formatted text chunks
    context_texts = []

    # Start citation numbers at 1
    ref_number = 1       

    # --- Add lab matches first ---
    for _, row in lab_matches.iterrows():
        # Build one formatted line for this lab result
        line = f"[{ref_number}] (Lab file: {row['file']}) {row['text']}"
        context_texts.append(line)  # store the line
        ref_number += 1             # move to the next citation number

    # --- Add slide matches next ---
    for _, row in slide_matches.iterrows():
        # Build one formatted line for this slide result
        line = f"[{ref_number}] (Slide file: {row['file']} | Page {row['page']}) {row['text']}"
        context_texts.append(line)  # store the line
        ref_number += 1             # move to the next citation number

    # Join everything into one string with blank lines between
    return "\n\n".join(context_texts)


load_dotenv(override=True)  # take environment variables from .env file

# Create a single OpenAI client (reads key from environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_7_day_plan(feedback_text, slides_index, slides_df, labs_index, labs_df, top_k_slides=5, top_k_labs=5, model_name="gpt-4o-mini"): 
    """
    How it works:
    1) Search slides and labs separately.
    2) Concatenate the results (labs first by default since they are practical).
    3) Build a single context block with simple citations.
    4) Call OpenAI to write a 7-day plan with spaced review.
    5) Return the generated text.

    Args:
        feedback_text (str): Student's feedback, "I lost points on SQL joins and confusion matrix."
        top_k_slides (int): Number of slide chunks to include.
        top_k_labs   (int): Number of lab chunks to include.
        model_name   (str): OpenAI chat model.

    Returns:
        str: The study plan text generated by the LLM.
    """
    # Search slides and labs
    slides_results = search_slides(slides_index, slides_df, feedback_text, top_k=top_k_slides)
    labs_results   = search_labs(labs_index, labs_df, feedback_text, top_k=top_k_labs)

    # Make context
    context = make_context(labs_results, slides_results)

    system_prompt = (
        "You are an academic coach for a data science course. "
        "You must create a concrete 7-day micro-task plan using ONLY the provided context. "
        "Ensure tasks alternate between review (reading/notes), application (coding exercises), and reflection."
        "Each day should include 2–4 actionable tasks, with estimated time, and a citation line that points back to the source. "
        "Use spaced review on Day 1, Day 3, and Day 6. "
        "If context is insufficient for any part, state that clearly."
    )
    
    user_prompt = (
        f"Student feedback: {feedback_text}\n\n"
        f"Context from course materials (slides and labs):\n"
        f"{context}\n"
        "Now write the 7-day plan in this structure:\n"
        "Day 1 — Understand\n"
        "- Task 1 (est. 15–25 min) — description [CITATION]\n"
        "- Task 2 (est. 10–20 min) — description [CITATION]\n"
        "Day 2 — Apply\n"
        "- Task 1 ...\n"
        "...\n"
        "Day 7 — Checkpoint\n"
        "- Mini-quiz or small coding task ...\n"
        "\n"
        "Rules:\n"
        "- Use only facts available in the context above.\n"
        "- Each task line should end with a [CITATION] using the [SOURCE: ...] entry from context.\n"
        "- If something is unclear or missing, say so.\n"
    )

    # Call OpenAI chat completion
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,  # low temperature for focused output
        max_tokens=1000   # adjust as needed
    )

    return response.choices[0].message.content
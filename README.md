# Grades2Goals Planner (G2G)

> Your feedback. Your roadmap. Your success.  
> Because grades should guide, not just judge.  

Grades2Goals is more than a feedback tool — it’s a personal study coach.  
Instead of leaving students with just a score, G2G transforms feedback into **actionable 7-day micro-plans**. Each plan blends **review, practice, and reflection** so students know exactly what to focus on, how to improve, and when to revisit concepts.  

Grades don’t have to be the end of the story. With G2G, they’re just the beginning of growth.  

---

## Project Overview

Grades2Goals is a learning tool that converts rubric scores, quiz performance, and assignment feedback into **personalized 7-day micro-task study plans**.  

With semantic search and embeddings, G2G links feedback directly to course resources like **slides, labs, and the syllabus** — and extends learning with optional outside practice (e.g., Kaggle, LeetCode, or textbooks).  

This repo walks through the full pipeline:

- **Data preparation** — extract and chunk course data  
- **Embeddings + FAISS** — semantic search over slides and labs  
- **Study plan generation** — 7-day task-based roadmap with citations  
- **Practice generation** — quizzes, coding, and reflection tasks  
- **Progress tracking** — SQLite backend to enforce day-by-day completion  

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-org>/grades2goals_planner.git
   cd grades2goals_planner

2. Create and activate a virtual environment:
    ```bash 
    python -m venv venv
    source venv/bin/activate   # on Mac/Linux
    venv\Scripts\activate      # on Windows


3. Install dependencies:
     ```bash 
    pip install -r requirements.txt

4. Add your own OpenAI Key: Create a .env file in the project root:
    ```bash 
    OPENAI_API_KEY=your_api_key_here

## Data
**Sources**
- Course Materials (slides, labs, syllabus) — chunked into semantic indexes.
- Example Plans — generated with ChatGPT for testing and prototyping.
- Mock Data — cartoons, online resources, and external exercises used for inspiration.


**Structure**
- /data/raw → original slides, labs, and test JSON.
- /data/processed → parquet, structured JSON, and embeddings.
---


## Code Structure
grades2goals_planner/
│
├── data/
│   ├── raw/              # input syllabus, slides, labs
│   └── processed/        # processed chunks, indexes, plans
│
├──doc/                   # regex cheat sheet
│
│
├── catalog/              # resources catalog, topic master
│
├── src/
│   └── utils.py          # shared functions for search, embeddings, FAISS
│
├── notebooks/
│   ├── 01_prepare_chunks.ipynb   # extract + chunk syllabus/slides/labs
│   ├── 02_embed_index.ipynb      # build FAISS indexes
│   ├── 03_search_plan.ipynb      # generate 7-day plan from feedback
│   ├── 03.5_db_outline.ipynb     # draft SQLite schema outline
│   ├── 04_progress_tracker.ipynb # enforce day-by-day completion
│   ├── 05_practice_gen.ipynb     # generate quizzes, coding, reflection tasks
│   └── 06_streamlit_app.ipynb    # (optional) prototype app interface
│
├── requirements.txt
├── README.md
└── LICENSE
---

## How to Run the Notebooks

**Run the pipeline step by step:**

1. Prepare chunks

 Run 01_prepare_chunks.ipynb to extract text from syllabus, slides, and labs.

 Output: slides_chunks.parquet, labs_chunks.parquet.


2. Build indexes

 Run 02_embed_index.ipynb to embed text and build FAISS search indexes.

 Output: faiss_slides.index, faiss_labs.index.


3. Generate study plan

 Run 03_search_plan.ipynb. Provide sample feedback (e.g., “I lost points on SQL joins”).

 Output: a structured 7-day plan.


4. SQLite progress tracking

 Notebooks 03.5 + 04 handle storing plans in a database, enforcing daily progress rules.


5. Practice generation

 Run 05_practice_gen.ipynb. Converts study plan into quiz questions, coding tasks, and reflection prompts.


6. (Optional) App prototype

 Notebook 06_streamlit_app.ipynb shows how this could be wrapped into a Streamlit app.
---

## Results
- The pipeline successfully creates chunked resources (slides, labs, syllabus).
- FAISS search works reliably to pull the right chunks.
- Study plans are generated with clear daily tasks and citations
- Progress tracking + day-locking works in SQLite (prototype).
- Practice generation produces structured quizzes, coding tasks, and reflection exercises.
- App prototype in Notebook 6 is in progress.

**What works:**
- Semantic search from course materials.
- Plan generation from feedback.
- Practice content generation.
- SQLite progress enforcement.


**What’s in progress:**
- Streamlit UI integration.
- Expanded dataset testing with more students.
---

## Tools & Resources
- Python (pandas, numpy, sqlite3, faiss, sentence-transformers)
- OpenAI API for plan + practice generation
- Chatrooms & Online references for repo structure + workflows
- ChatGPT used to generate synthetic test data
- Kaggle, Datacamp, YouTube linked as external practice resources
---

## License 
This project is licensed under the MIT License.
*Disclaimer: We do not own any rights to the original course materials.
All content here was created solely for educational purposes.*

---
## Contributor 
**Adewale Thompson**
- Notebook 3.5: created initial SQLite task management system.
- Notebook 4: developed progress tracker with rules (can’t advance to next day until current complete).
- Wrote task completion logic and reporting for study plan tracking.

Jasmine Sweat 



**Julissa Morales**
- Designed repo structure (src/, data/raw/, data/processed/).
- Created syllabus → resource catalog pipeline.
- Built Notebooks 1, 2, 3, and 5.
- Generated test data, managed resources, and acted as the team’s go to lead.


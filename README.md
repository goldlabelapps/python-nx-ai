## I_Python

> Python with FastAPI using Postgres & tsvector. 

Open Source, production ready Python FastAPI/Postgres app for [NX](https://goldlabel.pro?s=python-nx-ai)

```sh
uvicorn app.main:app  --reload
```

#### Install

Create an environment file and add Postgres credentials etc

`cp .env.sample .env`

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is at <http://localhost:8000>.

[localhost](http://localhost:8000) | [Public RESTful API](https://nx-ai.onrender.com) 

- **Python 3.11+**
- **Postgres**
- **tsvector** - Superfast full-text search (with GIN index)
### Full-Text Search (tsvector)

The prospects table includes a `search_vector` column (type: tsvector) that is automatically computed from all text fields on insert. A GIN index is created for this column, enabling fast and scalable full-text search queries.

**How it works:**

- On every insert or update, the `search_vector` is computed from all text columns using PostgreSQL's `to_tsvector('english', ...)`.
- The GIN index (`idx_prospects_search_vector`) allows efficient search queries like:

```sql
SELECT * FROM prospects WHERE search_vector @@ plainto_tsquery('english', 'search terms');
```

This makes searching across all text fields in the prospects table extremely fast, even for large datasets.
- **FastAPI** — RESTful API framework
- **Uvicorn** — ASGI server
- **Pytest** — testing framework
- **HTTPX / TestClient**

#### Docs

FastAPI automatically generates interactive documentation:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Processing Large CSV Files

The `/prospects/process` endpoint is designed for robust, scalable ingestion of large CSV files (e.g., 1300+ rows, 300KB+). It follows the same normalization and insertion pattern as `/prospects/seed`, but is optimized for large files:

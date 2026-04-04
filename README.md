## Python FastAPI/Postgres App

> Production-ready, open-source FastAPI application with PostgreSQL and blazing-fast full-text search.

#### Project Overview

This project provides a scalable API backend using FastAPI and PostgreSQL, featuring:

- Automatic full-text search on all text fields (via tsvector)
- Endpoints for health checks, product management, prompt handling, and prospect management
- Efficient ingestion and processing of large CSV files

#### 🚀 Features

- **Python 3.11+**
- **FastAPI** — Modern, high-performance REST API
- **PostgreSQL** — Robust relational database
- **tsvector + GIN** — Superfast full-text search
- **Uvicorn** — Lightning-fast ASGI server
- **Pytest** — Comprehensive testing

#### Getting Started

### 1. Clone & Setup Environment

```bash
git clone <repo-url>
cd python
cp .env.sample .env  # Add your Postgres credentials and settings
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Run the App

```bash
uvicorn app.main:app --reload
```

Visit [localhost:8000](http://localhost:8000) or [onrender](https://nx-ai.onrender.com)

#### API Documentation

FastAPI auto-generates interactive docs:

- [Swagger UI](https://nx-ai.onrender.com/docs)
- [ReDoc](https://nx-ai.onrender.com/redoc)


## Full-Text Search (tsvector)

The `prospects` table includes a `search_vector` column (type: tsvector) computed from all text fields on insert/update. A GIN index enables fast, scalable full-text search:

```sql
SELECT * FROM prospects WHERE search_vector @@ plainto_tsquery('english', 'search terms');
```

**How it works:**
- On every insert/update, `search_vector` is computed using PostgreSQL's `to_tsvector('english', ...)`.
- The GIN index (`idx_prospects_search_vector`) enables efficient search across large datasets.


## Processing Large CSV Files

The `/prospects/process` endpoint supports robust ingestion of large CSVs (e.g., 1300+ rows, 300KB+), following the same normalization and insertion pattern as `/prospects/seed` but optimized for scale.


## Directory Structure

```
app/
	main.py           # FastAPI entrypoint
	api/              # API endpoints & schemas
		health.py
		root.py
		routes.py
		products/
		prompts/
		prospects/
		resend/
		utils/
	static/           # Static assets (e.g., repoicon.png)
	utils/            # Utility scripts
tests/              # Pytest test suite
requirements.txt    # Python dependencies
render.yaml         # Deployment config (Render.com)
```


## Contributing

Contributions welcome. Please open issues or submit pull requests.


## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

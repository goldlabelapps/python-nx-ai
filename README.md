## Python NX AI

> FastAPI/Python/Postgres/tsvector. 
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
- **tsvector** - Superfast search
- **FastAPI** — RESTful API framework
- **Uvicorn** — ASGI server
- **Pytest** — testing framework
- **HTTPX / TestClient**

FastAPI automatically generates interactive documentation:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

#### Structure

```
app/
  __init__.py
  main.py          # FastAPI application entry point
  api/
    __init__.py
    routes.py      # API endpoint definitions
tests/
  __init__.py
  test_routes.py   # Unit and integration tests
requirements.txt
```


#### Endpoints

| Method | Path      | Description                     |
|--------|-----------|---------------------------------|
| GET    | `/`       | Welcome message                 |
| GET    | `/health` | Health check — returns `ok`     |
| POST   | `/echo`   | Echoes the JSON `message` field |



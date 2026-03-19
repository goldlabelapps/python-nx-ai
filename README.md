# NX AI

A clean, production-ready and modular FastAPI application for [NX](https://goldlabel.pro?s=nx-ai) AI services.

```sh
# Start the development server
uvicorn app.main:app --reload
```

[Public RESTful API](https://nx-ai.onrender.com) 

## Interactive API Docs

FastAPI automatically generates interactive documentation:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Stack

- **Python 3.11+**
- **FastAPI** — RESTful API framework
- **Uvicorn** — ASGI server
- **Pytest** — testing framework
- **HTTPX / TestClient** — HTTP testing

## Structure

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

## Install and run

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload
```

The API will be available at <http://localhost:8000>.

## Endpoints

| Method | Path      | Description                     |
|--------|-----------|---------------------------------|
| GET    | `/`       | Welcome message                 |
| GET    | `/health` | Health check — returns `ok`     |
| POST   | `/echo`   | Echoes the JSON `message` field |

### Example — Echo

```bash
curl -X POST http://localhost:8000/echo \
     -H "Content-Type: application/json" \
     -d '{"message": "hello"}'
# {"echo":"hello"}
```

## Running Tests

```bash
pytest
```

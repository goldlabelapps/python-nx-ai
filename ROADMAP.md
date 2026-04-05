# Security Hardening Roadmap

This document tracks the planned hardening work for the Python / FastAPI + PostgreSQL service.
Items are grouped by priority and theme. Tick each box as it ships.

---

## Priority 1 — Critical (do first, block release if missing)

### 1.1 Authentication & Authorization
- [ ] Add API-key or JWT middleware that protects every route except `GET /health`
- [ ] Require the key/token via an `Authorization: Bearer <token>` header
- [ ] Return `401 Unauthorized` for missing credentials and `403 Forbidden` for invalid ones
- [ ] Gate destructive endpoints (`PUT /prospects/seed`, `PUT /prospects/process`, `PATCH /prospects/alter`) behind an additional admin scope or separate admin-only key

### 1.2 Rate Limiting
- [ ] Add `slowapi` (or equivalent) rate-limiting middleware
- [ ] Apply a global limit (e.g. 60 req / min per IP) on all routes
- [ ] Apply a tighter limit (e.g. 5 req / min) on `POST /llm` and `POST /resend` to prevent API-cost abuse
- [ ] Return `429 Too Many Requests` with a `Retry-After` header on breach

### 1.3 Input Validation & Dynamic SQL
- [ ] Replace the f-string `UPDATE` in `prospects.py` (`f"UPDATE prospects SET {', '.join(fields)} …"`) with an explicit allow-list mapping column names to parameterized fragments
- [ ] Audit `seed.py`, `process.py`, and `alter.py` for any user-controlled values injected into SQL strings; switch to parameterized queries or psycopg2 `sql.Identifier` helpers throughout
- [ ] Add `max_length` constraints to all string fields in Pydantic schemas (e.g. `subject`, `html` in `EmailRequest`)
- [ ] Validate and sanitise the `html` body of `POST /resend` to prevent stored XSS being forwarded in outbound emails

---

## Priority 2 — High (ship within the next sprint)

### 2.1 Secrets Management
- [ ] Move all secrets (`GEMINI_API_KEY`, `RESEND_API_KEY`, `DB_PASSWORD`) out of plain environment variables and into a secrets manager (e.g. Render Secret Files, AWS Secrets Manager, or HashiCorp Vault)
- [ ] Set `resend.api_key` lazily inside the request handler rather than at module import time to avoid the key being captured in memory dumps or early-boot logs
- [ ] Rotate all existing credentials after the new secrets path is in place
- [ ] Add a startup check that raises a clear error if any required secret is missing, rather than failing silently at request time

### 2.2 HTTPS & Security Headers
- [ ] Ensure the Render service enforces HTTPS and redirects HTTP → HTTPS
- [ ] Add `SecurityHeadersMiddleware` (or `starlette-exceptionhandlers`) to set:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy: default-src 'none'`
  - `Referrer-Policy: no-referrer`
- [ ] Narrow CORS to only the methods and headers actually needed (e.g. `allow_methods=["GET","POST","PATCH"]`, explicit `allow_headers` list) rather than `["*"]`

### 2.3 Error Handling & Information Leakage
- [ ] Centralise exception handling with a FastAPI `exception_handler`; return generic error messages to callers and log full stack traces server-side only
- [ ] Remove raw exception text from Gemini API errors that are currently returned in API responses
- [ ] Disable FastAPI's `/docs` and `/redoc` endpoints in production (`docs_url=None, redoc_url=None` in non-dev environments)
- [ ] Set `debug=False` (ensure uvicorn is not started with `--reload` in production)

---

## Priority 3 — Medium (next two sprints)

### 3.1 Dependency Management & Supply Chain
- [ ] Pin all dependencies to exact versions in `requirements.txt` (remove `>=` ranges) and commit a `pip-compile`-generated lockfile
- [ ] Add `pip-audit` (or `safety`) to the CI pipeline to fail builds on known-CVE dependencies
- [ ] Migrate from `psycopg2-binary` (pre-compiled, less auditable) to `psycopg2` built from source, or adopt `psycopg3`
- [ ] Replace the bare `unittest discover` test runner in CI with `pytest` and add a coverage gate (e.g. ≥ 80 %)

### 3.2 Logging & Observability
- [ ] Replace `print()` calls with structured logging via Python's `logging` module (JSON format for log aggregators)
- [ ] Ensure DB credentials, API keys, and user PII (email addresses) are never written to logs
- [ ] Add request-ID correlation (e.g. via `asgi-correlation-id`) so requests can be traced end-to-end
- [ ] Ship logs to a centralised store (e.g. Render Log Streams → Datadog / Logtail) with alerting on 5xx spikes

### 3.3 Database Hardening
- [ ] Create a dedicated DB user with the minimum required privileges (SELECT / INSERT / UPDATE on specific tables only; no DDL in production)
- [ ] Enforce SSL on the PostgreSQL connection (`sslmode=require` in `psycopg2.connect`)
- [ ] Add connection pooling (e.g. `pgBouncer` or `psycopg2`'s `ThreadedConnectionPool`) to prevent connection exhaustion
- [ ] Enable PostgreSQL audit logging (`pgaudit`) to record DDL and DML for compliance

### 3.4 Sensitive-Operation Controls
- [ ] Remove or protect the debug / admin utility endpoints from the public router:
  - `PUT /prospects/seed` (drops and recreates the table)
  - `PUT /prospects/process` (bulk inserts from a CSV)
  - `PATCH /prospects/alter` (drops columns)
- [ ] If these must remain, move them to a separate internal-only router with independent authentication and IP allowlisting

---

## Priority 4 — Low / Continuous (ongoing hygiene)

### 4.1 CI/CD Security
- [ ] Add CodeQL or Bandit static analysis to the GitHub Actions workflow
- [ ] Add `trivy` or `grype` container/dependency scanning step to CI
- [ ] Enable GitHub Dependabot for automated dependency PRs
- [ ] Require passing CI checks before merge on `staging` and `master` (branch protection rules)
- [ ] Sign commits (GPG) and enforce it via branch protection

### 4.2 API Design
- [ ] Version the API under `/v1/` prefix so breaking security changes can be rolled out without disrupting existing clients
- [ ] Add request size limits to `POST /resend` and `POST /llm` (e.g. `max_request_size` middleware) to prevent large-payload DoS
- [ ] Add response pagination caps — current `limit` max of 500 on search is high; reduce to 100 and require explicit opt-in for larger pages

### 4.3 Operational / Process
- [ ] Document the threat model and data classification for this service
- [ ] Schedule quarterly dependency audits and secret rotations
- [ ] Add runbook for incident response (key rotation, DB failover, API key revocation)

---

## Tracking

| Priority | Items | Done |
|----------|-------|------|
| 1 — Critical | 10 | 0 |
| 2 — High | 13 | 0 |
| 3 — Medium | 14 | 0 |
| 4 — Low | 11 | 0 |
| **Total** | **48** | **0** |

Update the table above as items are completed.

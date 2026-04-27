from fastapi import APIRouter, HTTPException, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

_SQL = [
    """
    CREATE TABLE IF NOT EXISTS github_accounts (
        id SERIAL PRIMARY KEY,
        github_user_id BIGINT UNIQUE,
        login TEXT UNIQUE,
        name TEXT,
        email TEXT,
        company TEXT,
        blog TEXT,
        location TEXT,
        bio TEXT,
        avatar_url TEXT,
        html_url TEXT,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        last_synced_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS github_repos (
        id BIGSERIAL PRIMARY KEY,
        github_repo_id BIGINT UNIQUE NOT NULL,
        account_login TEXT,
        name TEXT NOT NULL,
        full_name TEXT,
        private BOOLEAN NOT NULL DEFAULT FALSE,
        fork BOOLEAN NOT NULL DEFAULT FALSE,
        archived BOOLEAN NOT NULL DEFAULT FALSE,
        disabled BOOLEAN NOT NULL DEFAULT FALSE,
        default_branch TEXT,
        language TEXT,
        stargazers_count INTEGER,
        watchers_count INTEGER,
        forks_count INTEGER,
        open_issues_count INTEGER,
        size_kb INTEGER,
        pushed_at TIMESTAMPTZ,
        created_at_github TIMESTAMPTZ,
        updated_at_github TIMESTAMPTZ,
        html_url TEXT,
        api_url TEXT,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS github_gists (
        id BIGSERIAL PRIMARY KEY,
        gist_id TEXT UNIQUE NOT NULL,
        owner_login TEXT,
        description TEXT,
        public BOOLEAN,
        files_count INTEGER,
        comments_count INTEGER,
        html_url TEXT,
        api_url TEXT,
        created_at_github TIMESTAMPTZ,
        updated_at_github TIMESTAMPTZ,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS github_projects (
        id BIGSERIAL PRIMARY KEY,
        github_project_id BIGINT UNIQUE NOT NULL,
        owner_login TEXT,
        owner_type TEXT,
        name TEXT NOT NULL,
        body TEXT,
        state TEXT,
        number INTEGER,
        html_url TEXT,
        api_url TEXT,
        created_at_github TIMESTAMPTZ,
        updated_at_github TIMESTAMPTZ,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS github_resources (
        id BIGSERIAL PRIMARY KEY,
        account_login TEXT,
        resource_type TEXT NOT NULL,
        resource_id TEXT NOT NULL,
        resource_name TEXT,
        resource_url TEXT,
        is_private BOOLEAN,
        state TEXT,
        created_at_github TIMESTAMPTZ,
        updated_at_github TIMESTAMPTZ,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (resource_type, resource_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_github_resources_type ON github_resources (resource_type);",
    "CREATE INDEX IF NOT EXISTS idx_github_resources_account ON github_resources (account_login);",
    "CREATE INDEX IF NOT EXISTS idx_github_resources_payload ON github_resources USING GIN (payload);",
    "CREATE INDEX IF NOT EXISTS idx_github_repos_payload ON github_repos USING GIN (payload);",
    "CREATE INDEX IF NOT EXISTS idx_github_gists_payload ON github_gists USING GIN (payload);",
    "CREATE INDEX IF NOT EXISTS idx_github_projects_payload ON github_projects USING GIN (payload);",
]


@router.post("/api/github/createtable")
def create_github_tables(api_key: str = Depends(get_api_key)) -> dict:
    """POST /api/github/createtable: Create GitHub ingestion tables."""
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        for statement in _SQL:
            cur.execute(statement)
        conn.commit()
        meta = make_meta("success", "GitHub tables created")
        return {
            "meta": meta,
            "data": {
                "tables": [
                    "github_accounts",
                    "github_repos",
                    "github_gists",
                    "github_projects",
                    "github_resources",
                ]
            },
        }
    except Exception as e:
        if conn is not None:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

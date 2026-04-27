"""Sync live data from the GitHub API into local Postgres tables."""

import os
import json
from fastapi import APIRouter, HTTPException, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key
import httpx

router = APIRouter()

_GH_BASE = "https://api.github.com"


def _gh_headers() -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN env variable not set")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_all_pages(client: httpx.Client, url: str) -> list:
    """Follow GitHub pagination and return all items."""
    results = []
    while url:
        resp = client.get(url)
        resp.raise_for_status()
        results.extend(resp.json())
        url = resp.links.get("next", {}).get("url") or ""
    return results


@router.post("/api/github/sync")
def sync_github(api_key: str = Depends(get_api_key)) -> dict:
    """POST /api/github/sync: Pull live data from GitHub API and upsert into Postgres."""
    headers = _gh_headers()
    counts = {}

    with httpx.Client(headers=headers, timeout=30) as client:
        # --- Account / user profile ---
        user_resp = client.get(f"{_GH_BASE}/user")
        user_resp.raise_for_status()
        user = user_resp.json()
        login = user["login"]

        conn = get_db_connection_direct()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO github_accounts
                    (github_user_id, login, name, email, company, blog, location, bio,
                     avatar_url, html_url, payload, last_synced_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                ON CONFLICT (github_user_id) DO UPDATE SET
                    login = EXCLUDED.login,
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    company = EXCLUDED.company,
                    blog = EXCLUDED.blog,
                    location = EXCLUDED.location,
                    bio = EXCLUDED.bio,
                    avatar_url = EXCLUDED.avatar_url,
                    html_url = EXCLUDED.html_url,
                    payload = EXCLUDED.payload,
                    last_synced_at = NOW(),
                    updated_at = NOW();
                """,
                (
                    user["id"], login, user.get("name"), user.get("email"),
                    user.get("company"), user.get("blog"), user.get("location"),
                    user.get("bio"), user.get("avatar_url"), user.get("html_url"),
                    json.dumps({
                        "public_repos": user.get("public_repos"),
                        "followers": user.get("followers"),
                        "following": user.get("following"),
                        "created_at": user.get("created_at"),
                    }),
                ),
            )
            counts["accounts"] = 1

            # --- Repos ---
            repos = _get_all_pages(client, f"{_GH_BASE}/user/repos?per_page=100&type=all")
            for r in repos:
                cur.execute(
                    """
                    INSERT INTO github_repos
                        (github_repo_id, account_login, name, full_name, private, fork,
                         archived, disabled, default_branch, language, stargazers_count,
                         watchers_count, forks_count, open_issues_count, size_kb,
                         pushed_at, created_at_github, updated_at_github,
                         html_url, api_url, payload, synced_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                    ON CONFLICT (github_repo_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        full_name = EXCLUDED.full_name,
                        private = EXCLUDED.private,
                        fork = EXCLUDED.fork,
                        archived = EXCLUDED.archived,
                        disabled = EXCLUDED.disabled,
                        default_branch = EXCLUDED.default_branch,
                        language = EXCLUDED.language,
                        stargazers_count = EXCLUDED.stargazers_count,
                        watchers_count = EXCLUDED.watchers_count,
                        forks_count = EXCLUDED.forks_count,
                        open_issues_count = EXCLUDED.open_issues_count,
                        size_kb = EXCLUDED.size_kb,
                        pushed_at = EXCLUDED.pushed_at,
                        updated_at_github = EXCLUDED.updated_at_github,
                        html_url = EXCLUDED.html_url,
                        api_url = EXCLUDED.api_url,
                        payload = EXCLUDED.payload,
                        synced_at = NOW(),
                        updated_at = NOW();
                    """,
                    (
                        r["id"], login, r["name"], r["full_name"],
                        r.get("private", False), r.get("fork", False),
                        r.get("archived", False), r.get("disabled", False),
                        r.get("default_branch"), r.get("language"),
                        r.get("stargazers_count", 0), r.get("watchers_count", 0),
                        r.get("forks_count", 0), r.get("open_issues_count", 0),
                        r.get("size", 0), r.get("pushed_at"),
                        r.get("created_at"), r.get("updated_at"),
                        r.get("html_url"), r.get("url"),
                        json.dumps({
                            "topics": r.get("topics", []),
                            "license": r.get("license"),
                            "visibility": r.get("visibility"),
                            "description": r.get("description"),
                        }),
                    ),
                )
            counts["repos"] = len(repos)

            # --- Gists ---
            gists = _get_all_pages(client, f"{_GH_BASE}/gists?per_page=100")
            for g in gists:
                cur.execute(
                    """
                    INSERT INTO github_gists
                        (gist_id, owner_login, description, public, files_count,
                         comments_count, html_url, api_url,
                         created_at_github, updated_at_github, payload, synced_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                    ON CONFLICT (gist_id) DO UPDATE SET
                        description = EXCLUDED.description,
                        public = EXCLUDED.public,
                        files_count = EXCLUDED.files_count,
                        comments_count = EXCLUDED.comments_count,
                        updated_at_github = EXCLUDED.updated_at_github,
                        payload = EXCLUDED.payload,
                        synced_at = NOW(),
                        updated_at = NOW();
                    """,
                    (
                        g["id"], login, g.get("description"), g.get("public"),
                        len(g.get("files", {})), g.get("comments", 0),
                        g.get("html_url"), g.get("url"),
                        g.get("created_at"), g.get("updated_at"),
                        json.dumps({
                            "files": list(g.get("files", {}).keys()),
                            "forks_count": g.get("forks", 0),
                        }),
                    ),
                )
            counts["gists"] = len(gists)

            # --- Projects (classic REST v3) ---
            projects_resp = client.get(
                f"{_GH_BASE}/users/{login}/projects?per_page=100",
                headers={**headers, "Accept": "application/vnd.github.inertia-preview+json"},
            )
            projects = projects_resp.json() if projects_resp.status_code == 200 and isinstance(projects_resp.json(), list) else []
            for p in projects:
                cur.execute(
                    """
                    INSERT INTO github_projects
                        (github_project_id, owner_login, owner_type, name, body,
                         state, number, html_url, api_url,
                         created_at_github, updated_at_github, payload, synced_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                    ON CONFLICT (github_project_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        body = EXCLUDED.body,
                        state = EXCLUDED.state,
                        updated_at_github = EXCLUDED.updated_at_github,
                        payload = EXCLUDED.payload,
                        synced_at = NOW(),
                        updated_at = NOW();
                    """,
                    (
                        p["id"], login, "user", p.get("name"), p.get("body"),
                        p.get("state"), p.get("number"),
                        p.get("html_url"), p.get("url"),
                        p.get("created_at"), p.get("updated_at"),
                        json.dumps({"columns_url": p.get("columns_url")}),
                    ),
                )
            counts["projects"] = len(projects)

            # --- Starred repos → github_resources ---
            starred = _get_all_pages(client, f"{_GH_BASE}/user/starred?per_page=100")
            for s in starred:
                cur.execute(
                    """
                    INSERT INTO github_resources
                        (account_login, resource_type, resource_id, resource_name,
                         resource_url, is_private, state,
                         created_at_github, updated_at_github, payload, synced_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                    ON CONFLICT (resource_type, resource_id) DO UPDATE SET
                        resource_name = EXCLUDED.resource_name,
                        resource_url = EXCLUDED.resource_url,
                        payload = EXCLUDED.payload,
                        synced_at = NOW(),
                        updated_at = NOW();
                    """,
                    (
                        login, "starred_repo", str(s["id"]), s["full_name"],
                        s.get("html_url"), s.get("private", False), "active",
                        s.get("created_at"), s.get("updated_at"),
                        json.dumps({
                            "language": s.get("language"),
                            "stargazers_count": s.get("stargazers_count"),
                            "description": s.get("description"),
                        }),
                    ),
                )
            counts["starred"] = len(starred)

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cur.close()
            conn.close()

    return {
        "meta": make_meta("success", f"GitHub sync complete for @{login}"),
        "data": {"login": login, "synced": counts},
    }

"""Seed GitHub tables with realistic fake data."""

from app.utils.db import get_db_connection_direct
import json

_ACCOUNTS = [
    {
        "github_user_id": 1024001,
        "login": "milkyway-dev",
        "name": "Alex Milky",
        "email": "alex@milkyway.dev",
        "company": "Milky Way Digital",
        "blog": "https://milkyway.dev",
        "location": "San Francisco, CA",
        "bio": "Full-stack developer. Open source enthusiast.",
        "avatar_url": "https://avatars.githubusercontent.com/u/1024001",
        "html_url": "https://github.com/milkyway-dev",
        "payload": {"public_repos": 42, "followers": 318, "following": 97},
    },
    {
        "github_user_id": 1024002,
        "login": "nova-studios",
        "name": "Nova Studios",
        "email": "hello@novastudios.io",
        "company": "Nova Studios LLC",
        "blog": "https://novastudios.io",
        "location": "Austin, TX",
        "bio": "We build tools for creative teams.",
        "avatar_url": "https://avatars.githubusercontent.com/u/1024002",
        "html_url": "https://github.com/nova-studios",
        "payload": {"public_repos": 17, "followers": 540, "following": 12},
    },
    {
        "github_user_id": 1024003,
        "login": "byte-foundry",
        "name": "Byte Foundry",
        "email": "team@bytefoundry.io",
        "company": "Byte Foundry Inc.",
        "blog": "https://bytefoundry.io",
        "location": "London, UK",
        "bio": "Crafting high-performance APIs since 2015.",
        "avatar_url": "https://avatars.githubusercontent.com/u/1024003",
        "html_url": "https://github.com/byte-foundry",
        "payload": {"public_repos": 29, "followers": 210, "following": 45},
    },
]

_REPOS = [
    {
        "github_repo_id": 5001001,
        "account_login": "milkyway-dev",
        "name": "fastapi-starter",
        "full_name": "milkyway-dev/fastapi-starter",
        "private": False,
        "fork": False,
        "archived": False,
        "disabled": False,
        "default_branch": "main",
        "language": "Python",
        "stargazers_count": 284,
        "watchers_count": 284,
        "forks_count": 61,
        "open_issues_count": 4,
        "size_kb": 1240,
        "pushed_at": "2026-04-20T14:32:00Z",
        "created_at_github": "2023-06-01T09:00:00Z",
        "updated_at_github": "2026-04-20T14:32:00Z",
        "html_url": "https://github.com/milkyway-dev/fastapi-starter",
        "api_url": "https://api.github.com/repos/milkyway-dev/fastapi-starter",
        "payload": {"topics": ["fastapi", "python", "starter-template"]},
    },
    {
        "github_repo_id": 5001002,
        "account_login": "nova-studios",
        "name": "canvas-kit",
        "full_name": "nova-studios/canvas-kit",
        "private": False,
        "fork": False,
        "archived": False,
        "disabled": False,
        "default_branch": "main",
        "language": "TypeScript",
        "stargazers_count": 912,
        "watchers_count": 912,
        "forks_count": 143,
        "open_issues_count": 11,
        "size_kb": 8800,
        "pushed_at": "2026-04-25T10:15:00Z",
        "created_at_github": "2022-11-14T08:00:00Z",
        "updated_at_github": "2026-04-25T10:15:00Z",
        "html_url": "https://github.com/nova-studios/canvas-kit",
        "api_url": "https://api.github.com/repos/nova-studios/canvas-kit",
        "payload": {"topics": ["canvas", "design-system", "typescript"]},
    },
    {
        "github_repo_id": 5001003,
        "account_login": "byte-foundry",
        "name": "pg-lightning",
        "full_name": "byte-foundry/pg-lightning",
        "private": False,
        "fork": False,
        "archived": False,
        "disabled": False,
        "default_branch": "main",
        "language": "Go",
        "stargazers_count": 1537,
        "watchers_count": 1537,
        "forks_count": 220,
        "open_issues_count": 7,
        "size_kb": 4300,
        "pushed_at": "2026-04-22T18:45:00Z",
        "created_at_github": "2021-03-08T12:00:00Z",
        "updated_at_github": "2026-04-22T18:45:00Z",
        "html_url": "https://github.com/byte-foundry/pg-lightning",
        "api_url": "https://api.github.com/repos/byte-foundry/pg-lightning",
        "payload": {"topics": ["postgres", "performance", "go"]},
    },
]

_GISTS = [
    {
        "gist_id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "owner_login": "milkyway-dev",
        "description": "FastAPI dependency injection pattern for Postgres",
        "public": True,
        "files_count": 2,
        "comments_count": 5,
        "html_url": "https://gist.github.com/milkyway-dev/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "api_url": "https://api.github.com/gists/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "created_at_github": "2025-09-10T11:00:00Z",
        "updated_at_github": "2025-09-12T08:30:00Z",
        "payload": {"forks_count": 3, "files": ["db.py", "example.py"]},
    },
    {
        "gist_id": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
        "owner_login": "nova-studios",
        "description": "Tailwind CSS dark mode toggle snippet",
        "public": True,
        "files_count": 1,
        "comments_count": 2,
        "html_url": "https://gist.github.com/nova-studios/b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
        "api_url": "https://api.github.com/gists/b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
        "created_at_github": "2025-12-01T15:20:00Z",
        "updated_at_github": "2025-12-03T09:00:00Z",
        "payload": {"forks_count": 1, "files": ["dark-mode.js"]},
    },
    {
        "gist_id": "c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6",
        "owner_login": "byte-foundry",
        "description": "Go connection pool tuning for high-throughput Postgres",
        "public": False,
        "files_count": 3,
        "comments_count": 0,
        "html_url": "https://gist.github.com/byte-foundry/c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6",
        "api_url": "https://api.github.com/gists/c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6",
        "created_at_github": "2026-01-18T07:45:00Z",
        "updated_at_github": "2026-01-18T07:45:00Z",
        "payload": {"forks_count": 0, "files": ["pool.go", "config.go", "README.md"]},
    },
]

_PROJECTS = [
    {
        "github_project_id": 9001001,
        "owner_login": "milkyway-dev",
        "owner_type": "user",
        "name": "API Roadmap 2026",
        "body": "Tracking all planned API features and improvements for 2026.",
        "state": "open",
        "number": 1,
        "html_url": "https://github.com/users/milkyway-dev/projects/1",
        "api_url": "https://api.github.com/projects/9001001",
        "created_at_github": "2025-12-15T10:00:00Z",
        "updated_at_github": "2026-04-18T14:00:00Z",
        "payload": {"columns_count": 4},
    },
    {
        "github_project_id": 9001002,
        "owner_login": "nova-studios",
        "owner_type": "organization",
        "name": "Canvas Kit v3",
        "body": "Planning board for the Canvas Kit v3 major release.",
        "state": "open",
        "number": 3,
        "html_url": "https://github.com/orgs/nova-studios/projects/3",
        "api_url": "https://api.github.com/projects/9001002",
        "created_at_github": "2026-01-05T09:30:00Z",
        "updated_at_github": "2026-04-23T11:00:00Z",
        "payload": {"columns_count": 5},
    },
    {
        "github_project_id": 9001003,
        "owner_login": "byte-foundry",
        "owner_type": "organization",
        "name": "Q2 Infrastructure Sprint",
        "body": "DevOps and infrastructure tasks for Q2 2026.",
        "state": "closed",
        "number": 7,
        "html_url": "https://github.com/orgs/byte-foundry/projects/7",
        "api_url": "https://api.github.com/projects/9001003",
        "created_at_github": "2026-03-01T08:00:00Z",
        "updated_at_github": "2026-04-01T17:30:00Z",
        "payload": {"columns_count": 3},
    },
]

_RESOURCES = [
    {
        "account_login": "milkyway-dev",
        "resource_type": "release",
        "resource_id": "rel-milkyway-001",
        "resource_name": "v2.4.0",
        "resource_url": "https://github.com/milkyway-dev/fastapi-starter/releases/tag/v2.4.0",
        "is_private": False,
        "state": "published",
        "created_at_github": "2026-03-10T12:00:00Z",
        "updated_at_github": "2026-03-10T12:00:00Z",
        "payload": {"tag_name": "v2.4.0", "prerelease": False, "assets_count": 2},
    },
    {
        "account_login": "nova-studios",
        "resource_type": "workflow",
        "resource_id": "wf-nova-042",
        "resource_name": "CI / Test Suite",
        "resource_url": "https://github.com/nova-studios/canvas-kit/actions/workflows/ci.yml",
        "is_private": False,
        "state": "active",
        "created_at_github": "2023-01-20T09:00:00Z",
        "updated_at_github": "2026-04-25T10:15:00Z",
        "payload": {"path": ".github/workflows/ci.yml", "badge_url": "https://github.com/nova-studios/canvas-kit/actions/workflows/ci.yml/badge.svg"},
    },
    {
        "account_login": "byte-foundry",
        "resource_type": "discussion",
        "resource_id": "disc-byte-019",
        "resource_name": "RFC: Connection pool strategy",
        "resource_url": "https://github.com/byte-foundry/pg-lightning/discussions/19",
        "is_private": False,
        "state": "open",
        "created_at_github": "2026-02-14T16:00:00Z",
        "updated_at_github": "2026-04-10T08:20:00Z",
        "payload": {"category": "Ideas", "answer_chosen": False, "comments_count": 12},
    },
]


def seed():
    conn = get_db_connection_direct()
    cur = conn.cursor()

    for r in _ACCOUNTS:
        cur.execute(
            """
            INSERT INTO github_accounts
                (github_user_id, login, name, email, company, blog, location, bio,
                 avatar_url, html_url, payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (github_user_id) DO NOTHING;
            """,
            (r["github_user_id"], r["login"], r["name"], r["email"], r["company"],
             r["blog"], r["location"], r["bio"], r["avatar_url"], r["html_url"],
             json.dumps(r["payload"])),
        )

    for r in _REPOS:
        cur.execute(
            """
            INSERT INTO github_repos
                (github_repo_id, account_login, name, full_name, private, fork, archived,
                 disabled, default_branch, language, stargazers_count, watchers_count,
                 forks_count, open_issues_count, size_kb, pushed_at,
                 created_at_github, updated_at_github, html_url, api_url, payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (github_repo_id) DO NOTHING;
            """,
            (r["github_repo_id"], r["account_login"], r["name"], r["full_name"],
             r["private"], r["fork"], r["archived"], r["disabled"], r["default_branch"],
             r["language"], r["stargazers_count"], r["watchers_count"], r["forks_count"],
             r["open_issues_count"], r["size_kb"], r["pushed_at"], r["created_at_github"],
             r["updated_at_github"], r["html_url"], r["api_url"], json.dumps(r["payload"])),
        )

    for r in _GISTS:
        cur.execute(
            """
            INSERT INTO github_gists
                (gist_id, owner_login, description, public, files_count, comments_count,
                 html_url, api_url, created_at_github, updated_at_github, payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (gist_id) DO NOTHING;
            """,
            (r["gist_id"], r["owner_login"], r["description"], r["public"],
             r["files_count"], r["comments_count"], r["html_url"], r["api_url"],
             r["created_at_github"], r["updated_at_github"], json.dumps(r["payload"])),
        )

    for r in _PROJECTS:
        cur.execute(
            """
            INSERT INTO github_projects
                (github_project_id, owner_login, owner_type, name, body, state, number,
                 html_url, api_url, created_at_github, updated_at_github, payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (github_project_id) DO NOTHING;
            """,
            (r["github_project_id"], r["owner_login"], r["owner_type"], r["name"],
             r["body"], r["state"], r["number"], r["html_url"], r["api_url"],
             r["created_at_github"], r["updated_at_github"], json.dumps(r["payload"])),
        )

    for r in _RESOURCES:
        cur.execute(
            """
            INSERT INTO github_resources
                (account_login, resource_type, resource_id, resource_name, resource_url,
                 is_private, state, created_at_github, updated_at_github, payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (resource_type, resource_id) DO NOTHING;
            """,
            (r["account_login"], r["resource_type"], r["resource_id"], r["resource_name"],
             r["resource_url"], r["is_private"], r["state"], r["created_at_github"],
             r["updated_at_github"], json.dumps(r["payload"])),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Seeded 3 rows into each GitHub table.")


if __name__ == "__main__":
    seed()

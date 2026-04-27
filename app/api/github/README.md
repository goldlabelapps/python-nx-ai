## GitHub

We are going to use this route to get data from our GitHub account using their API. We'll be storing that info in the Postgres DB, but have not created any tables yet.

### Create Table Route

**POST /api/github/createtable**

Hits this URL to create the GitHub tables in Postgres. Each table is created with `IF NOT EXISTS`, so it is safe to call multiple times — existing tables and data will not be affected.

### Proposed Table Design

1. github_accounts
- One row per GitHub account/user profile.
- Stores account identity fields and full raw payload.

2. github_repos
- One row per repository.
- Stores common repo analytics fields plus raw JSON payload.

3. github_gists
- One row per gist.
- Stores gist metadata plus raw JSON payload.

4. github_projects
- One row per project.
- Stores project metadata plus raw JSON payload.

5. github_resources
- Generic catch-all for any future GitHub resource type.
- Supports "everything else" from the API without migrations for every new object type.

### Why this shape works

- Normalized for common entities you asked for: repos, gists, projects.
- Flexible for all additional GitHub objects through jsonb payload storage.
- Indexes on resource type, account, and payload for filtering and search.



# Flickr API Integration

This module provides API routes for accessing and syncing Flickr data, mirroring the GitHub integration. It expects the following environment variables in your `.env` file:

- `FLICKR_USER`
- `FLICKR_KEY`
- `FLICKR_SECRET`

## Endpoints

- **GET /flickr**: Returns counts and recent records from all Flickr tables.
- **POST /flickr/createtable**: Drops all Flickr tables if they exist, then recreates them with the correct schema and constraints.
- **POST /flickr/emptytables**: Deletes all rows from all Flickr tables (does not drop tables).
- **POST /flickr/sync**: Fetches public photos for the configured Flickr user and stores them in the database.

## Table Design

1. **flickr_accounts**
   - One row per Flickr account/user profile.
   - Stores account identity fields and full raw payload.
2. **flickr_photos**
   - One row per photo.
   - `flickr_id` is unique.
   - Stores photo metadata plus raw JSON payload.
3. **flickr_albums**
   - One row per album.
   - Stores album metadata plus raw JSON payload.
4. **flickr_resources**
   - Generic catch-all for any future Flickr resource type.
   - Supports additional Flickr objects through jsonb payload storage.

## Notes

- The `/flickr/createtable` endpoint will **drop all Flickr tables** before recreating them. Use with caution—this will erase all Flickr data.
- The `/flickr/sync` endpoint currently fetches public photos for the configured user and inserts them into `flickr_photos`.
- The structure and endpoints are designed for consistency and flexibility, matching the GitHub integration.

# YouTube API Integration

This module provides API routes for accessing YouTube channel data, similar to the GitHub and Flickr integrations. It expects the following environment variable in your `.env` file:

- YOUTUBE_API_KEY

## Endpoints

- **GET /youtube**: Returns counts and recent records from all YouTube tables.

## Proposed Table Design

1. youtube_channels
   - One row per YouTube channel.
   - Stores channel identity fields and full raw payload.
2. youtube_videos
   - One row per video.
   - Stores video metadata plus raw JSON payload.
3. youtube_playlists
   - One row per playlist.
   - Stores playlist metadata plus raw JSON payload.
4. youtube_resources
   - Generic catch-all for any future YouTube resource type.
   - Supports additional YouTube objects through jsonb payload storage.

This structure mirrors the GitHub and Flickr integrations for consistency and flexibility.

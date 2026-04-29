from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta
from app.utils.api_key_auth import get_api_key
import os
import requests
import json
from dotenv import load_dotenv

router = APIRouter()

@router.post("/youtube/sync")
def sync_youtube(api_key: str = Depends(get_api_key)) -> dict:
    """POST /youtube/sync: Fetches data from YouTube Data API and stores in DB."""
    load_dotenv()
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_key:
        return {"meta": make_meta("error", "Missing YouTube API key"), "data": {}}

    # Example: Fetch channel info and latest videos for a given channel ID
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")  # Optionally add this to .env
    if not channel_id:
        return {"meta": make_meta("error", "Missing YOUTUBE_CHANNEL_ID in .env"), "data": {}}

    try:
        # Fetch channel details
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        channel_params = {
            "part": "snippet,contentDetails,statistics",
            "id": channel_id,
            "key": youtube_key
        }
        channel_resp = requests.get(channel_url, params=channel_params)
        channel_resp.raise_for_status()
        channel_data = channel_resp.json()
        channel_items = channel_data.get("items", [])
        if channel_items:
            channel = channel_items[0]
        else:
            return {"meta": make_meta("error", "Channel not found"), "data": {}}

        # Insert channel info
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO youtube_channels (youtube_id, title, payload)
            VALUES (%s, %s, %s)
            ON CONFLICT (youtube_id) DO NOTHING;
            """,
            (channel.get("id"), channel["snippet"].get("title"), json.dumps(channel))
        )

        # Fetch latest videos from uploads playlist
        uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        playlist_params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": 100,
            "key": youtube_key
        }
        playlist_resp = requests.get(playlist_url, params=playlist_params)
        playlist_resp.raise_for_status()
        playlist_data = playlist_resp.json()
        videos = playlist_data.get("items", [])
        for video in videos:
            video_id = video["contentDetails"]["videoId"]
            title = video["snippet"].get("title")
            cur.execute(
                """
                INSERT INTO youtube_videos (youtube_id, title, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (youtube_id) DO NOTHING;
                """,
                (video_id, title, json.dumps(video))
            )
        conn.commit()
        cur.close()
        conn.close()
        return {"meta": make_meta("success", f"Synced {len(videos)} videos from YouTube"), "data": {"count": len(videos)}}
    except Exception as e:
        return {"meta": make_meta("error", f"Sync error: {str(e)}"), "data": {}}

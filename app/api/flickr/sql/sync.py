from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta
from app.utils.api_key_auth import get_api_key
import os
import requests
import json
from dotenv import load_dotenv

router = APIRouter()

@router.post("/flickr/sync")
def sync_flickr(api_key: str = Depends(get_api_key)) -> dict:
    """POST /flickr/sync: Fetches data from Flickr API and stores in DB."""
    load_dotenv()
    flickr_user = os.getenv("FLICKR_USER")
    flickr_key = os.getenv("FLICKR_KEY")
    flickr_secret = os.getenv("FLICKR_SECRET")
    if not flickr_user or not flickr_key or not flickr_secret:
        return {"meta": make_meta("error", "Missing Flickr API credentials"), "data": {}}

    # Example: Fetch public photos for the user
    url = "https://api.flickr.com/services/rest/"
    params = {
        "method": "flickr.people.getPublicPhotos",
        "api_key": flickr_key,
        "user_id": flickr_user,
        "format": "json",
        "nojsoncallback": 1,
        "per_page": 100
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        photos = data.get("photos", {}).get("photo", [])
        conn = get_db_connection_direct()
        cur = conn.cursor()
        for photo in photos:
            cur.execute(
                """
                INSERT INTO flickr_photos (flickr_id, title, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (flickr_id) DO NOTHING;
                """,
                (photo.get("id"), photo.get("title"), json.dumps(photo))
            )
        conn.commit()
        cur.close()
        conn.close()
        return {"meta": make_meta("success", f"Synced {len(photos)} photos from Flickr"), "data": {"count": len(photos)}}
    except Exception as e:
        return {"meta": make_meta("error", f"Sync error: {str(e)}"), "data": {}}

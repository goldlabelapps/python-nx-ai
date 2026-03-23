from app import __version__
from fastapi import APIRouter
from fastapi import status
import os, time
import psycopg2
from dotenv import load_dotenv
from app import __version__

router = APIRouter()

@router.get("/products")
def root() -> dict:
    """Return a structured welcome message for the API root, including product data."""
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, price, in_stock, created_at FROM product;')
    products = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]),
            "in_stock": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()

    load_dotenv()
    base_url = os.getenv("BASE_URL", "http://localhost:8000")

    epoch = int(time.time() * 1000)
    meta = {
        "severity": "success",
        "title": "Product List",
        "version": __version__,
        "base_url": base_url,
        "time": epoch,
    }
    return {"meta": meta, "data": products}

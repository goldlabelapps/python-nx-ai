import os
import psycopg2
from dotenv import load_dotenv
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/products/reset", status_code=status.HTTP_200_OK)
def reset_products() -> dict:
    """Delete and recreate the product table, then seed with initial data."""
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    # Drop and recreate table
    cur.execute('''
        DROP TABLE IF EXISTS product;
        CREATE TABLE product (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price NUMERIC(10,2) NOT NULL,
            in_stock BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    # Seed data
    seed_products = [
        ("Apple", "Fresh red apple", 0.99, True),
        ("Banana", "Organic banana", 0.59, True),
        ("Orange", "Juicy orange", 1.29, True),
    ]
    cur.executemany(
        "INSERT INTO product (name, description, price, in_stock) VALUES (%s, %s, %s, %s);",
        seed_products
    )
    conn.commit()
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
    return {"message": "Product table reset and seeded.", "data": products}
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

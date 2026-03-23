from fastapi import APIRouter, status
import os, csv, time
from app.api.db import get_db_connection
from app import __version__

router = APIRouter()

@router.get("/products/update", status_code=status.HTTP_202_ACCEPTED)
def update_products() -> dict:
    """Process the large big_data.csv file to update products."""
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/big_data.csv'))
    process_csv(csv_path)
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    epoch = int(time.time() * 1000)
    meta = {
        "severity": "info",
        "title": "Product update from big_data.csv started",
        "version": __version__,
        "base_url": base_url,
        "time": epoch,
    }
    return {"meta": meta, "data": {"filename": "big_data.csv"}}

def process_csv(csv_path: str):
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute(
                """
                UPDATE product SET
                    Params=%(Params)s,
                    title=%(desc)s,
                    UOS=%(UOS)s,
                    Pack_Description=%(Pack_Description)s,
                    Hierarchy1=%(Hierarchy1)s,
                    Hierarchy2=%(Hierarchy2)s,
                    Hierarchy3=%(Hierarchy3)s,
                    UOP=%(UOP)s,
                    sSell1=%(sSell1)s,
                    sSell2=%(sSell2)s,
                    sSell3=%(sSell3)s,
                    sSell4=%(sSell4)s,
                    sSell5=%(sSell5)s,
                    pack1=%(pack1)s,
                    pack2=%(pack2)s,
                    pack3=%(pack3)s,
                    pack4=%(pack4)s,
                    pack5=%(pack5)s,
                    EAN=%(EAN)s
                WHERE item=%(item)s OR EAN=%(EAN)s
                """,
                row
            )
    conn.commit()
    cur.close()
    conn.close()

import os
import psycopg2
from dotenv import load_dotenv
import random

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT', '5432'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
)
cur = conn.cursor()
lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
for i in range(5):
    cur.execute(
        'INSERT INTO llm (vector, prompt, completion, duration, data) VALUES (%s, %s, %s, %s, %s);',
        ([random.random() for _ in range(1536)], lorem, lorem, random.uniform(0.1, 2.0), '{}')
    )
conn.commit()
print('Inserted 5 records.')
cur.close()
conn.close()

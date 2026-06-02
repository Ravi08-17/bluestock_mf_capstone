import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
conn = sqlite3.connect(BASE_DIR / "data" / "db" / "bluestock_mf.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(fact_nav);")
print("Columns in fact_nav table:")
for col in cursor.fetchall():
    print(f" - {col[1]}")

conn.close()
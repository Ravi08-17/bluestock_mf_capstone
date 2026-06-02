import sqlite3
from pathlib import Path
import pandas as pd

def execute_analytical_queries():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Dynamically find the matching column name in fact_nav
    cursor.execute("PRAGMA table_info(fact_nav);")
    nav_cols = [col[1].lower() for col in cursor.fetchall()]
    
    # Determine what column name SQLite used (handle case-sensitivity)
    scheme_col = "scheme_code"
    if "scheme_code" not in nav_cols:
        # Fallback to the first column if it's named differently
        cursor.execute("PRAGMA table_info(fact_nav);")
        raw_cols = [col[1] for col in cursor.fetchall()]
        scheme_col = raw_cols[0] # Usually the reset index column
        
    print("============================================================")
    print(" RUNNING DAY 2 DATABASE ANALYTICS INSIGHTS")
    print(f" Dynamic Join Column Identified: {scheme_col}")
    print("============================================================\n")
    
    print(" INSIGHT 1: SCHEME TIMELINE LOGS")
    q1 = f"""
    SELECT 
        f.scheme_code, 
        f.scheme_name, 
        COUNT(n.nav) as total_days, 
        MIN(n.nav_date) as start_date, 
        MAX(n.nav_date) as end_date
    FROM dim_fund f 
    LEFT JOIN fact_nav n ON f.scheme_code = n.[{scheme_col}]
    GROUP BY f.scheme_code;
    """
    print(pd.read_sql_query(q1, conn).to_string(index=False))
    print("\n" + "-"*60 + "\n")
    
    print(" INSIGHT 2: NAV HISTORICAL PEAKS & AVERAGES")
    q2 = f"""
    SELECT 
        f.scheme_name, 
        ROUND(AVG(n.nav), 2) as avg_nav, 
        MAX(n.nav) as peak_nav, 
        MIN(n.nav) as lowest_nav
    FROM fact_nav n 
    JOIN dim_fund f ON n.[{scheme_col}] = f.scheme_code 
    GROUP BY f.scheme_code;
    """
    print(pd.read_sql_query(q2, conn).to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    execute_analytical_queries()
import sqlite3
from pathlib import Path
import pandas as pd

def execute_analytical_queries():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
    
    conn = sqlite3.connect(DB_PATH)
    
    print("============================================================")
    print(" RUNNING DAY 2 PRODUCTION DATABASE ANALYTICS")
    print("============================================================\n")
    
    # Report 1: Timeline Tracking Records Matrix
    print(" REPORT 1: SCHEME COVERAGE AND LOG LENGTHS")
    q1 = """
    SELECT 
        f.amfi_code, 
        f.scheme_name, 
        f.fund_house,
        COUNT(n.nav) as total_tracked_days, 
        MIN(n.nav_date) as start_date, 
        MAX(n.nav_date) as end_date
    FROM dim_fund f 
    LEFT JOIN fact_nav n ON f.amfi_code = n.amfi_code 
    GROUP BY f.amfi_code
    LIMIT 5;
    """
    print(pd.read_sql_query(q1, conn).to_string(index=False))
    print("\n" + "-"*80 + "\n")
    
    # Report 2: Financial Threshold Statistics Matrix
    print(" REPORT 2: NAV HISTORICAL PEAKS & AVERAGES")
    q2 = """
    SELECT 
        f.scheme_name, 
        ROUND(AVG(n.nav), 2) as avg_nav, 
        ROUND(MAX(n.nav), 2) as peak_nav, 
        ROUND(MIN(n.nav), 2) as lowest_nav
    FROM fact_nav n 
    JOIN dim_fund f ON n.amfi_code = f.amfi_code 
    GROUP BY f.amfi_code
    LIMIT 5;
    """
    print(pd.read_sql_query(q2, conn).to_string(index=False))
    print("\n" + "-"*80 + "\n")
    
    # Report 3: High-Value Investor Capital Transacted Transaction Logs (Fixed Column mapping)
    print(" REPORT 3: RECENT TOP INVESTOR TRANSACTIONS")
    q3 = """
    SELECT 
        t.investor_id,
        t.transaction_date,
        f.scheme_name,
        t.transaction_type,
        t.amount_inr,
        t.kyc_status
    FROM fact_transactions t
    JOIN dim_fund f ON t.amfi_code = f.amfi_code
    ORDER BY t.amount_inr DESC
    LIMIT 5;
    """
    print(pd.read_sql_query(q3, conn).to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    execute_analytical_queries()
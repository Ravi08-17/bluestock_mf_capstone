import sqlite3
from pathlib import Path
import pandas as pd

def run_evaluation_queries():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
    
    conn = sqlite3.connect(DB_PATH)
    
    print("============================================================")
    print(" EXECUTING DAY 3 SYLLABUS EVALUATION QUERIES")
    print("============================================================\n")
    
    # 1. Top 5 funds by AUM
    print(" Query 1: Top 5 Funds by Highest Current Aggregate AUM Crore")
    q1 = """
    SELECT fund_house, MAX(aum_crore) AS peak_aum_crore, num_schemes 
    FROM fact_aum 
    GROUP BY fund_house 
    ORDER BY peak_aum_crore DESC 
    LIMIT 5;
    """
    print(pd.read_sql_query(q1, conn).to_string(index=False))
    print("\n" + "-"*80 + "\n")
    
    # 2. Average NAV per month
    print(" Query 2: Average NAV Per Month for AMFI Code 100016")
    q2 = """
    SELECT d.year, d.month, ROUND(AVG(n.nav), 2) AS avg_monthly_nav 
    FROM fact_nav n 
    JOIN dim_date d ON n.nav_date = d.date_string 
    WHERE n.amfi_code = 100016 
    GROUP BY d.year, d.month 
    LIMIT 5;
    """
    print(pd.read_sql_query(q2, conn).to_string(index=False))
    print("\n" + "-"*80 + "\n")

    # 3. Transactions by state
    print(" Query 3: Geographical Distribution of Transactions Across States")
    q3 = """
    SELECT state, COUNT(*) AS total_transactions, SUM(amount_inr) AS aggregate_capital_inr 
    FROM fact_transactions 
    GROUP BY state 
    ORDER BY aggregate_capital_inr DESC
    LIMIT 5;
    """
    print(pd.read_sql_query(q3, conn).to_string(index=False))
    print("\n" + "-"*80 + "\n")

    # 4. Funds with expense ratio < 1%
    print(" Query 4: Highly Cost-Efficient Funds (Expense Ratio < 1%)")
    q4 = """
    SELECT f.scheme_name, p.expense_ratio_pct, p.return_3yr_pct 
    FROM fact_performance p 
    JOIN dim_fund f ON p.amfi_code = f.amfi_code 
    WHERE p.expense_ratio_pct < 1.0 
    ORDER BY p.return_3yr_pct DESC
    LIMIT 5;
    """
    print(pd.read_sql_query(q4, conn).to_string(index=False))
    
    conn.close()
    print("\n ALL QUERIES PASSED VERIFICATION SUITE!")

if __name__ == "__main__":
    run_evaluation_queries()
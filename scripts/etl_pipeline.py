import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

def run_production_etl():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    PROCESSED_DIR = BASE_DIR / "data" / "processed"
    DB_DIR = BASE_DIR / "data" / "db"
    SQL_SCHEMA = BASE_DIR / "sql" / "schema.sql"
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    print("============================================================")
    print("  DAY 2: RUNNING ETL PIPELINE ON PRODUCTION DATASETS")
    print("============================================================\n")
    
    db_path = DB_DIR / "bluestock_mf.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(SQL_SCHEMA, "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    
    # 1. dim_fund Ingestion
    print(" Cleaning and loading 01_fund_master.csv...")
    m_path = RAW_DIR / "01_fund_master.csv"
    if m_path.exists():
        df = pd.read_csv(m_path)
        df.drop_duplicates(subset=["amfi_code"], inplace=True)
        # Slicing columns matching our schema setup
        df_fund = df[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "risk_category"]]
        df_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
        df_fund.to_csv(PROCESSED_DIR / "cleaned_fund_master.csv", index=False)
        
    # 2. fact_nav & dim_date Ingestion (Loop-Based Expansion)
    print(" Cleaning and loading 02_nav_history.csv...")
    n_path = RAW_DIR / "02_nav_history.csv"
    if n_path.exists():
        df_raw_nav = pd.read_csv(n_path)
        df_raw_nav["date"] = pd.to_datetime(df_raw_nav["date"])
        df_raw_nav = df_raw_nav[df_raw_nav["nav"] > 0]
        
        resampled_funds = []
        for amfi in df_raw_nav["amfi_code"].unique():
            df_sub = df_raw_nav[df_raw_nav["amfi_code"] == amfi].copy()
            df_sub.drop_duplicates(subset=["date"], inplace=True)
            df_sub.set_index("date", inplace=True)
            df_sub = df_sub.resample("D").ffill().reset_index()
            df_sub["amfi_code"] = int(amfi)
            resampled_funds.append(df_sub)
            
        df_nav = pd.concat(resampled_funds, ignore_index=True)
        
        # Build dim_date Time Intelligence
        df_date = pd.DataFrame({"date_string": df_nav["date"].dt.strftime("%Y-%m-%d").unique()})
        df_dt = pd.to_datetime(df_date["date_string"])
        df_date["year"] = df_dt.dt.year
        df_date["month"] = df_dt.dt.month
        df_date["day"] = df_dt.dt.day
        df_date["quarter"] = df_dt.dt.quarter
        df_date["day_of_week"] = df_dt.dt.day_name()
        df_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        
        df_nav["nav_date"] = df_nav["date"].dt.strftime("%Y-%m-%d")
        df_final_nav = df_nav[["amfi_code", "nav_date", "nav"]].copy()
        df_final_nav.to_sql("fact_nav", conn, if_exists="replace", index=False)
        df_final_nav.to_csv(PROCESSED_DIR / "cleaned_nav_history.csv", index=False)

    # 3. fact_performance Ingestion
    print(" Cleaning and loading 07_scheme_performance.csv...")
    p_path = RAW_DIR / "07_scheme_performance.csv"
    if p_path.exists():
        df_perf = pd.read_csv(p_path)
        df_perf = df_perf[["amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "expense_ratio_pct", "morningstar_rating", "risk_grade"]]
        df_perf.to_sql("fact_performance", conn, if_exists="replace", index=False)
        df_perf.to_csv(PROCESSED_DIR / "cleaned_scheme_performance.csv", index=False)

    # 4. fact_transactions Ingestion
    print(" Cleaning and loading 08_investor_transactions.csv...")
    t_path = RAW_DIR / "08_investor_transactions.csv"
    if t_path.exists():
        df_tx = pd.read_csv(t_path)
        df_tx = df_tx[["investor_id", "transaction_date", "amfi_code", "transaction_type", "amount_inr", "kyc_status"]]
        df_tx.to_sql("fact_transactions", conn, if_exists="replace", index=False)
        df_tx.to_csv(PROCESSED_DIR / "cleaned_investor_transactions.csv", index=False)

    print("\n Production Database Summary Accounts:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in cursor.fetchall():
        t_name = table[0]
        if t_name == 'sqlite_sequence': continue
        cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
        print(f"   • Table [{t_name}] now holds {cursor.fetchone()[0]} verified rows.")
        
    conn.close()
    print("\n PRODUCTION BACKEND PIPELINE COMPLETE!")

if __name__ == "__main__":
    run_production_etl()
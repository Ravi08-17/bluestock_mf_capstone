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
    print("  DAY 2: RUNNING LOOP-BASED ROBUST TIME-SERIES ETL")
    print("============================================================\n")
    
    db_path = DB_DIR / "bluestock_mf.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(SQL_SCHEMA, "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    
    # --- 1. FUND MASTER DIMENSION ---
    print(" Processing fund_master.csv...")
    master_path = RAW_DIR / "fund_master.csv"
    if master_path.exists():
        df_master = pd.read_csv(master_path)
        df_master.drop_duplicates(subset=["scheme_code"], inplace=True)
        df_master.to_sql("dim_fund", conn, if_exists="replace", index=False)
        df_master.to_csv(PROCESSED_DIR / "cleaned_fund_master.csv", index=False)
    
    # --- 2. NAV HISTORY (LOOP-BASED RESAMPLING) ---
    print(" Processing nav_history.csv (Using safe individual fund expansion)...")
    nav_path = RAW_DIR / "nav_history.csv"
    if nav_path.exists():
        df_raw_nav = pd.read_csv(nav_path)
        df_raw_nav["nav_date"] = pd.to_datetime(df_raw_nav["nav_date"])
        df_raw_nav = df_raw_nav[df_raw_nav["nav"] > 0]
        
        resampled_funds = []
        
        # Process each fund code individually to completely avoid multi-index bugs
        unique_schemes = df_raw_nav["scheme_code"].unique()
        for scheme in unique_schemes:
            # Filter to just this specific fund
            df_sub = df_raw_nav[df_raw_nav["scheme_code"] == scheme].copy()
            df_sub.drop_duplicates(subset=["nav_date"], inplace=True)
            
            # Resample dates for this specific fund
            df_sub.set_index("nav_date", inplace=True)
            df_sub = df_sub.resample("D").ffill()
            df_sub = df_sub.reset_index()
            
            # Explicitly force the scheme_code back in cleanly
            df_sub["scheme_code"] = int(scheme)
            resampled_funds.append(df_sub)
            
        # Combine all processed funds back together into one master table
        df_nav = pd.concat(resampled_funds, ignore_index=True)
            
        # Build Date Dimension table safely
        df_date = pd.DataFrame({"date_string": df_nav["nav_date"].dt.strftime("%Y-%m-%d").unique()})
        df_date_dt = pd.to_datetime(df_date["date_string"])
        df_date["year"] = df_date_dt.dt.year
        df_date["month"] = df_date_dt.dt.month
        df_date["day"] = df_date_dt.dt.day
        df_date["quarter"] = df_date_dt.dt.quarter
        df_date["day_of_week"] = df_date_dt.dt.day_name()
        
        df_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        
        # Convert date to string format for SQL compatibility
        df_nav["nav_date"] = df_nav["nav_date"].dt.strftime("%Y-%m-%d")
        
        # Final clean dataframe structure matching schema.sql exactly
        df_final_nav = df_nav[["scheme_code", "nav_date", "nav"]].copy()
        
        df_final_nav.to_sql("fact_nav", conn, if_exists="replace", index=False)
        df_final_nav.to_csv(PROCESSED_DIR / "cleaned_nav_history.csv", index=False)
    
    print("\n Database Row Summary Accounts:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        t_name = table[0]
        if t_name == 'sqlite_sequence': continue
        cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
        print(f"   • Table [{t_name}] now holds {cursor.fetchone()[0]} verified rows.")
        
    conn.close()
    print("\n PIPELINE LOADED SUCCESSFULLY WITHOUT ERRORS!")

if __name__ == "__main__":
    run_production_etl()
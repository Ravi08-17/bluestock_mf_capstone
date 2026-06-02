import os
from pathlib import Path
import pandas as pd

def ingest_and_profile_all_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    
    production_files = [
        "01_fund_master.csv", "02_nav_history.csv", "03_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv", "05_category_inflows.csv", "06_industry_folio_count.csv",
        "07_scheme_performance.csv", "08_investor_transactions.csv", "09_portfolio_holdings.csv",
        "10_benchmark_indices.csv"
    ]
    
    print("============================================================")
    print("🔬 DAY 1: RUNNING OFFICIAL PRODUCTION DATA INGESTION SUITE")
    print("============================================================\n")
    
    for file_name in production_files:
        file_path = RAW_DIR / file_name
        print(f" PROFILING DATASET: {file_name}")
        print("-" * 60)
        
        if not file_path.exists():
            print(f" ALERT: {file_name} is missing from data/raw/ folder!")
            print("-" * 60 + "\n")
            continue
            
        try:
            df = pd.read_csv(file_path)
            print(f"• Dataset Size: {df.shape[0]} Rows, {df.shape[1]} Columns")
            print("\n• Data Fields & Types (.dtypes):")
            print(df.dtypes)
            print("\n• First 2 Sample Rows (.head()):")
            print(df.head(2))
            
            nulls = df.isnull().sum().sum()
            dups = df.duplicated().sum()
            print(f"\n• Anomaly Scan: Missing Cells={nulls} | Duplicate Rows={dups}")
            
        except Exception as e:
            print(f" Failed to process dataset: {str(e)}")
            
        print("-" * 60 + "\n")

if __name__ == "__main__":
    ingest_and_profile_all_data()
import pandas as pd
from pathlib import Path

def validate_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    
    print(" Executing Data Validation & Integrity Checks...\n")
    
    # Load critical datasets
    master_df = pd.read_csv(RAW_DIR / "fund_master.csv")
    nav_df = pd.read_csv(RAW_DIR / "nav_history.csv")
    
    # 1. Structural Exploration
    print(" FUND MASTER STRUCTURAL OVERVIEW:")
    print(f"• Unique Fund Houses: {master_df['fund_house'].nunique()}")
    print(f"• Unique Categories: {master_df['category'].nunique()}")
    print(f"• Unique Sub-Categories: {master_df['sub_category'].nunique()}")
    print(f"• Risk Grades Found: {master_df['risk_grade'].unique().tolist()}\n")
    
    # 2. Referential Integrity Check (AMFI Code Verification)
    master_codes = set(master_df["scheme_code"].unique())
    nav_codes = set(nav_df["scheme_code"].unique())
    
    missing_in_nav = master_codes - nav_codes
    
    # 3. Print out Data Quality Summary Statement
    print("=" * 60)
    print(" DATA QUALITY SUMMARY REPORT")
    print("=" * 60)
    print(f"• Total codes in Fund Master: {len(master_codes)}")
    print(f"• Total codes found in NAV History: {len(nav_codes)}")
    
    if len(missing_in_nav) == 0:
        print(" REFERENTIAL INTEGRITY PERFECT: Every scheme code in fund_master matches a history partition.")
    else:
        print(f" INTEGRITY MISMATCH: {len(missing_in_nav)} scheme codes are missing historical prices!")
        print(f"  --> Missing AMFI Codes: {missing_in_nav}")
        
    print("-" * 60)
    print(" AMFI CODE ANATOMY INSIGHT:")
    print("  AMFI (Association of Mutual Funds in India) allocates unique 6-digit numeric identifiers")
    print("  to distinguish distinct mutual fund products, tracking plan types (Direct vs. Regular)")
    print("  and payout modes (Growth vs. IDCW) linearly.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    validate_data()
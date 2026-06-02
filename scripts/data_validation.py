from pathlib import Path
import pandas as pd

def run_day1_validation():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    
    print("============================================================")
    print("  DAY 1: EXECUTING AMFI REFERENTIAL INTEGRITY CHECKS")
    print("============================================================\n")
    
    master_path = RAW_DIR / "01_fund_master.csv"
    nav_path = RAW_DIR / "02_nav_history.csv"
    
    if not master_path.exists() or not nav_path.exists():
        print(" Error: Core production files missing for integrity validation checks!")
        return
        
    df_master = pd.read_csv(master_path)
    df_nav = pd.read_csv(nav_path)
    
    master_codes = set(df_master["amfi_code"].unique())
    nav_codes = set(df_nav["amfi_code"].unique())
    
    print(f" Unique AMFI Codes in Fund Master: {len(master_codes)}")
    print(f" Unique AMFI Codes in NAV History: {len(nav_codes)}")
    
    # Check for broken references between tables
    unlinked_codes = master_codes - nav_codes
    
    print("\n============================================================")
    print(" DAY 1 DATA VALIDATION SCHEMATIC REPORT")
    print("============================================================")
    if len(unlinked_codes) == 0:
        print(" SUCCESS: Referential alignment is at 100%!")
        print("   Every single AMFI code in the master file maps perfectly to history entries.")
    else:
        print(f"  DATA GAP DETECTED: {len(unlinked_codes)} codes have no tracking history!")
        print(f"   Unlinked Codes: {list(unlinked_codes)}")
    print("============================================================\n")

if __name__ == "__main__":
    run_day1_validation()
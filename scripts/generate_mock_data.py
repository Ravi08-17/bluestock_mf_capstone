import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def generate_all_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    np.random.seed(42)
    print(f"Generating base datasets in: {RAW_DIR}")
    
    # 1. Fund Master Codes & Structure
    schemes = {
        125497: ("HDFC Top 100 Fund - Direct Plan - Growth", "HDFC Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High"),
        119551: ("SBI Bluechip Fund - Direct Plan - Growth", "SBI Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High"),
        120503: ("ICICI Prudential Bluechip Fund - Direct Plan - Growth", "ICICI Prudential Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High"),
        118632: ("Nippon India Large Cap Fund - Direct Plan - Growth", "Nippon India Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High"),
        119092: ("Axis Bluechip Fund - Direct Plan - Growth", "Axis Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High"),
        120841: ("Kotak Bluechip Fund - Direct Plan - Growth", "Kotak Mutual Fund", "Equity Scheme - Large Cap Fund", "Very High")
    }
    
    master_rows = []
    for code, info in schemes.items():
        master_rows.append({
            "scheme_code": code,
            "scheme_name": info[0],
            "fund_house": info[1],
            "category": "Equity",
            "sub_category": info[2],
            "risk_grade": info[3]
        })
    df_master = pd.DataFrame(master_rows)
    df_master.to_csv(RAW_DIR / "fund_master.csv", index=False)
    
    # 2. Base NAV History
    date_today = datetime.today()
    dates = [date_today - timedelta(days=x) for x in range(365)]
    dates.reverse()
    
    nav_rows = []
    for code in schemes.keys():
        base_nav = np.random.uniform(50, 100)
        for d in dates:
            base_nav += np.random.normal(0, 0.5)
            nav_rows.append({
                "scheme_code": code,
                "nav_date": d.strftime("%Y-%m-%d"),
                "nav": round(max(base_nav, 10.0), 4)
            })
    df_nav = pd.DataFrame(nav_rows)
    df_nav.to_csv(RAW_DIR / "nav_history.csv", index=False)
    
    print("Core structural files generated successfully!")

if __name__ == "__main__":
    generate_all_data()
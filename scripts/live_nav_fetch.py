import pandas as pd
import requests
from pathlib import Path

def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    target_schemes = {
        125497: "HDFC_Top_100_Direct",
        119551: "SBI_Bluechip",
        120503: "ICICI_Bluechip",
        118632: "Nippon_Large_Cap",
        119092: "Axis_Bluechip",
        120841: "Kotak_Bluechip"
    }
    
    all_live_navs = []
    
    print("Initiating live API data fetch from mfapi.in...")
    print("-" * 60)
    
    for code, name in target_schemes.items():
        url = f"https://api.mfapi.in/mf/{code}"
        print(f"Fetching: {name} (AMFI: {code})...")
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code} for code {code}")
                continue
                
            payload = response.json()
            
            # The API stores historical lists inside the "data" key, not "nav"
            nav_entries = payload.get("data", [])
            
            if not nav_entries:
                print(f"Empty historical dataset received for code {code}")
                continue
            
            # Index 0 holds the absolute latest update
            latest_record = nav_entries[0]
            print(f"   ↳ Success! Latest found: Date={latest_record['date']}, NAV={latest_record['nav']}")
            
            # Extract metadata safely
            meta = payload.get("meta", {})
            
            all_live_navs.append({
                "scheme_code": int(code),
                "scheme_name": meta.get("scheme_name", name),
                "fund_house": meta.get("fund_house", "Unknown"),
                "scheme_type": meta.get("scheme_type", "Open Ended"),
                "scheme_category": meta.get("scheme_category", "Equity"),
                "live_nav_date": latest_record["date"],
                "live_nav": float(latest_record["nav"])
            })
            
            # Save the clean timeline CSV history for Day 3 analysis
            history_df = pd.DataFrame(nav_entries)
            history_df.to_csv(RAW_DIR / f"raw_api_history_{code}.csv", index=False)
            
        except Exception as e:
            print(f"Error processing AMFI code {code}: {str(e)}")
            
    print("-" * 60)
    if all_live_navs:
        live_df = pd.DataFrame(all_live_navs)
        live_df.to_csv(RAW_DIR / "live_snapshot_nav.csv", index=False)
        print("Live NAV Ingestion Completed Successfully!")
        print("\n", live_df[["scheme_code", "live_nav_date", "live_nav"]].to_string(index=False))
    else:
        print("Ingestion yielded no records.")

if __name__ == "__main__":
    main()
-- ============================================================
-- BLUESTOCK MUTUAL FUND CAPSTONE: STAR SCHEMA RELATIONAL MODEL
-- ============================================================

-- Table 1: Fund Information Dimension
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    risk_category TEXT
);

-- Table 2: Date Tracking Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_string TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    day_of_week TEXT
);

-- Table 3: Historical NAV Fact Ledger
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER,
    nav_date TEXT,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, nav_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (nav_date) REFERENCES dim_date(date_string)
);

-- Table 4: Investor Transactions Fact Ledger
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT,
    transaction_date TEXT,
    amfi_code INTEGER,
    transaction_type TEXT,
    amount_inr REAL,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Table 5: Performance Metrics Fact Ledger
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);
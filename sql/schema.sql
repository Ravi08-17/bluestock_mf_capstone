-- ============================================================
-- BLUESTOCK MUTUAL FUND CAPSTONE: STAR SCHEMA RELATIONAL MODEL
-- ============================================================

-- Table 1: Fund Information Dimension
CREATE TABLE IF NOT EXISTS dim_fund (
    scheme_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    risk_grade TEXT
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    nav_date TEXT,
    nav REAL NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code),
    FOREIGN KEY (nav_date) REFERENCES dim_date(date_string)
);

-- Table 4: Investor Transactions Fact Ledger
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER,
    transaction_date TEXT,
    transaction_type TEXT,
    amount REAL NOT NULL,
    kyc_status TEXT,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Table 5: Performance Metrics Fact Ledger
CREATE TABLE IF NOT EXISTS fact_performance (
    scheme_code INTEGER PRIMARY KEY,
    return_1y REAL,
    return_3y REAL,
    return_5y REAL,
    expense_ratio REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);
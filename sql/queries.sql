-- ============================================================
-- BLUESTOCK MUTUAL FUND CAPSTONE: DAY 2 ANALYTICAL QUERY SUITE
-- ============================================================

-- Query 1: View Complete Fund Master Details Linked with Total Tracked History
SELECT 
    f.scheme_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.risk_grade,
    COUNT(n.id) as total_tracked_days,
    MIN(n.nav_date) as history_start_date,
    MAX(n.nav_date) as history_end_date
FROM dim_fund f
LEFT JOIN fact_nav n ON f.scheme_code = n.scheme_code
GROUP BY f.scheme_code;

-- Query 2: Calculate the Average and Highest NAV for Each Scheme
SELECT 
    f.scheme_name,
    ROUND(AVG(n.nav), 2) as average_nav,
    ROUND(MAX(n.nav), 2) as peak_historical_nav,
    ROUND(MIN(n.nav), 2) as lowest_historical_nav    
FROM fact_nav n
JOIN dim_fund f ON n.scheme_code = f.scheme_code
GROUP BY f.scheme_code;

-- Query 3: Track Monthly Average NAV Trends for a Specific Scheme (e.g., HDFC - 125497)
SELECT 
    d.year,
    d.month,
    ROUND(AVG(n.nav), 2) as monthly_avg_nav,
    COUNT(n.id) as recorded_days
FROM fact_nav n
JOIN dim_date d ON n.nav_date = d.date_string
WHERE n.scheme_code = 125497
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
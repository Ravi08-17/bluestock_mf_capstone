
import os
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns

def run_quantitative_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
    OUT_DIR = BASE_DIR / "data" / "processed"
    CHART_DIR = BASE_DIR / "data" / "exported_charts"
    
    conn = sqlite3.connect(DB_PATH)
    
    print("============================================================")
    print(" DAY 4: EXECUTING QUANTITATIVE PERFORMANCE ANALYTICS ENGINE")
    print("============================================================\n")
    
    # Load core data structures
    df_nav = pd.read_sql_query("SELECT * FROM fact_nav ORDER BY amfi_code, nav_date", conn)
    df_fund = pd.read_sql_query("SELECT amfi_code, scheme_name FROM dim_fund", conn)
    
    # 1. Compute Daily Returns
    print(" Calculating Daily Returns & Risk Profiles...")
    df_nav['nav_date'] = pd.to_datetime(df_nav['nav_date'])
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    # 2. Performance Metric Lists
    rf = 0.065  # 6.5% RBI Repo Rate Proxy
    analytics_records = []
    
    # Mock benchmark tracking array for regression (Nifty 100 proxy mapping)
    # Generates a matching date timeline with safe synthetic normal variance
    unique_dates = sorted(df_nav['nav_date'].unique())
    np.random.seed(42)
    nifty100_returns = np.random.normal(0.0005, 0.01, len(unique_dates))
    df_bench = pd.DataFrame({'nav_date': unique_dates, 'bench_return': nifty100_returns})

    for amfi in df_nav['amfi_code'].unique():
        df_sub = df_nav[df_nav['amfi_code'] == amfi].sort_values('nav_date').copy()
        if len(df_sub) < 2:
            continue
            
        # CAGR Calculation
        nav_start, nav_end = df_sub['nav'].iloc[0], df_sub['nav'].iloc[-1]
        n_years = (df_sub['nav_date'].iloc[-1] - df_sub['nav_date'].iloc[0]).days / 365.25
        cagr = (nav_end / nav_start) ** (1 / n_years) - 1 if n_years > 0 else 0
        
        # Risk Ratios
        returns = df_sub['daily_return'].dropna()
        avg_annual_return = returns.mean() * 252
        std_annual_dev = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio
        sharpe = (avg_annual_return - rf) / std_annual_dev if std_annual_dev > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino = (avg_annual_return - rf) / downside_std if downside_std > 0 else 0
        
        # Alpha & Beta Regression vs Benchmark
        df_reg = df_sub.merge(df_bench, on='nav_date').dropna(subset=['daily_return'])
        if len(df_reg) > 5:
            beta, intercept, _, _, _ = linregress(df_reg['bench_return'], df_reg['daily_return'])
            alpha = intercept * 252
        else:
            alpha, beta = 0.0, 1.0
            
        # Maximum Drawdown
        df_sub['running_max'] = df_sub['nav'].cummax()
        df_sub['drawdown'] = df_sub['nav'] / df_sub['running_max'] - 1
        max_dd = df_sub['drawdown'].min()
        
        analytics_records.append({
            'amfi_code': amfi,
            'cagr': cagr,
            'sharpe': sharpe,
            'sortino': sortino,
            'alpha': alpha,
            'beta': beta,
            'max_dd': max_dd
        })
        
    df_analytics = pd.DataFrame(analytics_records).merge(df_fund, on='amfi_code')
    
    # 3. Build Composite Scorecard (0-100 Ranked Percentiles)
    print(" Compiling Composite Multi-Factor Scorecards...")
    df_analytics['rank_cagr'] = df_analytics['cagr'].rank(pct=True)
    df_analytics['rank_sharpe'] = df_analytics['sharpe'].rank(pct=True)
    df_analytics['rank_alpha'] = df_analytics['alpha'].rank(pct=True)
    df_analytics['rank_dd'] = df_analytics['max_dd'].rank(pct=True)  # Less negative is better
    
    # Composite formula weighting constraints
    df_analytics['composite_score'] = (
        0.35 * df_analytics['rank_cagr'] +
        0.25 * df_analytics['rank_sharpe'] +
        0.25 * df_analytics['rank_alpha'] +
        0.15 * df_analytics['rank_dd']
    ) * 100
    
    df_analytics = df_analytics.sort_values('composite_score', ascending=False)
    
    # Save CSV Deliverables
    df_analytics.to_csv(OUT_DIR / "fund_scorecard.csv", index=False)
    df_analytics[['amfi_code', 'scheme_name', 'alpha', 'beta']].to_csv(OUT_DIR / "alpha_beta.csv", index=False)
    print(" Saved fund_scorecard.csv and alpha_beta.csv cleanly to data/processed/!")

    # 4. Generate Benchmark Comparison Chart
    print(" Plotting Performance Verification Diagrams...")
    plt.figure(figsize=(12, 6))
    top_funds = df_analytics['scheme_name'].head(5).values
    df_plot = df_nav[df_nav['amfi_code'].isin(df_analytics['amfi_code'].head(5))]
    
    # Simplified aggregate cumulative plotting
    for amfi in df_analytics['amfi_code'].head(5):
        sub = df_nav[df_nav['amfi_code'] == amfi].sort_values('nav_date')
        cum_return = (1 + sub['daily_return'].fillna(0)).cumprod() - 1
        name = df_fund[df_fund['amfi_code'] == amfi]['scheme_name'].values[0]
        plt.plot(sub['nav_date'], cum_return, label=name[:30])
        
    plt.title("Top 5 Outperforming Schemes vs Benchmark Returns")
    plt.xlabel("Timeline Date Vector")
    plt.ylabel("Cumulative Alpha Growth")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "benchmark_comparison_chart.png")
    plt.show()
    
    conn.close()
    print(" DAY 4 QUANTITATIVE ANALYSIS PROCESSING COMPLETED SUCCESSFUL!")

if __name__ == "__main__":
    run_quantitative_pipeline()
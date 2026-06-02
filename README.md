\# Bluestock Mutual Fund Analytics Capstone



A production-grade ETL data engineering pipeline built to ingest, clean, validate, and analyze multi-source mutual fund historical data using Python (Pandas) and an optimized SQLite relational star schema.



\---



\##  Project Architecture



```text

├── data/

│   ├── raw/            # 10 official production CSV datasets

│   └── processed/      # Cleaned data files

│   └── db/             # Production SQLite relational database file

├── scripts/

│   ├── data\_ingestion.py   # Day 1: Full-scale data profiling engine

│   ├── data\_validation.py  # Day 1: AMFI key referential integrity checker

│   ├── etl\_pipeline.py     # Day 2: Robust loop-based time-series ETL pipeline

│   └── run\_queries.py      # Day 2: SQL analytics reporting suite

├── sql/

│   └── schema.sql          # Star schema relational architecture layouts

├── data\_dictionary.md      # Detailed column definitions and business descriptions

└── README.md               # Main project overview documentation


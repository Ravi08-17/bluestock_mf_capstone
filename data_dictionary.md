\#  Bluestock Mutual Fund Analytics: Data Dictionary (Day 2 Schema)



This data dictionary outlines the Star Schema relational database architecture implemented within `data/db/bluestock\_mf.db`.



\---



\##  1. Table: `dim\_fund` (Dimension Table)

Tracks unique core mutual fund schemes and classification details.



| Column Name | Data Type | Key Type | Business Definition | Source |

| :--- | :--- | :--- | :--- | :--- |

| `scheme\_code` | INTEGER | PRIMARY KEY | Unique 6-digit AMFI identifier code for the mutual fund. | `fund\_master.csv` |

| `scheme\_name` | TEXT | None | Full legal marketing name of the fund scheme. | `fund\_master.csv` |

| `fund\_house` | TEXT | None | Asset Management Company (AMC) managing the fund (e.g., SBI, HDFC). | `fund\_master.csv` |

| `category` | TEXT | None | Broad asset class categorization (e.g., Equity, Debt). | `fund\_master.csv` |

| `sub\_category` | TEXT | None | Specific investment strategy (e.g., Large Cap, Mid Cap). | `fund\_master.csv` |

| `risk\_grade` | TEXT | None | Risk assessment category assigned to the fund. | `fund\_master.csv` |



\---



\##  2. Table: `dim\_date` (Dimension Table)

Provides expanded time-intelligence attributes for optimized date group aggregations.



| Column Name | Data Type | Key Type | Business Definition | Source |

| :--- | :--- | :--- | :--- | :--- |

| `date\_string` | TEXT | PRIMARY KEY | Calendar date formatted cleanly as string string (`YYYY-MM-DD`). | Dynamically Generated |

| `year` | INTEGER | None | Calendar year of the log (e.g., 2025, 2026). | Dynamically Generated |

| `month` | INTEGER | None | Numerical month identifier (1 through 12). | Dynamically Generated |

| `day` | INTEGER | None | Day of the month (1 through 31). | Dynamically Generated |

| `quarter` | INTEGER | None | Calendar quarter identifier (1 through 4). | Dynamically Generated |

| `day\_of\_week` | TEXT | None | String name of the day (e.g., Monday, Sunday). | Dynamically Generated |



\---



\##  3. Table: `fact\_nav` (Fact Table)

Tracks the historical continuous time-series of daily Net Asset Values (NAV).



| Column Name | Data Type | Key Type | Business Definition | Source |

| :--- | :--- | :--- | :--- | :--- |

| `scheme\_code` | INTEGER | FOREIGN KEY | References `dim\_fund(scheme\_code)`. | `nav\_history.csv` |

| `nav\_date` | TEXT | FOREIGN KEY | References `dim\_date(date\_string)`. | `nav\_history.csv` |

| `nav` | REAL | None | Net Asset Value price per unit on that given date. | `nav\_history.csv` |



> \*Note: Missing records for weekend closed-market periods and national holidays have been automatically forward-filled (ffill) from the last known trading day's closing values to protect computational time-series continuity.\*


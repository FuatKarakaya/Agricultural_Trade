"""
Recreate Producer_Prices table from CSV.
Executes the SQL files: create_producer_prices.sql and import_producer_prices.sql
"""
import os
from database import get_db_connection

def run_sql_file(filepath):
    """Execute a SQL file."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        cur.execute(sql)
        conn.commit()
        print(f"Executed: {filepath}")
        return cur.rowcount
    except Exception as e:
        conn.rollback()
        print(f"Error in {filepath}: {e}")
        return None
    finally:
        conn.close()

# Step 1: Create the table
run_sql_file('create_producer_prices.sql')

# Step 2: Import data (uses psycopg2's copy_expert for COPY command)
conn = get_db_connection()
cur = conn.cursor()

try:
    # Create staging table
    cur.execute("""
        DROP TABLE IF EXISTS producer_prices_staging;
        CREATE TEMP TABLE producer_prices_staging (
            area_code INTEGER,
            area_code_m49 VARCHAR(10),
            area VARCHAR(100),
            item_code INTEGER,
            item_code_cpc VARCHAR(20),
            item VARCHAR(200),
            element_code INTEGER,
            element VARCHAR(100),
            year_code INTEGER,
            year INTEGER,
            months_code VARCHAR(20),
            months VARCHAR(20),
            unit VARCHAR(20),
            value FLOAT,
            flag VARCHAR(5)
        );
    """)
    
    # Copy CSV into staging
    csv_path = r'C:\Users\fuatk\Desktop\Agricultural_Trade\Prices_E_All_Data_Normal.csv'
    with open(csv_path, 'r', encoding='latin-1') as f:
        cur.copy_expert("COPY producer_prices_staging FROM STDIN WITH (FORMAT csv, HEADER true)", f)
    print(f"Loaded CSV into staging table")
    
    # Insert with transformation
    cur.execute("""
        INSERT INTO Producer_Prices (country_id, commodity_id, month, year, unit, value)
        SELECT 
            CAST(TRIM(BOTH '''' FROM area_code_m49) AS INTEGER) as country_id,
            item_code as commodity_id,
            CASE months
                WHEN 'January' THEN 1  WHEN 'February' THEN 2  WHEN 'March' THEN 3
                WHEN 'April' THEN 4    WHEN 'May' THEN 5       WHEN 'June' THEN 6
                WHEN 'July' THEN 7     WHEN 'August' THEN 8    WHEN 'September' THEN 9
                WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
            END as month,
            year,
            unit,
            value
        FROM producer_prices_staging s
        WHERE months != 'Annual value'
          AND value IS NOT NULL
          AND EXISTS (SELECT 1 FROM Countries c WHERE c.country_id = CAST(TRIM(BOTH '''' FROM s.area_code_m49) AS INTEGER))
          AND EXISTS (SELECT 1 FROM Commodities cm WHERE cm.fao_code = s.item_code);
    """)
    
    conn.commit()
    print(f"Inserted {cur.rowcount} rows into Producer_Prices")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    conn.close()

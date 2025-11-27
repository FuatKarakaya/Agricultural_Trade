from database import get_db_connection

def migrate_sql():
    conn = get_db_connection()
    cur = conn.cursor()

    years = range(2010, 2024)
    y_cols_def = [f'ADD COLUMN IF NOT EXISTS "Y{y}" FLOAT' for y in years]
    y_cols_sel = [f'CAST(t."Y{y}" AS FLOAT)' for y in years]
    y_cols_ins = [f'"Y{y}"' for y in years]

    sql = f"""
    ALTER TABLE Producer_Prices
        DROP COLUMN IF EXISTS year CASCADE,
        DROP COLUMN IF EXISTS price_unit,
        DROP COLUMN IF EXISTS value;
    
    ALTER TABLE Producer_Prices {', '.join(y_cols_def)};

    INSERT INTO Producer_Prices (country_id, commodity_id, month, {', '.join(y_cols_ins)})
    SELECT
        c.country_id,
        CAST(t."Item Code" AS INTEGER),
        CASE t."Months"
            WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
            WHEN 'April' THEN 4   WHEN 'May' THEN 5      WHEN 'June' THEN 6
            WHEN 'July' THEN 7    WHEN 'August' THEN 8   WHEN 'September' THEN 9
            WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
        END,
        {', '.join(y_cols_sel)}
    FROM tempnotnormalpp t
    JOIN countries c ON t."Area" = c.country_name
    JOIN commodities cm ON CAST(t."Item Code" AS INTEGER) = cm.fao_code
    WHERE t."Months" != 'Annual value'
      AND t."Item Code" ~ '^[0-9]+$';
    """
    
    try:
        print("Executing SQL migration...")
        cur.execute(sql)
        conn.commit()
        print(f"Migration successful. Rows inserted: {cur.rowcount}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_sql()
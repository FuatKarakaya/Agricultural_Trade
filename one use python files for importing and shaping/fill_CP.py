from database import get_db_connection

def migrate_cp_sql():
    conn = get_db_connection()
    cur = conn.cursor()

    sql = """

    INSERT INTO Consumer_Prices (country_id, year, month, value, type)
    SELECT
        countries.country_id,
        CAST(tempcp."Year" AS INTEGER),
        CASE tempcp."Months"
            WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
            WHEN 'April' THEN 4   WHEN 'May' THEN 5      WHEN 'June' THEN 6
            WHEN 'July' THEN 7    WHEN 'August' THEN 8   WHEN 'September' THEN 9
            WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
        END,
        CAST(tempcp."Value" AS FLOAT),
        CAST(tempcp."Type" AS SMALLINT)
    FROM tempcp
    JOIN countries ON tempcp."Area" = countries.country_name
    WHERE tempcp."Months" != 'Annual value';
    """
    
    try:
        print("Executing SQL migration for Consumer_Prices...")
        cur.execute(sql)
        conn.commit()
        print(f"Migration successful. Rows inserted: {cur.rowcount}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_cp_sql()
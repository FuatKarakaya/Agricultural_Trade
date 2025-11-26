import csv
import os
from database import get_db_connection

# --- CONFIGURATION ---
CSV_FILE_PATH = r"C:\Users\fuatk\Desktop\CP.csv"
TABLE_NAME = "tempCP"

def import_csv():
    conn = None
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            columns = ['"{}"'.format(col.strip().replace('"', '')) for col in header]

        conn = get_db_connection()
        cur = conn.cursor()
        print("Connected to database.")

        print(f"Creating table '{TABLE_NAME}'...")
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
        
        create_query = f"CREATE TABLE {TABLE_NAME} ({' TEXT, '.join(columns)} TEXT);"
        cur.execute(create_query)
        conn.commit()

        print("Importing data...")
        with open(CSV_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            copy_sql = f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER DELIMITER ','"
            cur.copy_expert(copy_sql, f)
            conn.commit()
        
        print("Success: Table created and data imported.")

    except Exception as e:
        print(f"Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    import_csv()
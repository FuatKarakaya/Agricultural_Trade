from database import execute_query, get_db_connection
import csv
import os

TABLE_NAME = "commodity"
COLUMNS_TO_DROP = [
    "Domain Code",
    "Domain",
    "Description",
    "HS Code",
    "HS07 Code",
    "HS12 Code"
]

def drop_unwanted_columns():
    drop_parts = [f'DROP COLUMN IF EXISTS "{col}"' for col in COLUMNS_TO_DROP]
    query = f'ALTER TABLE {TABLE_NAME} {", ".join(drop_parts)};'
    
    print(f"Executing: {query}")
    try:
        execute_query(query)
        print("Columns dropped successfully.")
    except Exception as e:
        print(f"Failed to drop columns: {e}")

CSV_FILE_PATH = r"C:\Users\fuatk\Desktop\Agricultural_Trade\commodity.csv" 
TABLE_NAME = "commodity"

def import_csv_to_postgres():
    conn = None
    try:
        # 1. Read CSV Header to define columns
        # 'utf-8-sig' automatically handles the BOM character if present at the start of the file
        with open(CSV_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)  # Read just the first line
            
            # Clean headers: strip whitespace and remove existing quotes to prevent double-quoting
            # Then wrap in double quotes for SQL identifier safety
            # formatted using .format to avoid quote collision SyntaxErrors
            columns = ['"{}"'.format(col.strip().replace('"', '')) for col in header]

        # 2. Connect to DB (Single connection for both Create and Copy)
        conn = get_db_connection()
        cur = conn.cursor()
        print("Connected to database.")

        # 3. Create the table
        print(f"Preparing to recreate table '{TABLE_NAME}'...")
        
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
        
        create_query = f"CREATE TABLE {TABLE_NAME} ({' TEXT, '.join(columns)} TEXT);"
        cur.execute(create_query)
        conn.commit() # Commit schema changes
        
        print(f"Table '{TABLE_NAME}' created with {len(columns)} columns (all TEXT).")

        # 4. Perform the COPY
        with open(CSV_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            copy_sql = f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER DELIMITER ','"
            cur.copy_expert(copy_sql, f)
            conn.commit() # Commit data changes
            
            # Log operations
            with open("log.sql", "a") as log:
                log.write(f"\n{create_query}")
                log.write(f"\n{copy_sql} (via copy_expert)")
            
            print("Data import successful via COPY command.")

    except Exception as e:
        print(f"Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    import_csv_to_postgres()
    drop_unwanted_columns()


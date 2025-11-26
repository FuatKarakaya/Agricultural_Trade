from database import execute_query

TABLE_NAME = "tempNotNormalPP"

def change_table_name():

    query = f"ALTER TABLE {TABLE_NAME} RENAME TO tempNotNormalPP;"
    print(f"Executing table rename...")
    
    try:
        execute_query(query)
        print("Table renamed successfully.")
    except Exception as e:
        print(f"Failed to rename table: {e}")

def delete_annual_rows():
    """
    Deletes rows where the 'Months' column is 'Annual value'.
    """
    query = f"DELETE FROM {TABLE_NAME} WHERE \"Months\" = 'Annual value';"
    print(f"Executing row deletion...")
    
    try:
        rows_deleted = execute_query(query)
        print(f"Rows deleted successfully. Count: {rows_deleted}")
    except Exception as e:
        print(f"Failed to delete rows: {e}")

def drop_flag_columns():
    """
    Drops columns Y1991F through Y2024F.
    """
    # Generate the list of columns: Y1991F, Y1992F, ..., Y2024F
    columns_to_drop = [f"Y{year}F" for year in range(1991, 2025)]
    
    # Construct the query: DROP COLUMN IF EXISTS "Y1991F", DROP COLUMN IF EXISTS "Y1992F"...
    drop_parts = [f'DROP COLUMN IF EXISTS "{col}"' for col in columns_to_drop]
    query = f'ALTER TABLE {TABLE_NAME} {", ".join(drop_parts)};'
    
    print(f"Executing column drop for {len(columns_to_drop)} columns...")
    
    try:
        execute_query(query)
        print("Flag columns (F) dropped successfully.")
    except Exception as e:
        print(f"Failed to drop columns: {e}")

if __name__ == "__main__":
    columns_to_drop = [f"Y{year}" for year in range(1991, 2000)]
    drop_parts = [f'DROP COLUMN IF EXISTS "{col}"' for col in columns_to_drop]
    query = f'ALTER TABLE {TABLE_NAME} {", ".join(drop_parts)};'
    try:
        execute_query(query)
        print("Year columns (1991-1999) dropped successfully.")
    except Exception as e:
        print(f"Failed to drop year columns: {e}")
    
"""
Script to delete commodities with item_name starting with a number.
Only deletes commodities that are NOT referenced in other tables.
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return psycopg2.connect(db_url)

def delete_numeric_commodities():
    conn = get_connection()
    cur = conn.cursor()
    
    # Find commodities starting with a number that are NOT referenced anywhere
    cur.execute("""
        SELECT cm.fao_code, cm.item_name 
        FROM Commodities cm
        WHERE cm.item_name ~ '^[0-9]'
          AND NOT EXISTS (SELECT 1 FROM Production p WHERE p.commodity_code = cm.fao_code)
          AND NOT EXISTS (SELECT 1 FROM Producer_Prices pp WHERE pp.commodity_id = cm.fao_code)
        ORDER BY cm.item_name;
    """)
    
    rows = cur.fetchall()
    
    if not rows:
        print("No unreferenced commodities found with item_name starting with a number.")
        cur.close()
        conn.close()
        return
    
    print(f"Found {len(rows)} UNREFERENCED commodities with item_name starting with a number:")
    print("-" * 60)
    for fao_code, item_name in rows:
        print(f"  FAO Code: {fao_code} | Item: {item_name}")
    print("-" * 60)
    
    # Ask for confirmation
    confirm = input(f"\nAre you sure you want to delete these {len(rows)} records? (yes/no): ")
    
    if confirm.lower() == 'yes':
        # Delete only unreferenced records
        cur.execute("""
            DELETE FROM Commodities cm
            WHERE cm.item_name ~ '^[0-9]'
              AND NOT EXISTS (SELECT 1 FROM Production p WHERE p.commodity_code = cm.fao_code)
              AND NOT EXISTS (SELECT 1 FROM Producer_Prices pp WHERE pp.commodity_id = cm.fao_code);
        """)
        deleted_count = cur.rowcount
        conn.commit()
        print(f"\n✓ Successfully deleted {deleted_count} commodities.")
    else:
        print("\n✗ Operation cancelled. No records were deleted.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    delete_numeric_commodities()

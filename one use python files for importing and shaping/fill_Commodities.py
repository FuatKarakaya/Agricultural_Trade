from database import execute_query

if __name__ == "__main__":
    execute_query('ALTER TABLE commodities DROP COLUMN IF EXISTS item_group_name;')
    execute_query("""
        INSERT INTO commodities (fao_code, item_name, cpc_code)
        SELECT DISTINCT ON ("Item") 
            CAST("Item Code" AS INTEGER), 
            "Item", 
            "CPC Code"
        FROM commodity
        WHERE "Item Code" ~ '^[0-9]+$'
        ORDER BY "Item", "Item Code"
        ON CONFLICT DO NOTHING;
    """)
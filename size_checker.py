from database import fetch_query

def get_table_sizes():
    query = """
    SELECT
        relname AS table_name,
        pg_size_pretty(pg_total_relation_size(relid)) AS formatted_size
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC;
    """
    
    rows = fetch_query(query)
    
    if rows:
        print(f"{'Table Name':<30} | {'Total Size':<10}")
        print("-" * 44)
        for row in rows:
            print(f"{row['table_name']:<30} | {row['formatted_size']:<10}")
    else:
        print("Could not fetch table sizes or no user tables found.")

if __name__ == "__main__":
    get_table_sizes()
from database import fetch_query

def analyze_element_code():
    table_name = "tempcp"
    column_name = "Element Code"

    print(f"Analyzing '{column_name}' distribution in '{table_name}'...")

    # Query to group by Element Code and count occurrences
    query = f"""
    SELECT "{column_name}", COUNT(*) as count
    FROM {table_name}
    GROUP BY "{column_name}"
    ORDER BY count DESC;
    """

    results = fetch_query(query)

    if results:
        # Calculate total rows for percentage calculation
        total_rows = sum(row['count'] for row in results)
        
        print(f"\nTotal Rows: {total_rows}")
        print("-" * 50)
        print(f"{'Element Code':<20} | {'Count':<10} | {'Percentage':<10}")
        print("-" * 50)

        for row in results:
            code = row[column_name]
            count = row['count']
            percentage = (count / total_rows) * 100

            # Handle potential NULL values in display
            display_code = str(code) if code is not None else "NULL"

            print(f"{display_code:<20} | {count:<10} | {percentage:.2f}%")
    else:
        print("No results found or table is empty.")

if __name__ == "__main__":
    analyze_element_code()
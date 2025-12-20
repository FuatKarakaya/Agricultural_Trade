"""
Script to identify missing country codes in the trade_data_final table
that don't exist in the Countries table.
"""
from database import fetch_query

def find_missing_countries():
    output_lines = []
    
    # Find missing reporter countries
    missing_reporters_query = """
        SELECT DISTINCT tf.reporter_code
        FROM trade_data_final tf
        LEFT JOIN Countries c ON tf.reporter_code::integer = c.country_id
        WHERE c.country_id IS NULL
        ORDER BY tf.reporter_code;
    """
    
    # Find missing partner countries
    missing_partners_query = """
        SELECT DISTINCT tf.partner_code
        FROM trade_data_final tf
        LEFT JOIN Countries c ON tf.partner_code::integer = c.country_id
        WHERE c.country_id IS NULL
        ORDER BY tf.partner_code;
    """
    
    # Get count of records affected
    affected_records_query = """
        SELECT 
            COUNT(*) FILTER (WHERE rc.country_id IS NULL) as missing_reporter_records,
            COUNT(*) FILTER (WHERE pc.country_id IS NULL) as missing_partner_records,
            COUNT(*) FILTER (WHERE rc.country_id IS NULL OR pc.country_id IS NULL) as total_affected_records,
            COUNT(*) as total_records
        FROM trade_data_final tf
        LEFT JOIN Countries rc ON tf.reporter_code::integer = rc.country_id
        LEFT JOIN Countries pc ON tf.partner_code::integer = pc.country_id;
    """
    
    output_lines.append("MISSING COUNTRY CODES ANALYSIS")
    output_lines.append("=" * 40)
    
    # Missing reporters
    missing_reporters = fetch_query(missing_reporters_query)
    output_lines.append("\nMissing Reporter Country Codes:")
    if missing_reporters:
        for row in missing_reporters:
            output_lines.append(f"  - {row['reporter_code']}")
    else:
        output_lines.append("  None")
    
    # Missing partners
    missing_partners = fetch_query(missing_partners_query)
    output_lines.append("\nMissing Partner Country Codes:")
    if missing_partners:
        for row in missing_partners:
            output_lines.append(f"  - {row['partner_code']}")
    else:
        output_lines.append("  None")
    
    # Affected records summary
    stats = fetch_query(affected_records_query)
    if stats:
        s = stats[0]
        output_lines.append("\nImpact Summary:")
        output_lines.append(f"  Records with missing reporter: {s['missing_reporter_records']}")
        output_lines.append(f"  Records with missing partner: {s['missing_partner_records']}")
        output_lines.append(f"  Total affected records: {s['total_affected_records']}")
        output_lines.append(f"  Total records in table: {s['total_records']}")
        
        if s['total_records'] > 0:
            percentage = (s['total_affected_records'] / s['total_records']) * 100
            output_lines.append(f"  Percentage affected: {percentage:.2f}%")
    
    # Print all output
    result = "\n".join(output_lines)
    print(result)
    
    # Also save to file
    with open("missing_countries_report.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("\nReport saved to: missing_countries_report.txt")

if __name__ == "__main__":
    find_missing_countries()

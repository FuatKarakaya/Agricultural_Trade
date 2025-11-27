from flask import Blueprint, render_template, request
from database import fetch_query

consumer_price_bp = Blueprint("consumer_price", __name__)

@consumer_price_bp.route("/consumer_prices")
def consumer_prices_dashboard():
    # 1. Handle limit parameter
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50

    # 2. Main Data Query
    # Since Consumer_Prices stores years in rows (Long format), we use aggregation (MAX + CASE)
    # to pivot the data into columns (Wide format) for 2021, 2022, 2023.
    # We also map the numeric types (1, 2, 3) to readable text.
    query = """
        SELECT 
            c.country_name,
            cp.month,
            CASE cp.type
                WHEN 1 THEN 'General Indices (2015=100)'
                WHEN 2 THEN 'Food Indices (2015=100)'
                WHEN 3 THEN 'Food Price Inflation'
                ELSE 'Unknown'
            END as type_name,
            MAX(CASE WHEN cp.year = 2021 THEN cp.value END) as "Y2021",
            MAX(CASE WHEN cp.year = 2022 THEN cp.value END) as "Y2022",
            MAX(CASE WHEN cp.year = 2023 THEN cp.value END) as "Y2023"
        FROM Consumer_Prices cp
        JOIN countries c ON cp.country_id = c.country_id
        WHERE cp.year IN (2021, 2022, 2023)
        GROUP BY c.country_name, cp.month, cp.type
        ORDER BY c.country_name, cp.type, cp.month
        LIMIT %s
    """
    prices = fetch_query(query, (limit,))

    # 3. Statistics Query
    stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT country_id) as total_countries
        FROM Consumer_Prices
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}

    return render_template(
        'consumer_prices.html',
        prices=prices,
        total_records=stats.get('total_records', 0),
        total_countries=stats.get('total_countries', 0),
        current_limit=limit
    )
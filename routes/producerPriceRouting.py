from flask import Blueprint, render_template, request
from database import fetch_query

producer_price_bp = Blueprint("producer_price", __name__)

@producer_price_bp.route("/producer_prices")
def producer_prices_dashboard():
    try:
        limit = int(request.args.get('limit', 30))
    except ValueError:
        limit = 30

    #join Producer_Prices with Countries and Commodities to get readable names
    #fetch the IDs and the last 3 years of data (Y2021, Y2022, Y2023)
    query = """
        SELECT 
            p.unique_id,
            c.country_name,
            cm.item_name,
            p.month,
            p."Y2021",
            p."Y2022",
            p."Y2023"
        FROM Producer_Prices p
        JOIN countries c ON p.country_id = c.country_id
        JOIN commodities cm ON p.commodity_id = cm.fao_code
        ORDER BY c.country_name, cm.item_name, p.month
        LIMIT %s
    """
    prices = fetch_query(query, (limit,))

    #Statistics Query
    stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT country_id) as total_countries,
            COUNT(DISTINCT commodity_id) as total_commodities
        FROM Producer_Prices
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}

    return render_template(
        'producer_prices.html',
        prices=prices,
        total_records=stats.get('total_records', 0),
        total_countries=stats.get('total_countries', 0),
        total_commodities=stats.get('total_commodities', 0),
        current_limit=limit
    )
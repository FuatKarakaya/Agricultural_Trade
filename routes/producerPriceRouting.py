from flask import Blueprint, render_template, request
from database import fetch_query

producer_price_bp = Blueprint("producer_price", __name__)

@producer_price_bp.route("/producer_prices")
def producer_prices_dashboard():
    try:
        limit = int(request.args.get('limit', 30))
    except ValueError:
        limit = 30
    
    # Get filter parameters
    country_filter = request.args.get('country', '')
    commodity_filter = request.args.get('commodity', '')

    # Fetch countries for dropdown
    countries_query = """
        SELECT DISTINCT c.country_id, c.country_name
        FROM countries c
        JOIN Producer_Prices p ON c.country_id = p.country_id
        ORDER BY c.country_name
    """
    countries = fetch_query(countries_query)

    # Fetch commodities for dropdown
    commodities_query = """
        SELECT DISTINCT cm.fao_code, cm.item_name
        FROM commodities cm
        JOIN Producer_Prices p ON cm.fao_code = p.commodity_id
        ORDER BY cm.item_name
    """
    commodities = fetch_query(commodities_query)

    # Build dynamic query with filters
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
        WHERE 1=1
    """
    params = []
    
    if country_filter:
        query += " AND c.country_id = %s"
        params.append(country_filter)
    
    if commodity_filter:
        query += " AND cm.fao_code = %s"
        params.append(commodity_filter)
    
    query += " ORDER BY c.country_name, cm.item_name, p.month LIMIT %s"
    params.append(limit)
    
    prices = fetch_query(query, tuple(params))

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
        countries=countries,
        commodities=commodities,
        selected_country=country_filter,
        selected_commodity=commodity_filter,
        total_records=stats.get('total_records', 0),
        total_countries=stats.get('total_countries', 0),
        total_commodities=stats.get('total_commodities', 0),
        current_limit=limit
    )
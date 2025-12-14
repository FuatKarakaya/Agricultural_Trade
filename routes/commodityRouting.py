from flask import Blueprint, render_template, request
from database import fetch_query

commodity_bp = Blueprint("commodity", __name__)

@commodity_bp.route("/commodities")
def commodities_dashboard():
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50
        
    search_query = request.args.get('search', '').strip()

    base_query = """
        SELECT fao_code, item_name, cpc_code 
        FROM commodities
    """
    params = []
    
    if search_query:
        base_query += " WHERE item_name ILIKE %s"
        params.append(f"%{search_query}%")
    
    base_query += " ORDER BY item_name ASC LIMIT %s"
    params.append(limit)
    
    commodities = fetch_query(base_query, tuple(params))

    stats_query = """
        SELECT 
            COUNT(*) as total_commodities,
            COUNT(cpc_code) as with_cpc
        FROM commodities
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}

    return render_template(
        'commodities.html',
        commodities=commodities,
        total_commodities=stats.get('total_commodities', 0),
        with_cpc=stats.get('with_cpc', 0),
        current_limit=limit,
        search_query=search_query
    )
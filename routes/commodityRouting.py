from flask import Blueprint, render_template, request
from database import fetch_query
from routes.auth_routes import login_required, admin_required

commodity_bp = Blueprint("commodity", __name__)

@commodity_bp.route("/commodities")
@login_required
def commodities_dashboard():
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50
        
    search_query = request.args.get('search', '').strip()

    # Query with FULL OUTER JOIN and GROUP BY to count price records per commodity
    # FULL OUTER JOIN returns all commodities AND all price records (even orphan ones)
    base_query = """
        SELECT 
            cm.fao_code, 
            cm.item_name, 
            cm.cpc_code,
            COUNT(pp.unique_id) as price_records
        FROM Commodities cm
        FULL OUTER JOIN Producer_Prices pp ON cm.fao_code = pp.commodity_id
    """
    params = []
    
    if search_query:
        base_query += " WHERE cm.item_name ILIKE %s"
        params.append(f"%{search_query}%")
    
    # GROUP BY is required when using aggregate functions with non-aggregated columns
    base_query += " GROUP BY cm.fao_code, cm.item_name, cm.cpc_code"
    base_query += " ORDER BY cm.item_name ASC LIMIT %s"
    params.append(limit)
    
    commodities = fetch_query(base_query, tuple(params))

    stats_query = """
        SELECT 
            COUNT(*) as total_commodities,
            COUNT(CASE WHEN cpc_code IS NOT NULL AND cpc_code != '' THEN 1 END) as with_cpc
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
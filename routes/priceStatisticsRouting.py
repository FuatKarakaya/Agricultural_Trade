from flask import Blueprint, render_template, request
from database import fetch_query
from routes.auth_routes import login_required

price_statistics_bp = Blueprint("price_statistics", __name__)

@price_statistics_bp.route("/prices/statistics")
@login_required
def price_statistics_dashboard():
    """
    Price Statistics Dashboard
    - Nested query (derived table)
    - 4-table complex join with commodity filter
    """
    
    # Get commodity filter parameter
    commodity_filter = request.args.get('commodity', '')
    
    # Fetch commodities for dropdown
    commodities_query = """
        SELECT DISTINCT cm.fao_code, cm.item_name
        FROM Commodities cm
        JOIN Producer_Prices pp ON cm.fao_code = pp.commodity_id
        ORDER BY cm.item_name
    """
    commodities = fetch_query(commodities_query)
    
    # ==================== NESTED QUERY (Derived Table) ====================
    commodity_stats_query = """
        SELECT 
            cm.item_name as commodity_name,
            commodity_stats.total_records,
            commodity_stats.country_count,
            ROUND(commodity_stats.avg_price::numeric, 2) as avg_price
        FROM (
            SELECT 
                commodity_id,
                COUNT(*) as total_records,
                COUNT(DISTINCT country_id) as country_count,
                AVG(value) as avg_price
            FROM Producer_Prices
            WHERE value IS NOT NULL
            GROUP BY commodity_id
        ) commodity_stats
        JOIN Commodities cm ON cm.fao_code = commodity_stats.commodity_id
        ORDER BY commodity_stats.avg_price DESC
        LIMIT 5
    """
    commodity_stats = fetch_query(commodity_stats_query)
    
    # ==================== 4-TABLE JOIN (with GROUP BY for yearly avg) ====================
    four_table_query = """
        SELECT 
            c.country_name,
            cm.item_name as commodity_name,
            pp.year,
            ROUND(AVG(pp.value)::numeric, 2) as avg_price,
            ROUND(MAX(p.quantity)::numeric, 0) as production_qty
        FROM Producer_Prices pp
        JOIN Countries c ON c.country_id = pp.country_id
        JOIN Commodities cm ON cm.fao_code = pp.commodity_id
        JOIN Production p ON p.country_code = pp.country_id 
                          AND p.commodity_code = pp.commodity_id 
                          AND p.year = pp.year
        WHERE pp.value IS NOT NULL AND p.quantity IS NOT NULL
    """
    params = []
    
    if commodity_filter:
        four_table_query += " AND cm.fao_code = %s"
        params.append(commodity_filter)
    
    four_table_query += """
        GROUP BY c.country_name, cm.item_name, pp.year
        ORDER BY pp.year DESC, avg_price DESC
        LIMIT 10
    """
    
    four_table_data = fetch_query(four_table_query, tuple(params) if params else None)
    
    return render_template(
        'price_statistics.html',
        commodity_stats=commodity_stats,
        four_table_data=four_table_data,
        commodities=commodities,
        selected_commodity=commodity_filter,
    )

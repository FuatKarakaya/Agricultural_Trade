from flask import Blueprint, render_template, request
from database import execute_query, fetch_query

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/trades")
def Trade_data_long_dashboard():
    
    
    selected_reporter = request.args.get('reporter_countries', '')
    selected_partner = request.args.get('partner_countries', '')
    selected_element = request.args.get('element', '')
    selected_year = request.args.get('year', '')
    selected_commodity = request.args.get('commodity', '')
    sort_by = request.args.get('sort', 'value_desc')
    
    
    query = """
        SELECT 
            tf.*,
            rc.country_name as reporter_name,
            pc.country_name as partner_name,
            c.item_name
        FROM Trade_data_long tf
        LEFT JOIN Countries rc ON tf.reporter_countries = rc.country_id
        LEFT JOIN Countries pc ON tf.partner_countries = pc.country_id
        LEFT JOIN Commodities c ON tf.item = c.item_name
        WHERE 1=1
    """
    #change to fao code
    params = []
    

    query += " LIMIT 100"
    
    # Fetch trade flows
    Trade_data_long = fetch_query(query, tuple(params))
    
    # Get all countries for filter dropdown
    countries = fetch_query("SELECT country_id, country_name FROM Countries ORDER BY country_name")
    
    # Get all commodities for filter dropdown
    commodities = fetch_query("SELECT fao_code, item_name FROM Commodities ORDER BY item_name")
    
    # Get available years
    years_data = fetch_query("SELECT DISTINCT year FROM Trade_data_long ORDER BY year DESC")
    available_years = [row['year'] for row in years_data] if years_data else []
    
    # Calculate statistics
    stats_query = """
        SELECT 
            COUNT(*) as total_trades,
            SUM(value) as total_value,
            COUNT(DISTINCT reporter_countries) + COUNT(DISTINCT partner_countries) as active_countries,
            COUNT(DISTINCT item) as traded_commodities
        FROM Trade_data_long
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}
    
    # Get trade type breakdown
    element_query = """
        SELECT 
            element,
            COUNT(*) as count,
            SUM(value) as total_value,
            AVG(value) as avg_value
        FROM Trade_data_long
        GROUP BY element
        ORDER BY total_value DESC
    """
    element_data = fetch_query(element_query)
    
    element_breakdown = ""
    top_partners = ""
    

    
    # Pass all variables to template
    return render_template(
        'trade_flows.html',
        trade_flows=Trade_data_long or [],
        countries=countries or [],
        commodities=commodities or [],
        available_years=available_years,
        selected_reporter=selected_reporter,
        selected_partner=selected_partner,
        selected_element=selected_element,
        selected_year=selected_year,
        selected_commodity=selected_commodity,
        sort_by=sort_by,
        total_trades=stats.get('total_trades', 0),
        total_value=stats.get('total_value', 0),
        active_countries=stats.get('active_countries', 0),
        traded_commodities=stats.get('traded_commodities', 0),
        element_breakdown=element_breakdown,
        top_partners=top_partners,
    )



@trade_bp.route("/trades/<int:trade_id>")
def trade_detailed(trade_id):
    return 
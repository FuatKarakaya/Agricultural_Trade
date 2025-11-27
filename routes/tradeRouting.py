from flask import Blueprint, render_template, request
from database import execute_query, fetch_query

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/trades")
def Trade_data_long_dashboard():
    
    # Get filter parameters - match the template form field names
    selected_reporter = request.args.get('reporter_country', '')
    selected_partner = request.args.get('partner_country', '')
    selected_trade_type = request.args.get('trade_type', '')
    selected_year = request.args.get('year', '')
    selected_commodity = request.args.get('commodity', '')
    sort_by = request.args.get('sort', 'value_desc')
    
    # Build query with filters
    query = """
        SELECT 
            tf.unique_id,
            tf.reporter_countries AS reporter_country,
            tf.partner_countries AS partner_country,
            tf.item_code AS trade_item,
            tf.item,
            tf.element AS trade_type,
            tf.unit,
            tf.year,
            tf.value,
            rc.country_name AS reporter_name,
            pc.country_name AS partner_name,
            c.item_name AS commodity_name
        FROM Trade_data_long AS tf
        LEFT JOIN Countries AS rc ON tf.reporter_countries = rc.country_id
        LEFT JOIN Countries AS pc ON tf.partner_countries = pc.country_id
        LEFT JOIN Commodities AS c ON c.fao_code = tf.item_code
        WHERE 1=1
    """
    
    params = []
    
    # Apply filters
    if selected_reporter:
        query += " AND tf.reporter_countries = %s"
        params.append(selected_reporter)
    
    if selected_partner:
        query += " AND tf.partner_countries = %s"
        params.append(selected_partner)
    
    if selected_trade_type:
        query += " AND tf.element = %s"
        params.append(selected_trade_type)
    
    if selected_year:
        query += " AND tf.year = %s"
        params.append(selected_year)
    
    if selected_commodity:
        query += " AND tf.item_code = %s"
        params.append(selected_commodity)
    
    # Add sorting
    if sort_by == 'value_desc':
        query += " ORDER BY tf.value DESC NULLS LAST"
    elif sort_by == 'value_asc':
        query += " ORDER BY tf.value ASC NULLS LAST"
    elif sort_by == 'year_desc':
        query += " ORDER BY tf.year DESC"
    elif sort_by == 'year_asc':
        query += " ORDER BY tf.year ASC"
    else:
        query += " ORDER BY tf.value DESC NULLS LAST"
    
    query += " LIMIT 100;"
    
    # Fetch trade flows
    trade_flows = fetch_query(query, tuple(params) if params else None)
    
    # Get all countries for filter dropdowns (template expects 'country_code' and 'country_name')
    countries_query = """
        SELECT country_id AS country_code, country_name 
        FROM Countries 
        ORDER BY country_name
    """
    countries = fetch_query(countries_query)
    
    # Get all commodities for filter dropdown (template expects 'fao_code' and 'commodity_name')
    commodities_query = """
        SELECT fao_code, item_name AS commodity_name 
        FROM Commodities 
        ORDER BY item_name
    """
    commodities = fetch_query(commodities_query)
    
    # Get available years
    years_data = fetch_query("SELECT DISTINCT year FROM Trade_data_long ORDER BY year DESC")
    available_years = [row['year'] for row in years_data] if years_data else []
    
    # Calculate statistics (apply same filters for accurate stats)
    stats_base = """
        FROM Trade_data_long tf
        WHERE 1=1
    """
    stats_params = []
    
    if selected_reporter:
        stats_base += " AND tf.reporter_countries = %s"
        stats_params.append(selected_reporter)
    if selected_partner:
        stats_base += " AND tf.partner_countries = %s"
        stats_params.append(selected_partner)
    if selected_trade_type:
        stats_base += " AND tf.element = %s"
        stats_params.append(selected_trade_type)
    if selected_year:
        stats_base += " AND tf.year = %s"
        stats_params.append(selected_year)
    if selected_commodity:
        stats_base += " AND tf.item_code = %s"
        stats_params.append(selected_commodity)
    
    stats_query = f"""
        SELECT 
            COUNT(*) as total_trades,
            COALESCE(SUM(value), 0) as total_value,
            COUNT(DISTINCT reporter_countries) + COUNT(DISTINCT partner_countries) as active_countries,
            COUNT(DISTINCT item_code) as traded_commodities
        {stats_base}
    """
    stats_result = fetch_query(stats_query, tuple(stats_params) if stats_params else None)
    stats = stats_result[0] if stats_result else {}
    
    # Get trade type breakdown (template expects 'trade_type_breakdown' dict)
    trade_type_query = f"""
        SELECT 
            element as trade_type,
            COUNT(*) as count,
            COALESCE(SUM(value), 0) as total_value,
            COALESCE(AVG(value), 0) as avg_value
        {stats_base}
        GROUP BY element
        ORDER BY total_value DESC
    """
    trade_type_data = fetch_query(trade_type_query, tuple(stats_params) if stats_params else None)
    
    # Convert to dict format expected by template
    trade_type_breakdown = {}
    total_count = sum(row['count'] for row in trade_type_data) if trade_type_data else 0
    for row in (trade_type_data or []):
        trade_type_breakdown[row['trade_type']] = {
            'count': row['count'],
            'total_value': row['total_value'],
            'avg_value': row['avg_value'],
            'percentage': (row['count'] / total_count * 100) if total_count > 0 else 0
        }
    
    # Get top trading partners
    top_partners_query = """
        SELECT 
            tf.reporter_countries,
            tf.partner_countries,
            rc.country_name AS reporter_name,
            pc.country_name AS partner_name,
            COUNT(*) AS transaction_count,
            COALESCE(SUM(tf.value), 0) AS total_value,
            MODE() WITHIN GROUP (ORDER BY c.item_name) AS top_commodity
        FROM Trade_data_long tf
        LEFT JOIN Countries rc ON tf.reporter_countries = rc.country_id
        LEFT JOIN Countries pc ON tf.partner_countries = pc.country_id
        LEFT JOIN Commodities c ON c.fao_code = tf.item_code
        GROUP BY tf.reporter_countries, tf.partner_countries, rc.country_name, pc.country_name
        ORDER BY total_value DESC
        LIMIT 10
    """
    top_partners = fetch_query(top_partners_query)
    
    # Get top traded commodities
    top_commodities_query = """
        SELECT 
            tf.item_code AS fao_code,
            c.item_name AS commodity_name,
            COUNT(*) AS trade_count,
            COALESCE(SUM(tf.value), 0) AS total_value,
            COUNT(DISTINCT tf.reporter_countries) + COUNT(DISTINCT tf.partner_countries) AS country_count,
            COALESCE(AVG(tf.value), 0) AS avg_value
        FROM Trade_data_long tf
        LEFT JOIN Commodities c ON c.fao_code = tf.item_code
        GROUP BY tf.item_code, c.item_name
        ORDER BY total_value DESC
        LIMIT 6
    """
    top_commodities_traded = fetch_query(top_commodities_query)
    
    # Pass all variables to template
    return render_template(
        'trade_flows.html',
        trade_flows=trade_flows or [],
        # Filter dropdown data
        reporter_countries=countries or [],
        partner_countries=countries or [],
        available_commodities=commodities or [],
        available_years=available_years,
        # Selected filter values
        selected_reporter=selected_reporter,
        selected_partner=selected_partner,
        selected_trade_type=selected_trade_type,
        selected_year=selected_year,
        selected_commodity=selected_commodity,
        sort_by=sort_by,
        # Statistics
        total_trades=stats.get('total_trades', 0),
        total_value=stats.get('total_value', 0),
        active_countries=stats.get('active_countries', 0),
        traded_commodities=stats.get('traded_commodities', 0),
        # Additional sections
        trade_type_breakdown=trade_type_breakdown,
        top_partners=top_partners or [],
        top_commodities_traded=top_commodities_traded or [],
    )


@trade_bp.route("/trades/<int:trade_id>")
def trade_detailed(trade_id):
    return 
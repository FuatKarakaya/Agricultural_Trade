from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import execute_query, fetch_query

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/trades")
def Trade_data_long_dashboard():
    
    # Get filter parameters
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
    
    # Get all countries for filter dropdowns
    countries_query = """
        SELECT country_id AS country_code, country_name 
        FROM Countries 
        ORDER BY country_name
    """
    countries = fetch_query(countries_query)
    
    # Get all commodities for filter dropdown
    commodities_query = """
        SELECT fao_code, item_name AS commodity_name 
        FROM Commodities 
        ORDER BY item_name
    """
    commodities = fetch_query(commodities_query)
    
    # Get available years
    years_data = fetch_query("SELECT DISTINCT year FROM Trade_data_long ORDER BY year DESC")
    available_years = [row['year'] for row in years_data] if years_data else []

    # Get available trade type
    trade_types_data = fetch_query("SELECT DISTINCT element FROM Trade_data_long WHERE element IS NOT NULL ORDER BY element")
    available_trade_types = [row['element'] for row in trade_types_data] if trade_types_data else []

    # Get available units
    units_data = fetch_query("SELECT DISTINCT unit FROM Trade_data_long WHERE unit IS NOT NULL ORDER BY unit")
    available_units = [row['unit'] for row in units_data] if units_data else []
    
    # Calculate statistics
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
    
    # Get trade type breakdownn
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
        available_trade_types=available_trade_types,
        available_units=available_units,
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


@trade_bp.route("/trades/add", methods=["POST"])
def add_trade_flow():
    
    try:
        # Get form data
        reporter_country = request.form.get('reporter_country')
        partner_country = request.form.get('partner_country')
        commodity = request.form.get('commodity')
        trade_type = request.form.get('trade_type')
        year = request.form.get('year')
        value = request.form.get('value')
        unit = request.form.get('unit')

        
        if reporter_country == partner_country:
            flash("Reporter country and partner country must be different!", "error")
            return redirect(url_for('trade.Trade_data_long_dashboard'))

        # Insert query
        insert_query = """
            INSERT INTO Trade_data_long
            (reporter_countries, partner_countries, item_code, element, unit, year, value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (reporter_country, partner_country, commodity, trade_type, unit, year, value)

        # Execute the insert
        execute_query(insert_query, params)

        flash("Trade flow record added successfully!", "success")
        return redirect(url_for('trade.Trade_data_long_dashboard'))

    except Exception as e:
        flash(f"Error adding trade flow: {str(e)}", "error")
        return redirect(url_for('trade.Trade_data_long_dashboard'))


@trade_bp.route("/trades/edit/<int:trade_id>", methods=["POST"])
def edit_trade_flow(trade_id):
    try:
        # Get form data
        reporter_country = request.form.get('reporter_country')
        partner_country = request.form.get('partner_country')
        commodity = request.form.get('commodity')
        trade_type = request.form.get('trade_type')
        year = request.form.get('year')
        value = request.form.get('value')
        unit = request.form.get('unit')

        if reporter_country == partner_country:
            flash("Reporter country and partner country must be different!", "error")
            return redirect(url_for('trade.Trade_data_long_dashboard'))

        # Update query
        update_query = """
            UPDATE Trade_data_long
            SET reporter_countries = %s,
                partner_countries = %s,
                item_code = %s,
                element = %s,
                unit = %s,
                year = %s,
                value = %s
            WHERE unique_id = %s
        """

        params = (reporter_country, partner_country, commodity, trade_type, unit, year, value, trade_id)

        # Execute the update
        execute_query(update_query, params)

        flash("Trade flow record updated successfully!", "success")
        return redirect(url_for('trade.Trade_data_long_dashboard'))

    except Exception as e:
        flash(f"Error updating trade flow: {str(e)}", "error")
        return redirect(url_for('trade.Trade_data_long_dashboard'))


@trade_bp.route("/trades/delete/<int:trade_id>", methods=["POST"])
def delete_trade_flow(trade_id):
    try:
        # Delete query
        delete_query = "DELETE FROM Trade_data_long WHERE unique_id = %s"

        # Execute the delete
        execute_query(delete_query, (trade_id,))

        flash("Trade flow record deleted successfully!", "success")
        return redirect(url_for('trade.Trade_data_long_dashboard'))

    except Exception as e:
        flash(f"Error deleting trade flow: {str(e)}", "error")
        return redirect(url_for('trade.Trade_data_long_dashboard'))


@trade_bp.route("/trades/statistics")
def trade_statistics():
    """Trade Flows Statistics Dashboard with Charts"""

    try:
        # Query 1: Time Series Data (Exports vs Imports by Year)
        time_series_query = """
            SELECT
                tf.year,
                tf.element AS trade_type,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(tf.value), 0) AS total_value
            FROM Trade_data_long tf
            WHERE tf.element IN ('Export', 'Import') AND tf.year IS NOT NULL
            GROUP BY tf.year, tf.element
            ORDER BY tf.year ASC
        """
        time_series_raw = fetch_query(time_series_query)

        # Format time series data for Chart.js
        years = sorted(list(set([row['year'] for row in time_series_raw])))
        exports_data = []
        imports_data = []

        for year in years:
            export_row = next((r for r in time_series_raw if r['year'] == year and r['trade_type'] == 'Export'), None)
            import_row = next((r for r in time_series_raw if r['year'] == year and r['trade_type'] == 'Import'), None)
            exports_data.append(export_row['total_value'] if export_row else 0)
            imports_data.append(import_row['total_value'] if import_row else 0)

        time_series_data = {
            'labels': years,
            'exports': exports_data,
            'imports': imports_data
        }

        # Query 2: Top Trading Countries
        top_countries_query = """
            SELECT
                c.country_name,
                c.country_id,
                COUNT(DISTINCT tf.unique_id) AS trade_count,
                COALESCE(SUM(tf.value), 0) AS total_trade_value
            FROM Trade_data_long tf
            LEFT JOIN Countries c ON (tf.reporter_countries = c.country_id)
            WHERE c.country_name IS NOT NULL
            GROUP BY c.country_id, c.country_name

            UNION ALL

            SELECT
                c.country_name,
                c.country_id,
                COUNT(DISTINCT tf.unique_id) AS trade_count,
                COALESCE(SUM(tf.value), 0) AS total_trade_value
            FROM Trade_data_long tf
            LEFT JOIN Countries c ON (tf.partner_countries = c.country_id)
            WHERE c.country_name IS NOT NULL
            GROUP BY c.country_id, c.country_name
        """
        top_countries_raw = fetch_query(top_countries_query)

        # Aggregate by country (sum duplicates from reporter and partner)
        country_totals = {}
        for row in top_countries_raw:
            country_name = row['country_name']
            if country_name in country_totals:
                country_totals[country_name] += row['total_trade_value']
            else:
                country_totals[country_name] = row['total_trade_value']

        # Sort and get top 10
        sorted_countries = sorted(country_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        top_countries_data = {
            'labels': [c[0] for c in sorted_countries],
            'values': [c[1] for c in sorted_countries]
        }

        # Query 3: Trade Balance by Country
        trade_balance_query = """
            SELECT
                c.country_name,
                COALESCE(SUM(CASE WHEN tf.element = 'Export' THEN tf.value ELSE 0 END), 0) AS exports,
                COALESCE(SUM(CASE WHEN tf.element = 'Import' THEN tf.value ELSE 0 END), 0) AS imports
            FROM Trade_data_long tf
            LEFT JOIN Countries c ON tf.reporter_countries = c.country_id
            WHERE c.country_name IS NOT NULL
            GROUP BY c.country_id, c.country_name
            ORDER BY ABS(COALESCE(SUM(CASE WHEN tf.element = 'Export' THEN tf.value ELSE 0 END), 0) -
                         COALESCE(SUM(CASE WHEN tf.element = 'Import' THEN tf.value ELSE 0 END), 0)) DESC
            LIMIT 15
        """
        trade_balance_raw = fetch_query(trade_balance_query)

        trade_balance_data = {
            'labels': [row['country_name'] for row in trade_balance_raw],
            'exports': [row['exports'] for row in trade_balance_raw],
            'imports': [row['imports'] for row in trade_balance_raw],
            'balance': [row['exports'] - row['imports'] for row in trade_balance_raw]
        }

        # Query 4: Top Commodities Distribution
        commodities_query = """
            SELECT
                c.item_name,
                COUNT(*) AS trade_count,
                COALESCE(SUM(tf.value), 0) AS total_value
            FROM Trade_data_long tf
            LEFT JOIN Commodities c ON tf.item_code = c.fao_code
            WHERE c.item_name IS NOT NULL
            GROUP BY c.item_name
            ORDER BY total_value DESC
            LIMIT 8
        """
        commodities_raw = fetch_query(commodities_query)

        commodities_data = {
            'labels': [row['item_name'] for row in commodities_raw],
            'values': [row['total_value'] for row in commodities_raw]
        }

        # Query 5: Regional Trade Distribution (skip if no region column)
        regional_query = """
            SELECT
                COALESCE(c.region, 'Unknown') AS region,
                COUNT(*) AS trade_count,
                COALESCE(SUM(tf.value), 0) AS total_value
            FROM Trade_data_long tf
            LEFT JOIN Countries c ON tf.reporter_countries = c.country_id
            WHERE c.region IS NOT NULL
            GROUP BY c.region
            ORDER BY total_value DESC
        """
        try:
            regional_raw = fetch_query(regional_query)
            regional_data = {
                'labels': [row['region'] for row in regional_raw],
                'values': [row['total_value'] for row in regional_raw]
            }
        except:
            # If region column doesn't exist, use placeholder
            regional_data = {
                'labels': ['Data Not Available'],
                'values': [0]
            }

        # Query 6: Yearly Trade Volume
        volume_query = """
            SELECT
                tf.year,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(tf.value), 0) AS total_value,
                COALESCE(AVG(tf.value), 0) AS avg_value
            FROM Trade_data_long tf
            WHERE tf.year IS NOT NULL
            GROUP BY tf.year
            ORDER BY tf.year ASC
        """
        volume_raw = fetch_query(volume_query)

        volume_data = {
            'labels': [row['year'] for row in volume_raw],
            'values': [row['total_value'] for row in volume_raw],
            'counts': [row['transaction_count'] for row in volume_raw]
        }

        # Calculate Summary Statistics
        summary_query = """
            SELECT
                COUNT(*) as total_trades,
                COALESCE(SUM(value), 0) as total_value,
                COUNT(DISTINCT reporter_countries) as reporter_countries_count,
                COUNT(DISTINCT partner_countries) as partner_countries_count,
                MIN(year) as min_year,
                MAX(year) as max_year
            FROM Trade_data_long
        """
        summary = fetch_query(summary_query)[0]

        total_trades = summary['total_trades']
        total_value = summary['total_value']
        total_countries = summary['reporter_countries_count'] + summary['partner_countries_count']
        year_range = f"{summary['min_year']}-{summary['max_year']}"

        # Render template with all data
        return render_template(
            'trade_statistics.html',
            time_series_data=time_series_data,
            top_countries_data=top_countries_data,
            trade_balance_data=trade_balance_data,
            commodities_data=commodities_data,
            regional_data=regional_data,
            volume_data=volume_data,
            total_trades=total_trades,
            total_value=total_value,
            total_countries=total_countries,
            year_range=year_range
        )

    except Exception as e:
        flash(f"Error loading statistics: {str(e)}", "error")
        return redirect(url_for('trade.Trade_data_long_dashboard'))


@trade_bp.route("/trades/<int:trade_id>")
def trade_detailed(trade_id):
    return
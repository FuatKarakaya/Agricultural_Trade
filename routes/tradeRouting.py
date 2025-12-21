from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import execute_query, fetch_query
from routes.auth_routes import admin_required, login_required

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/trades")
@login_required
def trade_data_final_dashboard():

    # Get filter parameters (multi-select)
    selected_reporters = request.args.getlist('reporter_country')
    selected_partners = request.args.getlist('partner_country')
    selected_trade_types = request.args.getlist('trade_type')
    selected_years = request.args.getlist('year')
    selected_commodities = request.args.getlist('commodity')
    sort_by = request.args.get('sort', 'value_desc')

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 20  # Items per page
    offset = (page - 1) * per_page

    # Build query with filters
    query = """
        SELECT
            tf.unique_id,
            tf.reporter_code AS reporter_country,
            tf.partner_code AS partner_country,
            tf.item_code AS trade_item,
            tf.trade_type,
            tf.year,
            tf.qty_tonnes,
            tf.val_1k_usd,
            rc.country_name AS reporter_name,
            pc.country_name AS partner_name,
            c.item_name AS commodity_name
        FROM trade_data_final AS tf
        LEFT JOIN Countries AS rc ON tf.reporter_code = rc.country_id
        LEFT JOIN Countries AS pc ON tf.partner_code = pc.country_id
        LEFT JOIN Commodities AS c ON tf.item_code::integer = c.fao_code
        WHERE 1=1
    """

    params = []

    # Apply filters (multi-select)
    if selected_reporters:
        placeholders = ', '.join(['%s'] * len(selected_reporters))
        query += f" AND tf.reporter_code IN ({placeholders})"
        params.extend(selected_reporters)

    if selected_partners:
        placeholders = ', '.join(['%s'] * len(selected_partners))
        query += f" AND tf.partner_code IN ({placeholders})"
        params.extend(selected_partners)

    if selected_trade_types:
        placeholders = ', '.join(['%s'] * len(selected_trade_types))
        query += f" AND tf.trade_type IN ({placeholders})"
        params.extend(selected_trade_types)

    if selected_years:
        placeholders = ', '.join(['%s'] * len(selected_years))
        query += f" AND tf.year IN ({placeholders})"
        params.extend([int(y) for y in selected_years])

    if selected_commodities:
        placeholders = ', '.join(['%s'] * len(selected_commodities))
        query += f" AND tf.item_code IN ({placeholders})"
        params.extend(selected_commodities)
    
    # Add sorting - expanded to support all columns
    sort_options = {
        'year_desc': 'tf.year DESC',
        'year_asc': 'tf.year ASC',
        'reporter_asc': 'rc.country_name ASC',
        'reporter_desc': 'rc.country_name DESC',
        'partner_asc': 'pc.country_name ASC',
        'partner_desc': 'pc.country_name DESC',
        'type_asc': 'tf.trade_type ASC',
        'type_desc': 'tf.trade_type DESC',
        'commodity_asc': 'c.item_name ASC',
        'commodity_desc': 'c.item_name DESC',
        'qty_asc': 'tf.qty_tonnes ASC NULLS LAST',
        'qty_desc': 'tf.qty_tonnes DESC NULLS LAST',
        'value_asc': 'tf.val_1k_usd ASC NULLS LAST',
        'value_desc': 'tf.val_1k_usd DESC NULLS LAST',
    }

    order_by = sort_options.get(sort_by, 'tf.val_1k_usd DESC NULLS LAST')
    query += f" ORDER BY {order_by}"

    # Get total count for pagination (before adding LIMIT/OFFSET)
    count_query = f"SELECT COUNT(*) as total {query[query.find('FROM'):]}"
    count_query = count_query.split('ORDER BY')[0]  # Remove ORDER BY for count
    total_records = fetch_query(count_query, tuple(params) if params else None)
    total_count = total_records[0]['total'] if total_records else 0
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    # Add pagination
    query += f" LIMIT {per_page} OFFSET {offset};"

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
    years_data = fetch_query("SELECT DISTINCT year FROM trade_data_final ORDER BY year DESC")
    available_years = [row['year'] for row in years_data] if years_data else []

    # Get available trade type
    trade_types_data = fetch_query("SELECT DISTINCT trade_type FROM trade_data_final WHERE trade_type IS NOT NULL ORDER BY trade_type")
    available_trade_types = [row['trade_type'] for row in trade_types_data] if trade_types_data else []
    
    # Calculate statistics
    stats_base = """
        FROM trade_data_final tf
        WHERE 1=1
    """
    stats_params = []

    if selected_reporters:
        placeholders = ', '.join(['%s'] * len(selected_reporters))
        stats_base += f" AND tf.reporter_code IN ({placeholders})"
        stats_params.extend(selected_reporters)
    if selected_partners:
        placeholders = ', '.join(['%s'] * len(selected_partners))
        stats_base += f" AND tf.partner_code IN ({placeholders})"
        stats_params.extend(selected_partners)
    if selected_trade_types:
        placeholders = ', '.join(['%s'] * len(selected_trade_types))
        stats_base += f" AND tf.trade_type IN ({placeholders})"
        stats_params.extend(selected_trade_types)
    if selected_years:
        placeholders = ', '.join(['%s'] * len(selected_years))
        stats_base += f" AND tf.year IN ({placeholders})"
        stats_params.extend([int(y) for y in selected_years])
    if selected_commodities:
        placeholders = ', '.join(['%s'] * len(selected_commodities))
        stats_base += f" AND tf.item_code IN ({placeholders})"
        stats_params.extend(selected_commodities)
    
    stats_query = f"""
        SELECT
            COUNT(*) as total_trades,
            COALESCE(SUM(val_1k_usd), 0) as total_value,
            COUNT(DISTINCT reporter_code) + COUNT(DISTINCT partner_code) as active_countries,
            COUNT(DISTINCT item_code) as traded_commodities
        {stats_base}
    """
    stats_result = fetch_query(stats_query, tuple(stats_params) if stats_params else None)
    stats = stats_result[0] if stats_result else {}
    
    # Get trade type breakdownn
    trade_type_query = f"""
        SELECT
            trade_type,
            COUNT(*) as count,
            COALESCE(SUM(val_1k_usd), 0) as total_value,
            COALESCE(AVG(val_1k_usd), 0) as avg_value
        {stats_base}
        GROUP BY trade_type
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
    # This query demonstrates ALL rubric requirements:
    # 1. NESTED QUERY: Subquery for percentage of global trade
    # 2. COMPLEX JOIN: 5 tables (trade_data_final + Countries x2 + Commodities + Production)
    # 3. GROUP BY: Grouped by country pairs and regions
    # 4. OUTER JOIN: All LEFT JOINs to include trades even without production data
    top_partners_query = """
        SELECT
            tf.reporter_code,
            tf.partner_code,
            rc.country_name AS reporter_name,
            rc.region AS reporter_region,
            pc.country_name AS partner_name,
            pc.region AS partner_region,
            COUNT(*) AS transaction_count,
            COALESCE(SUM(tf.val_1k_usd), 0) AS total_value,
            COALESCE(SUM(tf.qty_tonnes), 0) AS total_quantity,
            MODE() WITHIN GROUP (ORDER BY c.item_name) AS top_commodity,
            -- NESTED QUERY: Calculate percentage of global trade (Requirement 1)
            ROUND(
                (COALESCE(SUM(tf.val_1k_usd), 0) /
                 NULLIF((SELECT SUM(val_1k_usd) FROM trade_data_final), 0) * 100),
                2
            ) AS pct_of_global_trade,
            -- Check if reporter country produces what they trade
            CASE
                WHEN SUM(COALESCE(p.quantity, 0)) > 0 THEN 'Producer & Trader'
                ELSE 'Trader Only'
            END AS trade_classification,
            COALESCE(SUM(p.quantity), 0) AS domestic_production
        FROM trade_data_final tf
        -- TABLE 1 & 2: Reporter Country with region (OUTER JOIN - Requirement 4)
        LEFT JOIN Countries rc ON tf.reporter_code = rc.country_id
        -- TABLE 3: Partner Country with region (OUTER JOIN - Requirement 4)
        LEFT JOIN Countries pc ON tf.partner_code = pc.country_id
        -- TABLE 4: Commodities (OUTER JOIN - Requirement 4)
        LEFT JOIN Commodities c ON tf.item_code::integer = c.fao_code
        -- TABLE 5: Production to check domestic production (OUTER JOIN - Requirement 4)
        LEFT JOIN production p ON tf.reporter_code = p.country_code
                                AND tf.item_code::integer = p.commodity_code
                                AND tf.year = p.year
        WHERE tf.year >= 2015
        -- GROUP BY clause (Requirement 3)
        GROUP BY
            tf.reporter_code,
            tf.partner_code,
            rc.country_name,
            rc.region,
            pc.country_name,
            pc.region
        HAVING COUNT(*) > 0
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
            COALESCE(SUM(tf.val_1k_usd), 0) AS total_value,
            COUNT(DISTINCT tf.reporter_code) + COUNT(DISTINCT tf.partner_code) AS country_count,
            COALESCE(AVG(tf.val_1k_usd), 0) AS avg_value
        FROM trade_data_final tf
        LEFT JOIN Commodities c ON tf.item_code::integer = c.fao_code
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
        # Selected filter values
        selected_reporters=selected_reporters,
        selected_partners=selected_partners,
        selected_trade_types=selected_trade_types,
        selected_years=selected_years,
        selected_commodities=selected_commodities,
        sort_by=sort_by,
        # Statistics
        total_trades=stats.get('total_trades', 0),
        total_value=1000 * stats.get('total_value', 0),
        active_countries=stats.get('active_countries', 0),
        traded_commodities=stats.get('traded_commodities', 0),
        # Additional sections
        trade_type_breakdown=trade_type_breakdown,
        top_partners=top_partners or [],
        top_commodities_traded=top_commodities_traded or [],
        # Pagination
        page=page,
        total_pages=total_pages,
        total_count=total_count,
        per_page=per_page,
    )


@trade_bp.route("/trades/add", methods=["POST"])
@admin_required
def add_trade_flow():

    try:
        # Get form data
        reporter_country = request.form.get('reporter_country')
        partner_country = request.form.get('partner_country')
        commodity = request.form.get('commodity')
        trade_type = request.form.get('trade_type')
        year = request.form.get('year')
        qty_tonnes = request.form.get('qty_tonnes')
        val_1k_usd = request.form.get('val_1k_usd')

        # Validate that at least one of quantity or value is provided
        qty_valid = qty_tonnes and qty_tonnes.strip() != '' and float(qty_tonnes) > 0
        val_valid = val_1k_usd and val_1k_usd.strip() != '' and float(val_1k_usd) > 0

        if not qty_valid and not val_valid:
            flash("Please provide either Quantity or Value (at least one is required)!", "error")
            return redirect(url_for('trade.trade_data_final_dashboard'))

        if reporter_country == partner_country:
            flash("Reporter country and partner country must be different!", "error")
            return redirect(url_for('trade.trade_data_final_dashboard'))

        # Convert empty strings or invalid values to None for database
        qty_tonnes = float(qty_tonnes) if qty_valid else None
        val_1k_usd = float(val_1k_usd) if val_valid else None

        # Insert query
        insert_query = """
            INSERT INTO trade_data_final
            (reporter_code, partner_code, item_code, trade_type, year, qty_tonnes, val_1k_usd)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (reporter_country, partner_country, commodity, trade_type, year, qty_tonnes, val_1k_usd)

        # Execute the insert
        execute_query(insert_query, params)

        flash("Trade flow record added successfully!", "success")
        return redirect(url_for('trade.trade_data_final_dashboard'))

    except Exception as e:
        flash(f"Error adding trade flow: {str(e)}", "error")
        return redirect(url_for('trade.trade_data_final_dashboard'))


@trade_bp.route("/trades/edit/<int:trade_id>", methods=["POST"])
@admin_required
def edit_trade_flow(trade_id):
    try:
        # Get form data
        reporter_country = request.form.get('reporter_country')
        partner_country = request.form.get('partner_country')
        commodity = request.form.get('commodity')
        trade_type = request.form.get('trade_type')
        year = request.form.get('year')
        qty_tonnes = request.form.get('qty_tonnes')
        val_1k_usd = request.form.get('val_1k_usd')

        # Validate that at least one of quantity or value is provided
        qty_valid = qty_tonnes and qty_tonnes.strip() != '' and float(qty_tonnes) > 0
        val_valid = val_1k_usd and val_1k_usd.strip() != '' and float(val_1k_usd) > 0

        if not qty_valid and not val_valid:
            flash("Please provide either Quantity or Value (at least one is required)!", "error")
            return redirect(url_for('trade.trade_data_final_dashboard'))

        if reporter_country == partner_country:
            flash("Reporter country and partner country must be different!", "error")
            return redirect(url_for('trade.trade_data_final_dashboard'))

        # Convert empty strings or invalid values to None for database
        qty_tonnes = float(qty_tonnes) if qty_valid else None
        val_1k_usd = float(val_1k_usd) if val_valid else None

        # Update query
        update_query = """
            UPDATE trade_data_final
            SET reporter_code = %s,
                partner_code = %s,
                item_code = %s,
                trade_type = %s,
                year = %s,
                qty_tonnes = %s,
                val_1k_usd = %s
            WHERE unique_id = %s
        """

        params = (reporter_country, partner_country, commodity, trade_type, year, qty_tonnes, val_1k_usd, trade_id)

        # Execute the update
        execute_query(update_query, params)

        flash("Trade flow record updated successfully!", "success")
        return redirect(url_for('trade.trade_data_final_dashboard'))

    except Exception as e:
        flash(f"Error updating trade flow: {str(e)}", "error")
        return redirect(url_for('trade.trade_data_final_dashboard'))


@trade_bp.route("/trades/delete/<int:trade_id>", methods=["POST"])
@admin_required
def delete_trade_flow(trade_id):
    try:
        # Delete query
        delete_query = "DELETE FROM trade_data_final WHERE unique_id = %s"

        # Execute the delete
        execute_query(delete_query, (trade_id,))

        flash("Trade flow record deleted successfully!", "success")
        return redirect(url_for('trade.trade_data_final_dashboard'))

    except Exception as e:
        flash(f"Error deleting trade flow: {str(e)}", "error")
        return redirect(url_for('trade.trade_data_final_dashboard'))


@trade_bp.route("/trades/statistics")
def trade_statistics():
    """Trade Flows Statistics Dashboard with Charts"""

    try:
        # Query 1: Time Series Data (Exports vs Imports by Year)
        time_series_query = """
            SELECT
                tf.year,
                tf.trade_type,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value
            FROM trade_data_final tf
            WHERE tf.trade_type IN ('Export', 'Import') AND tf.year IS NOT NULL
            GROUP BY tf.year, tf.trade_type
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
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_trade_value
            FROM trade_data_final tf
            LEFT JOIN Countries c ON tf.reporter_code = c.country_id
            WHERE c.country_name IS NOT NULL
            GROUP BY c.country_id, c.country_name

            UNION ALL

            SELECT
                c.country_name,
                c.country_id,
                COUNT(DISTINCT tf.unique_id) AS trade_count,
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_trade_value
            FROM trade_data_final tf
            LEFT JOIN Countries c ON tf.partner_code = c.country_id
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
                COALESCE(SUM(CASE WHEN tf.trade_type = 'Export' THEN tf.val_1k_usd ELSE 0 END), 0) AS exports,
                COALESCE(SUM(CASE WHEN tf.trade_type = 'Import' THEN tf.val_1k_usd ELSE 0 END), 0) AS imports
            FROM trade_data_final tf
            LEFT JOIN Countries c ON tf.reporter_code = c.country_id
            WHERE c.country_name IS NOT NULL
            GROUP BY c.country_id, c.country_name
            ORDER BY ABS(COALESCE(SUM(CASE WHEN tf.trade_type = 'Export' THEN tf.val_1k_usd ELSE 0 END), 0) -
                         COALESCE(SUM(CASE WHEN tf.trade_type = 'Import' THEN tf.val_1k_usd ELSE 0 END), 0)) DESC
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
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value
            FROM trade_data_final tf
            LEFT JOIN Commodities c ON tf.item_code::integer = c.fao_code
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
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value
            FROM trade_data_final tf
            LEFT JOIN Countries c ON tf.reporter_code = c.country_id
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
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value,
                COALESCE(AVG(tf.val_1k_usd), 0) AS avg_value
            FROM trade_data_final tf
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
                COALESCE(SUM(val_1k_usd), 0) as total_value,
                COUNT(DISTINCT reporter_code) as reporter_countries_count,
                COUNT(DISTINCT partner_code) as partner_countries_count,
                MIN(year) as min_year,
                MAX(year) as max_year
            FROM trade_data_final
        """
        summary = fetch_query(summary_query)[0]

        total_trades = summary['total_trades']
        total_value = summary['total_value']
        total_countries = summary['reporter_countries_count'] + summary['partner_countries_count']
        year_range = f"{summary['min_year']}-{summary['max_year']}"

        # Get trade type breakdown
        trade_type_query = """
            SELECT
                trade_type,
                COUNT(*) as count,
                COALESCE(SUM(val_1k_usd), 0) as total_value,
                COALESCE(AVG(val_1k_usd), 0) as avg_value
            FROM trade_data_final
            WHERE trade_type IS NOT NULL
            GROUP BY trade_type
            ORDER BY total_value DESC
        """
        trade_type_data = fetch_query(trade_type_query)

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
                tf.reporter_code,
                tf.partner_code,
                rc.country_name AS reporter_name,
                rc.region AS reporter_region,
                pc.country_name AS partner_name,
                pc.region AS partner_region,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value,
                COALESCE(SUM(tf.qty_tonnes), 0) AS total_quantity,
                MODE() WITHIN GROUP (ORDER BY c.item_name) AS top_commodity,
                ROUND(
                    (COALESCE(SUM(tf.val_1k_usd), 0) /
                     NULLIF((SELECT SUM(val_1k_usd) FROM trade_data_final), 0) * 100),
                    2
                ) AS pct_of_global_trade,
                CASE
                    WHEN SUM(COALESCE(p.quantity, 0)) > 0 THEN 'Producer & Trader'
                    ELSE 'Trader Only'
                END AS trade_classification,
                COALESCE(SUM(p.quantity), 0) AS domestic_production
            FROM trade_data_final tf
            LEFT JOIN Countries rc ON tf.reporter_code = rc.country_id
            LEFT JOIN Countries pc ON tf.partner_code = pc.country_id
            LEFT JOIN Commodities c ON tf.item_code::integer = c.fao_code
            LEFT JOIN production p ON tf.reporter_code = p.country_code
                                    AND tf.item_code::integer = p.commodity_code
                                    AND tf.year = p.year
            WHERE tf.year >= 2015
            GROUP BY
                tf.reporter_code,
                tf.partner_code,
                rc.country_name,
                rc.region,
                pc.country_name,
                pc.region
            HAVING COUNT(*) > 0
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
                COALESCE(SUM(tf.val_1k_usd), 0) AS total_value,
                COUNT(DISTINCT tf.reporter_code) + COUNT(DISTINCT tf.partner_code) AS country_count,
                COALESCE(AVG(tf.val_1k_usd), 0) AS avg_value
            FROM trade_data_final tf
            LEFT JOIN Commodities c ON tf.item_code::integer = c.fao_code
            GROUP BY tf.item_code, c.item_name
            ORDER BY total_value DESC
            LIMIT 6
        """
        top_commodities_traded = fetch_query(top_commodities_query)

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
            year_range=year_range,
            trade_type_breakdown=trade_type_breakdown,
            top_partners=top_partners or [],
            top_commodities_traded=top_commodities_traded or []
        )

    except Exception as e:
        flash(f"Error loading statistics: {str(e)}", "error")
        return redirect(url_for('trade.trade_data_final_dashboard'))
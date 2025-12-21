from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import fetch_query, execute_query
from routes.auth_routes import login_required, admin_required

producer_price_bp = Blueprint("producer_price", __name__)

@producer_price_bp.route("/producer_prices")
@login_required
def producer_prices_dashboard():
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50
    
    # Get filter parameters
    country_filter = request.args.get('country', '')
    commodity_filter = request.args.get('commodity', '')
    
    # Multi-month selection (list of month numbers)
    selected_months = request.args.getlist('months')
    # Convert to integers, filter invalid values
    selected_months = [int(m) for m in selected_months if m.isdigit() and 1 <= int(m) <= 12]
    
    # Year range filters
    year_from = request.args.get('year_from', '', type=str)
    year_to = request.args.get('year_to', '', type=str)
    
    # Unit filter
    unit_filter = request.args.get('unit', '')

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
    
    # Fetch available years for dropdown
    years_query = """
        SELECT DISTINCT year FROM Producer_Prices ORDER BY year DESC
    """
    years_result = fetch_query(years_query)
    available_years = [r['year'] for r in years_result] if years_result else []
    
    # Fetch distinct units to check if we need unit filter
    units_query = """
        SELECT DISTINCT unit FROM Producer_Prices WHERE unit IS NOT NULL ORDER BY unit
    """
    units_result = fetch_query(units_query)
    available_units = [r['unit'] for r in units_result] if units_result else []
    # Only show unit filter if more than 1 distinct unit
    show_unit_filter = len(available_units) > 1

    # Build dynamic query with filters
    query = """
        SELECT 
            p.unique_id,
            c.country_id,
            c.country_name,
            cm.item_name,
            p.month,
            p.year,
            p.unit,
            p.value
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
    
    # Multi-month filter
    if selected_months:
        placeholders = ', '.join(['%s'] * len(selected_months))
        query += f" AND p.month IN ({placeholders})"
        params.extend(selected_months)
    
    # Year range filter
    if year_from:
        try:
            query += " AND p.year >= %s"
            params.append(int(year_from))
        except ValueError:
            pass
    
    if year_to:
        try:
            query += " AND p.year <= %s"
            params.append(int(year_to))
        except ValueError:
            pass
    
    # Unit filter
    if unit_filter:
        query += " AND p.unit = %s"
        params.append(unit_filter)
    
    query += " ORDER BY p.year DESC, c.country_name, cm.item_name, p.month LIMIT %s"
    params.append(limit)
    
    prices = fetch_query(query, tuple(params))

    # Statistics Query
    stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT country_id) as total_countries,
            COUNT(DISTINCT commodity_id) as total_commodities
        FROM Producer_Prices
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}
    
    # Month names for template
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

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
        current_limit=limit,
        # New filter data
        available_years=available_years,
        selected_months=selected_months,
        year_from=year_from,
        year_to=year_to,
        month_names=month_names,
        available_units=available_units,
        show_unit_filter=show_unit_filter,
        selected_unit=unit_filter
    )


# ==================== CRUD OPERATIONS ====================

@producer_price_bp.route("/producer-prices/new", methods=["GET"])
@admin_required
def add_producer_price_form():
    """Display form for adding new producer price record"""
    # Fetch countries for dropdown
    countries_query = """
        SELECT country_id, country_name
        FROM Countries
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    # Fetch commodities for dropdown
    commodities_query = """
        SELECT fao_code, item_name
        FROM Commodities
        ORDER BY item_name ASC;
    """
    commodities = fetch_query(commodities_query, ())

    # Years list
    years = list(range(2010, 2026))

    # Month names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    return render_template(
        "producer_price_add.html",
        countries=countries,
        commodities=commodities,
        years=years,
        month_names=month_names,
    )


@producer_price_bp.route("/producer-prices/add", methods=["POST"])
@admin_required
def add_producer_price():
    """Handle form submission for adding new producer price record"""
    country_id = request.form.get("country_id", type=int)
    commodity_id = request.form.get("commodity_id", type=int)
    year = request.form.get("year", type=int)
    month = request.form.get("month", type=int)
    unit = request.form.get("unit", "LCU")
    value = request.form.get("value", type=float)

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not commodity_id:
        errors.append("Commodity is required.")
    if not year:
        errors.append("Year is required.")
    if not month or month < 1 or month > 12:
        errors.append("Valid month (1-12) is required.")
    if value is None:
        errors.append("Value is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("producer_price.add_producer_price_form"))

    # Check if record already exists
    existing = fetch_query(
        """
        SELECT unique_id FROM Producer_Prices
        WHERE country_id = %s AND commodity_id = %s AND year = %s AND month = %s;
        """,
        (country_id, commodity_id, year, month),
    )

    if existing:
        flash("A record for this country, commodity, year, and month already exists.", "error")
        return redirect(url_for("producer_price.add_producer_price_form"))

    # Insert new record
    execute_query(
        """
        INSERT INTO Producer_Prices (country_id, commodity_id, year, month, unit, value)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (country_id, commodity_id, year, month, unit, value),
    )

    flash("Producer price record added successfully.", "success")
    return redirect(url_for("producer_price.add_producer_price_form"))


@producer_price_bp.route("/producer-prices/edit", methods=["GET"])
@admin_required
def edit_producer_price_form():
    """Display form for editing existing producer price record"""
    unique_id = request.args.get("id", type=int)

    if not unique_id:
        flash("Invalid record ID.", "error")
        return redirect(url_for("producer_price.producer_prices_dashboard"))

    # Fetch existing record
    record = fetch_query(
        """
        SELECT p.unique_id, p.country_id, p.commodity_id, p.year, p.month, p.unit, p.value,
               c.country_name, cm.item_name
        FROM Producer_Prices p
        JOIN Countries c ON p.country_id = c.country_id
        JOIN Commodities cm ON p.commodity_id = cm.fao_code
        WHERE p.unique_id = %s;
        """,
        (unique_id,),
    )

    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("producer_price.producer_prices_dashboard"))

    record = record[0]

    # Month names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    return render_template(
        "producer_price_edit.html",
        record=record,
        month_names=month_names,
    )


@producer_price_bp.route("/producer-prices/update", methods=["POST"])
@admin_required
def update_producer_price():
    """Handle form submission for updating producer price record"""
    unique_id = request.form.get("unique_id", type=int)
    unit = request.form.get("unit", "LCU")
    value = request.form.get("value", type=float)

    errors = []
    if not unique_id:
        errors.append("Record ID is required.")
    if value is None:
        errors.append("Value is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("producer_price.producer_prices_dashboard"))

    # Update record
    execute_query(
        """
        UPDATE Producer_Prices
        SET unit = %s, value = %s
        WHERE unique_id = %s;
        """,
        (unit, value, unique_id),
    )

    flash("Producer price record updated successfully.", "success")
    return redirect(url_for("producer_price.edit_producer_price_form", id=unique_id))


@producer_price_bp.route("/producer-prices/delete", methods=["POST"])
@admin_required
def delete_producer_price():
    """Handle delete request for producer price record"""
    unique_id = request.form.get("unique_id", type=int)

    if not unique_id:
        flash("Invalid record ID.", "error")
        return redirect(url_for("producer_price.producer_prices_dashboard"))

    # Delete record
    execute_query(
        """
        DELETE FROM Producer_Prices
        WHERE unique_id = %s;
        """,
        (unique_id,),
    )

    flash("Producer price record deleted successfully.", "success")
    return redirect(url_for("producer_price.producer_prices_dashboard"))
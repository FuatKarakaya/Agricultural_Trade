from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import fetch_query, execute_query
from routes.auth_routes import login_required, admin_required

consumer_price_bp = Blueprint("consumer_price", __name__)

@consumer_price_bp.route("/consumer_prices")
@login_required
def consumer_prices_dashboard():
    # Handle limit parameter
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50

    # Get filter parameters
    country_filter = request.args.get('country', '')
    type_filter = request.args.get('type', '')
    
    # Multi-month selection (list of month numbers)
    selected_months = request.args.getlist('months')
    selected_months = [int(m) for m in selected_months if m.isdigit() and 1 <= int(m) <= 12]
    
    # Year range filters
    year_from = request.args.get('year_from', '')
    year_to = request.args.get('year_to', '')

    # Fetch countries for dropdown
    countries_query = """
        SELECT DISTINCT c.country_id, c.country_name
        FROM countries c
        JOIN Consumer_Prices cp ON c.country_id = cp.country_id
        ORDER BY c.country_name
    """
    countries = fetch_query(countries_query)
    
    # Fetch available years for dropdown
    years_query = """
        SELECT DISTINCT year FROM Consumer_Prices ORDER BY year DESC
    """
    years_result = fetch_query(years_query)
    available_years = [r['year'] for r in years_result] if years_result else []
    
    # Type options (hardcoded since we know there are only 2)
    type_options = [
        {'value': 1, 'name': 'General Indices (2015=100)'},
        {'value': 2, 'name': 'Food Indices (2015=100)'}
    ]

    # Build dynamic query with filters
    query = """
        SELECT 
            cp.unique_id,
            c.country_name,
            c.country_id,
            cp.month,
            cp.type,
            CASE cp.type
                WHEN 1 THEN 'General Indices (2015=100)'
                WHEN 2 THEN 'Food Indices (2015=100)'
                ELSE 'Unknown'
            END as type_name,
            cp.year,
            cp.value
        FROM Consumer_Prices cp
        JOIN countries c ON cp.country_id = c.country_id
        WHERE 1=1
    """
    params = []
    
    if country_filter:
        query += " AND c.country_id = %s"
        params.append(country_filter)
    
    if type_filter:
        try:
            query += " AND cp.type = %s"
            params.append(int(type_filter))
        except ValueError:
            pass
    
    # Multi-month filter
    if selected_months:
        placeholders = ', '.join(['%s'] * len(selected_months))
        query += f" AND cp.month IN ({placeholders})"
        params.extend(selected_months)
    
    # Year range filter
    if year_from:
        try:
            query += " AND cp.year >= %s"
            params.append(int(year_from))
        except ValueError:
            pass
    
    if year_to:
        try:
            query += " AND cp.year <= %s"
            params.append(int(year_to))
        except ValueError:
            pass
    
    query += " ORDER BY cp.year DESC, c.country_name, cp.type, cp.month LIMIT %s"
    params.append(limit)
    
    prices = fetch_query(query, tuple(params))

    # Statistics Query
    stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT country_id) as total_countries
        FROM Consumer_Prices
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
        'consumer_prices.html',
        prices=prices,
        total_records=stats.get('total_records', 0),
        total_countries=stats.get('total_countries', 0),
        current_limit=limit,
        # Filter data
        countries=countries,
        selected_country=country_filter,
        type_options=type_options,
        selected_type=type_filter,
        available_years=available_years,
        selected_months=selected_months,
        year_from=year_from,
        year_to=year_to,
        month_names=month_names
    )


# ==================== CRUD OPERATIONS ====================

@consumer_price_bp.route("/consumer-prices/new", methods=["GET"])
@admin_required
def add_consumer_price_form():
    """Display form for adding new consumer price record"""
    # Fetch countries for dropdown
    countries_query = """
        SELECT country_id, country_name
        FROM Countries
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    # Years list
    years = list(range(2000, 2026))

    # Type options
    type_options = [
        {'value': 1, 'name': 'General Indices (2015=100)'},
        {'value': 2, 'name': 'Food Indices (2015=100)'}
    ]

    # Month names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    return render_template(
        "consumer_price_add.html",
        countries=countries,
        years=years,
        type_options=type_options,
        month_names=month_names,
    )


@consumer_price_bp.route("/consumer-prices/add", methods=["POST"])
@admin_required
def add_consumer_price():
    """Handle form submission for adding new consumer price record"""
    country_id = request.form.get("country_id", type=int)
    price_type = request.form.get("type", type=int)
    year = request.form.get("year", type=int)
    month = request.form.get("month", type=int)
    value = request.form.get("value", type=float)

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not price_type or price_type not in [1, 2]:
        errors.append("Valid type (General or Food) is required.")
    if not year:
        errors.append("Year is required.")
    if not month or month < 1 or month > 12:
        errors.append("Valid month (1-12) is required.")
    if value is None:
        errors.append("Value is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("consumer_price.add_consumer_price_form"))

    # Check if record already exists
    existing = fetch_query(
        """
        SELECT unique_id FROM Consumer_Prices
        WHERE country_id = %s AND type = %s AND year = %s AND month = %s;
        """,
        (country_id, price_type, year, month),
    )

    if existing:
        flash("A record for this country, type, year, and month already exists.", "error")
        return redirect(url_for("consumer_price.add_consumer_price_form"))

    # Insert new record
    execute_query(
        """
        INSERT INTO Consumer_Prices (country_id, type, year, month, value)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (country_id, price_type, year, month, value),
    )

    flash("Consumer price record added successfully.", "success")
    return redirect(url_for("consumer_price.add_consumer_price_form"))


@consumer_price_bp.route("/consumer-prices/edit", methods=["GET"])
@admin_required
def edit_consumer_price_form():
    """Display form for editing existing consumer price record"""
    unique_id = request.args.get("id", type=int)

    if not unique_id:
        flash("Invalid record ID.", "error")
        return redirect(url_for("consumer_price.consumer_prices_dashboard"))

    # Fetch existing record
    record = fetch_query(
        """
        SELECT cp.unique_id, cp.country_id, cp.type, cp.year, cp.month, cp.value,
               c.country_name,
               CASE cp.type
                   WHEN 1 THEN 'General Indices (2015=100)'
                   WHEN 2 THEN 'Food Indices (2015=100)'
                   ELSE 'Unknown'
               END as type_name
        FROM Consumer_Prices cp
        JOIN Countries c ON cp.country_id = c.country_id
        WHERE cp.unique_id = %s;
        """,
        (unique_id,),
    )

    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("consumer_price.consumer_prices_dashboard"))

    record = record[0]

    # Month names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    return render_template(
        "consumer_price_edit.html",
        record=record,
        month_names=month_names,
    )


@consumer_price_bp.route("/consumer-prices/update", methods=["POST"])
@admin_required
def update_consumer_price():
    """Handle form submission for updating consumer price record"""
    unique_id = request.form.get("unique_id", type=int)
    value = request.form.get("value", type=float)

    errors = []
    if not unique_id:
        errors.append("Record ID is required.")
    if value is None:
        errors.append("Value is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("consumer_price.consumer_prices_dashboard"))

    # Update record
    execute_query(
        """
        UPDATE Consumer_Prices
        SET value = %s
        WHERE unique_id = %s;
        """,
        (value, unique_id),
    )

    flash("Consumer price record updated successfully.", "success")
    return redirect(url_for("consumer_price.edit_consumer_price_form", id=unique_id))


@consumer_price_bp.route("/consumer-prices/delete", methods=["POST"])
@admin_required
def delete_consumer_price():
    """Handle delete request for consumer price record"""
    unique_id = request.form.get("unique_id", type=int)

    if not unique_id:
        flash("Invalid record ID.", "error")
        return redirect(url_for("consumer_price.consumer_prices_dashboard"))

    # Delete record
    execute_query(
        """
        DELETE FROM Consumer_Prices
        WHERE unique_id = %s;
        """,
        (unique_id,),
    )

    flash("Consumer price record deleted successfully.", "success")
    return redirect(url_for("consumer_price.consumer_prices_dashboard"))
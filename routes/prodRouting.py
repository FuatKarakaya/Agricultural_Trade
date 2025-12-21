from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import fetch_query, execute_query
from routes.auth_routes import admin_required

prod_bp = Blueprint("prod", __name__)


@prod_bp.route("/production")
def production():
    """Browse production records with filters"""
    try:
        country_code = request.args.get("country_code", "")
        commodity_code = request.args.get("commodity_code", "")
        year = request.args.get("year", "")
        unit = request.args.get("unit", "")
        search = request.args.get("search", "").strip()

        # Advanced query with 4 tables including LEFT OUTER JOIN and nested subquery
        query = """
            SELECT 
                p.production_ID AS production_id,
                p.year,
                p.unit,
                p.quantity,
                c.country_name,
                c.region,
                co.item_name,
                co.cpc_code,
                -- Element count from Production_Value (shows data completeness)
                COALESCE(pv_agg.element_count, 0) AS element_count,
                -- Calculated metric: Production density (per capita if population available)
                CASE 
                    WHEN c.population > 0 THEN p.quantity / c.population
                    ELSE 0 
                END AS production_per_capita
            FROM production p
            -- Join 1: Countries table for geographic metadata
            INNER JOIN Countries c ON p.country_code = c.country_id
            -- Join 2: Commodities table for item details
            INNER JOIN Commodities co ON p.commodity_code = co.fao_code
            -- Join 3 (LEFT OUTER): Nested subquery with GROUP BY for aggregating production values
            LEFT OUTER JOIN (
                SELECT 
                    production_ID,
                    SUM(value) AS total_value,
                    COUNT(DISTINCT element) AS element_count
                FROM Production_Value
                WHERE value IS NOT NULL
                GROUP BY production_ID
            ) AS pv_agg ON p.production_ID = pv_agg.production_ID
            WHERE 1=1
        """
        params = []

        if country_code:
            query += " AND p.country_code = %s"
            params.append(country_code)

        if commodity_code:
            query += " AND p.commodity_code = %s"
            params.append(commodity_code)

        if year:
            query += " AND p.year = %s"
            params.append(year)
        
        if unit:
            query += " AND p.unit = %s"
            params.append(unit)
        
        if search:
            query += """ AND (
                CAST(p.production_ID AS TEXT) LIKE %s 
                OR c.country_name ILIKE %s
                OR co.item_name ILIKE %s
                OR CAST(p.year AS TEXT) LIKE %s
                OR CAST(p.quantity AS TEXT) LIKE %s
                OR p.unit ILIKE %s
            )"""
            search_param = f"%{search}%"
            params.extend([search_param] * 6)

        # Order by year and quantity
        query += """ ORDER BY 
            CASE WHEN p.quantity IS NOT NULL AND p.unit IS NOT NULL 
                      AND c.country_name IS NOT NULL AND co.item_name IS NOT NULL 
                 THEN 0 ELSE 1 END,
            p.year DESC, p.quantity DESC NULLS LAST
            LIMIT 50"""

        production_list = fetch_query(query, params)


        if production_list is None:
            return (
                render_template(
                    "error.html",
                    error="Failed to load production data. "
                    "Check that the Production table exists and that the query is valid.",
                ),
                500,
            )

        # High-level stats for overview cards
        stats_result = fetch_query(
            """
            SELECT 
                COUNT(*) AS total_records,
                COUNT(DISTINCT country_code) AS total_countries,
                COUNT(DISTINCT commodity_code) AS total_commodities,
                MIN(year) AS min_year,
                MAX(year) AS max_year
            FROM production
            """
        )
        stats = stats_result[0] if stats_result else {}

        # Get filter options
        countries = fetch_query(
            "SELECT DISTINCT country_id, country_name FROM Countries ORDER BY country_name"
        )

        commodities = fetch_query(
            "SELECT DISTINCT fao_code, item_name FROM Commodities ORDER BY item_name"
        )

        years = fetch_query("SELECT DISTINCT year FROM production ORDER BY year DESC")
        
        units = fetch_query("SELECT DISTINCT unit FROM production WHERE unit IS NOT NULL ORDER BY unit")
        
        # Chart: Top 10 countries by number of distinct items produced
        chart_query = """
            SELECT c.country_name, COUNT(DISTINCT p.commodity_code) as item_count
            FROM production p
            INNER JOIN Countries c ON p.country_code = c.country_id
            GROUP BY c.country_name
            ORDER BY item_count DESC
            LIMIT 10
        """
        chart_result = fetch_query(chart_query)
        chart_data = []
        if chart_result:
            chart_data = [{"country": row["country_name"], "quantity": int(row["item_count"] or 0)} for row in chart_result]

        return render_template(
            "production.html",
            production=production_list,
            stats=stats,
            countries=countries,
            commodities=commodities,
            years=years,
            units=units,
            selected_country=country_code,
            selected_commodity=commodity_code,
            selected_year=year,
            selected_unit=unit,
            search=search,
            chart_data=chart_data,
            # Add pagination variables for template compatibility
            page=1,
            per_page=50,
            total_records=len(production_list) if production_list else 0,
            total_pages=1,
            # Add sorting variables
            sort_by="year",
            sort_order="desc",
        )
    except Exception as e:
        print(f"Error in production: {e}")
        # Return simple error response without template
        return f"<h1>Error</h1><p>{str(e)}</p>", 500


@prod_bp.route("/production/<int:production_id>")
def production_detail(production_id):
    """View production record details"""
    try:
        # Get production details
        production = fetch_query(
            """
            SELECT p.*, 
                   c.region,
                   c.population,
                   com.item_name,
                   com.cpc_code
            FROM production p
            JOIN Countries c ON p.country_code = c.country_id
            JOIN Commodities com ON p.commodity_code = com.fao_code
            WHERE p.production_ID = %s
            """,
            [production_id],
        )

        if not production:
            return (
                render_template("error.html", error="Production record not found"),
                404,
            )
        production = production[0]

        # Get production values for this record
        production_values = fetch_query(
            """
            SELECT *
            FROM production_Value
            WHERE production_ID = %s
            ORDER BY year DESC, element
            """,
            [production_id],
        )

        # Get historical production for same country/commodity
        historical_production = fetch_query(
            """
            SELECT year, quantity, unit
            FROM production
            WHERE country_code = %s 
                AND commodity_code = %s
                AND production_ID != %s
            ORDER BY year DESC
            LIMIT 10
            """,
            [production["country_code"], production["commodity_code"], production_id],
        )

        # Get comparative production (other countries, same commodity, same year)
        comparative_production = fetch_query(
            """
            SELECT p.country_code, p.quantity, c.region
            FROM production p
            JOIN Countries c ON p.country_code = c.country_id
            WHERE p.commodity_code = %s 
                AND p.year = %s
                AND p.production_ID != %s
                AND p.quantity > 0
            ORDER BY p.quantity DESC
            LIMIT 10
            """,
            [production["commodity_code"], production["year"], production_id],
        )

        return render_template(
            "production_detail.html",
            production=production,
            production_values=production_values,
            historical=historical_production,
            comparative=comparative_production,
        )
    except Exception as e:
        return render_template("error.html", error=str(e)), 500


@prod_bp.route("/production/new", methods=["GET"])
@admin_required
def add_production_form():
    """Display form to add new production record"""
    year = request.args.get("year", 2023, type=int)
    selected_country_id = request.args.get("country_id", type=int)
    selected_commodity_code = request.args.get("commodity_code", type=int)
    
    years = list(range(1990, 2026))
    
    countries = fetch_query(
        "SELECT DISTINCT country_id, country_name FROM Countries ORDER BY country_name"
    )
    
    commodities = fetch_query(
        "SELECT DISTINCT fao_code, item_name FROM Commodities ORDER BY item_name"
    )
    
    return render_template(
        "production_add.html",
        years=years,
        year=year,
        countries=countries,
        commodities=commodities,
        selected_country_id=selected_country_id,
        selected_commodity_code=selected_commodity_code,
    )


@prod_bp.route("/production/add", methods=["POST"])
@admin_required
def add_production():
    """Handle production record addition"""
    try:
        # Get form data
        country_code = request.form.get("country_code", type=int)
        commodity_code = request.form.get("commodity_code", type=int)
        year = request.form.get("year", type=int)
        unit = request.form.get("unit", "t")
        quantity = request.form.get("quantity", type=float)
        
        # Validation
        if not country_code or not commodity_code or not year:
            flash("Country, commodity, and year are required.", "error")
            return redirect(url_for("prod.production"))
        
        if quantity is None or quantity < 0:
            flash("Quantity must be a non-negative number.", "error")
            return redirect(url_for("prod.production"))
        
        # Verify commodity exists (no need to fetch item_name - it's in Commodities table)
        commodity_row = fetch_query(
            "SELECT fao_code FROM Commodities WHERE fao_code = %s",
            (commodity_code,)
        )
        if not commodity_row:
            flash("Selected commodity not found.", "error")
            return redirect(url_for("prod.production"))
        
        # Check for duplicate
        existing = fetch_query(
            """
            SELECT production_ID
            FROM Production
            WHERE country_code = %s AND commodity_code = %s AND year = %s
            """,
            (country_code, commodity_code, year)
        )
        
        if existing:
            flash("Record already exists for this country, commodity, and year.", "error")
            return redirect(url_for("prod.production"))
        
        # Insert new record
        insert_query = """
            INSERT INTO Production (country_code, commodity_code, year, unit, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (country_code, commodity_code, year, unit, quantity))
        
        flash("Production record added successfully!", "success")
        return redirect(url_for("prod.production"))
        
    except Exception as e:
        flash(f"Error adding production record: {str(e)}", "error")
        return redirect(url_for("prod.production"))


@prod_bp.route("/production/<int:production_id>/edit", methods=["GET"])
@admin_required
def edit_production_form(production_id):
    """Display form to edit existing production record"""
    try:
        # Get current production data
        production = fetch_query(
            """
            SELECT p.production_ID, p.country_code, p.commodity_code, p.year, p.unit, p.quantity,
                   c.country_name, co.item_name
            FROM Production p
            JOIN Countries c ON p.country_code = c.country_id
            JOIN Commodities co ON p.commodity_code = co.fao_code
            WHERE p.production_ID = %s
            """,
            [production_id]
        )
        
        if not production:
            flash("Production record not found.", "error")
            return redirect(url_for("prod.production"))
        
        production = production[0]
        
        return render_template(
            "production_edit.html",
            production=production
        )
        
    except Exception as e:
        flash(f"Error loading production record: {str(e)}", "error")
        return redirect(url_for("prod.production"))


@prod_bp.route("/production/<int:production_id>/edit", methods=["POST"])
@admin_required
def edit_production(production_id):
    """Handle production record update"""
    try:
        unit = request.form.get("unit", "t")
        quantity = request.form.get("quantity", type=float)
        
        if quantity is None or quantity < 0:
            flash("Quantity must be a non-negative number.", "error")
            return redirect(url_for("prod.edit_production_form", production_id=production_id))
        
        # Update the record (only unit and quantity can be edited)
        update_query = """
            UPDATE Production 
            SET unit = %s, quantity = %s
            WHERE production_ID = %s
        """
        execute_query(update_query, (unit, quantity, production_id))
        
        flash("Production record updated successfully!", "success")
        return redirect(url_for("prod.production"))
        
    except Exception as e:
        flash(f"Error updating production record: {str(e)}", "error")
        return redirect(url_for("prod.production"))


@prod_bp.route("/production/<int:production_id>/delete", methods=["POST"])
@admin_required
def delete_production(production_id):
    """Handle production record deletion (CASCADE deletes related Production_Value records)"""
    try:
        # Check if record exists
        existing = fetch_query(
            "SELECT production_ID FROM Production WHERE production_ID = %s",
            [production_id]
        )
        
        if not existing:
            flash("Production record not found.", "error")
            return redirect(url_for("prod.production"))
        
        # Delete the record (Production_Value records are CASCADE deleted)
        delete_query = "DELETE FROM Production WHERE production_ID = %s"
        execute_query(delete_query, [production_id])
        
        flash("Production record deleted successfully! Related production values were also removed.", "success")
        return redirect(url_for("prod.production"))
        
    except Exception as e:
        flash(f"Error deleting production record: {str(e)}", "error")
        return redirect(url_for("prod.production"))


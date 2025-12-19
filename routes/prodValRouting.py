from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import fetch_query, execute_query

prod_val_bp = Blueprint("prod_val", __name__)


@prod_val_bp.route("/production-values")
def production_values():
    """Browse production values with enhanced joins"""
    try:
        selected_element = request.args.get("element", "")
        selected_year = request.args.get("year", "")
        country_code = request.args.get("country_code", "")
        commodity_code = request.args.get("commodity_code", "")
        region = request.args.get("region", "")

        # Enhanced query with multiple JOINs similar to production page
        query = """
            SELECT 
                pv.production_value_ID AS production_value_id,
                pv.production_ID AS production_id,
                pv.element,
                pv.year,
                pv.unit,
                pv.value,
                p.country_code,
                p.commodity_code,
                p.unit AS production_unit,
                c.country_name,
                c.region,
                c.subregion,
                co.item_name,
                co.cpc_code
            FROM Production_Value pv
            INNER JOIN Production p ON pv.production_ID = p.production_ID
            INNER JOIN Countries c ON p.country_code = c.country_id
            INNER JOIN Commodities co ON p.commodity_code = co.fao_code
            WHERE 1=1
        """
        params = []

        if selected_element:
            query += " AND pv.element = %s"
            params.append(selected_element)

        if selected_year:
            query += " AND pv.year = %s"
            params.append(selected_year)

        if country_code:
            query += " AND p.country_code = %s"
            params.append(country_code)
        
        if commodity_code:
            query += " AND p.commodity_code = %s"
            params.append(commodity_code)
        
        if region:
            query += " AND c.region = %s"
            params.append(region)

        query += " ORDER BY pv.year DESC, pv.value DESC LIMIT 50"

        production_values_list = fetch_query(query, params)

        if production_values_list is None:
            return render_template("error.html", error="Database query failed."), 500

        # Enhanced stats with more information
        stats_result = fetch_query(
            """
            SELECT 
                COUNT(*) as total_records,
                SUM(pv.value) as total_value,
                COUNT(DISTINCT pv.element) as total_elements,
                COUNT(DISTINCT p.country_code) as total_countries,
                COUNT(DISTINCT p.commodity_code) as total_commodities,
                MIN(pv.year) as min_year,
                MAX(pv.year) as max_year
            FROM Production_Value pv
            INNER JOIN Production p ON pv.production_ID = p.production_ID
            """
        )
        stats = stats_result[0] if stats_result else {}

        # Get filter options
        elements = fetch_query(
            "SELECT DISTINCT element FROM Production_Value ORDER BY element"
        )
        years = fetch_query(
            "SELECT DISTINCT year FROM Production_Value ORDER BY year DESC"
        )
        countries = fetch_query(
            """
            SELECT DISTINCT c.country_id, c.country_name
            FROM Countries c
            INNER JOIN Production p ON c.country_id = p.country_code
            INNER JOIN Production_Value pv ON p.production_ID = pv.production_ID
            ORDER BY c.country_name
            """
        )
        
        # Get filter options
        commodities = fetch_query(
            "SELECT DISTINCT fao_code, item_name FROM Commodities ORDER BY item_name"
        )
        
        regions = fetch_query(
            "SELECT DISTINCT region FROM Countries WHERE region IS NOT NULL ORDER BY region"
        )

        return render_template(
            "production_values.html",
            production_values=production_values_list,
            stats=stats,
            elements=elements,
            years=years,
            countries=countries,
            commodities=commodities,
            regions=regions,
            selected_element=selected_element,
            selected_year=selected_year,
            selected_country=country_code,
            selected_commodity=commodity_code,
            selected_region=region,
            # Add pagination variables for template compatibility
            page=1,
            per_page=50,
            total_records=len(production_values_list) if production_values_list else 0,
            total_pages=1,
            # Add sorting variables
            sort_by="year",
            sort_order="desc",
            # Add search variable
            search="",
            # Add chart data
            chart_data=[]
        )

    except Exception as e:
        print(f"Error in production_values: {e}")
        # Return simple error response without template
        return f"<h1>Error</h1><p>{str(e)}</p>", 500


@prod_val_bp.route("/production-value/<int:production_value_id>")
def production_value_detail(production_value_id):
    """View details - RESTORED FEATURES (Simple Queries Only)"""
    try:
        query = "SELECT * FROM Production_Value WHERE production_value_ID = %s"
        result = fetch_query(query, [production_value_id])

        if not result:
            return (
                render_template("error.html", error="Production value not found"),
                404,
            )

        production_value = result[0]

        ts_query = """
            SELECT year, element, value, unit 
            FROM Production_Value 
            WHERE production_ID = %s 
            ORDER BY year DESC
        """
        time_series = fetch_query(ts_query, [production_value["production_ID"]])

        # Shows general stats for this element type across all years
        yt_query = """
            SELECT 
                year, 
                AVG(value) as avg_value, 
                MIN(value) as min_value, 
                MAX(value) as max_value, 
                COUNT(*) as record_count 
            FROM Production_Value 
            WHERE element = %s 
                AND value IS NOT NULL 
            GROUP BY year 
            ORDER BY year DESC 
            LIMIT 10
        """
        yearly_trends = fetch_query(yt_query, [production_value["element"]])

        element_comparison = []

        return render_template(
            "production_value_detail.html",
            production_value=production_value,
            time_series=time_series,
            element_comparison=element_comparison,
            yearly_trends=yearly_trends,
        )

    except Exception as e:
        print(f"Error in production_value_detail: {e}")
        return render_template("error.html", error=str(e)), 500


@prod_val_bp.route("/production-values/new", methods=["GET"])
def add_production_value_form():
    """Display form to add new production value record"""
    year = request.args.get("year", 2023, type=int)
    years = list(range(1990, 2026))
    
    productions = fetch_query(
        """
        SELECT p.production_ID, p.year, c.country_name, com.item_name
        FROM Production p
        JOIN Countries c ON p.country_code = c.country_id
        JOIN Commodities com ON p.commodity_code = com.fao_code
        ORDER BY p.year DESC, c.country_name, com.item_name
        LIMIT 1000
        """
    )
    
    # Get distinct elements with their units from existing records
    elements = fetch_query(
        """
        SELECT DISTINCT element, unit 
        FROM Production_Value 
        WHERE element IS NOT NULL 
        ORDER BY element
        """
    )
    
    # Get countries for dropdown (with region for filtering)
    countries = fetch_query(
        "SELECT DISTINCT country_id, country_name, region FROM Countries ORDER BY country_name"
    )
    
    # Get commodities for dropdown
    commodities = fetch_query(
        "SELECT DISTINCT fao_code, item_name FROM Commodities ORDER BY item_name"
    )
    
    # Get regions for dropdown
    regions = fetch_query(
        "SELECT DISTINCT region FROM Countries WHERE region IS NOT NULL ORDER BY region"
    )
    
    return render_template(
        "production_value_add.html",
        years=years,
        year=year,
        elements=elements,
        countries=countries,
        commodities=commodities,
        regions=regions,
    )


@prod_val_bp.route("/production-values/add", methods=["POST"])
def add_production_value():
    """Handle production value record addition"""
    try:
        # Get form data
        country_id = request.form.get("country", type=int)
        commodity_code = request.form.get("commodity", type=int)
        element = request.form.get("element", "").strip()
        year = request.form.get("year", type=int)
        value = request.form.get("value", type=float)
        
        # Validation
        if not country_id:
            flash("Country is required.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        if not commodity_code:
            flash("Commodity is required.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        if not element:
            flash("Element is required.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        if not year:
            flash("Year is required.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        if value is None:
            flash("Value is required.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        # Get unit from element
        unit_row = fetch_query(
            "SELECT unit FROM Production_Value WHERE element = %s LIMIT 1",
            (element,)
        )
        unit = unit_row[0]["unit"] if unit_row else ""
        
        # Look up production_id from country + commodity + year
        production_row = fetch_query(
            """
            SELECT production_ID 
            FROM Production 
            WHERE country_code = %s AND commodity_code = %s AND year = %s
            """,
            (country_id, commodity_code, year)
        )
        
        if not production_row:
            flash("No production record found for this country, commodity, and year combination. Please add the production record first.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        production_id = production_row[0]["production_id"]
        
        # Check for duplicate
        existing = fetch_query(
            """
            SELECT production_value_ID
            FROM Production_Value
            WHERE production_ID = %s AND element = %s AND year = %s
            """,
            (production_id, element, year)
        )
        
        if existing:
            flash("Record already exists for this production, element, and year.", "error")
            return redirect(url_for("prod_val.add_production_value_form"))
        
        # Insert new record
        insert_query = """
            INSERT INTO Production_Value (production_ID, element, year, unit, value)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (production_id, element, year, unit, value))
        
        flash("Production value record added successfully!", "success")
        return redirect(url_for("prod_val.add_production_value_form"))
        
    except Exception as e:
        flash(f"Error adding production value record: {str(e)}", "error")
        return redirect(url_for("prod_val.add_production_value_form"))

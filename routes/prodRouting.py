from flask import Blueprint, render_template, request
from database import fetch_query

prod_bp = Blueprint("prod", __name__)


@prod_bp.route("/production")
def production():
    """Browse production records with filters"""
    try:
        country_code = request.args.get("country_code", "")
        commodity_code = request.args.get("commodity_code", "")
        year = request.args.get("year", "")

        # Trying to use 4 tables here, will continue.
        query = """
            SELECT 
                p.production_ID AS production_id,
                p.year,
                p.unit,
                p.quantity,
                c.country_name,
                co.item_name,
                pv.value AS production_value
            FROM production p
            INNER JOIN Countries c ON p.country_code = c.country_id
            INNER JOIN Commodities co ON p.commodity_code = co.fao_code
            LEFT JOIN Production_Value pv ON pv.production_ID = p.production_ID
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

        query += " ORDER BY p.year DESC, p.quantity DESC LIMIT 50"

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

        return render_template(
            "production.html",
            production=production_list,
            stats=stats,
            countries=countries,
            commodities=commodities,
            years=years,
            selected_country=country_code,
            selected_commodity=commodity_code,
            selected_year=year,
            # Add pagination variables for template compatibility
            page=1,
            per_page=50,
            total_records=len(production_list) if production_list else 0,
            total_pages=1,
            # Add sorting variables
            sort_by="year",
            sort_order="desc",
            # Add search variable
            search=""
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
                   c.subregion,
                   c.population,
                   com.item_name,
                   com.item_group_name,
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

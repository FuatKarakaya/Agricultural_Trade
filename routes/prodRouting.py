from flask import Blueprint, render_template, request
from database import execute_query

prod_bp = Blueprint("prod", __name__)


@prod_bp.route("/production")
def production():
    """Browse production records with filters"""
    try:
        country_code = request.args.get("country_code", "")
        commodity_code = request.args.get("commodity_code", "")
        year = request.args.get("year", "")

        query = """
            SELECT p.*, 
                   c.region,
                   com.item_name,
                   com.item_group_name
            FROM Production p
            JOIN Countries c ON p.country_code = c.country_id
            JOIN Commodities com ON p.commodity_code = com.fao_code
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

        query += " ORDER BY p.year DESC, p.quantity DESC LIMIT 100"

        production_list = execute_query(query, params)

        # Get filter options
        countries = execute_query(
            "SELECT DISTINCT country_id FROM Countries ORDER BY country_id"
        )

        commodities = execute_query(
            "SELECT DISTINCT fao_code, item_name FROM Commodities ORDER BY item_name"
        )

        years = execute_query("SELECT DISTINCT year FROM Production ORDER BY year DESC")

        return render_template(
            "production.html",
            production=production_list,
            countries=countries,
            commodities=commodities,
            years=years,
            selected_country=country_code,
            selected_commodity=commodity_code,
            selected_year=year,
        )
    except Exception as e:
        return render_template("error.html", error=str(e)), 500


@prod_bp.route("/production/<int:production_id>")
def production_detail(production_id):
    """View production record details"""
    try:
        # Get production details
        production = execute_query(
            """
            SELECT p.*, 
                   c.region,
                   c.subregion,
                   c.population,
                   com.item_name,
                   com.item_group_name,
                   com.cpc_code
            FROM Production p
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
        production_values = execute_query(
            """
            SELECT *
            FROM Production_Value
            WHERE production_ID = %s
            ORDER BY year DESC, element
            """,
            [production_id],
        )

        # Get historical production for same country/commodity
        historical_production = execute_query(
            """
            SELECT year, quantity, unit
            FROM Production
            WHERE country_code = %s 
                AND commodity_code = %s
                AND production_ID != %s
            ORDER BY year DESC
            LIMIT 10
            """,
            [production["country_code"], production["commodity_code"], production_id],
        )

        # Get comparative production (other countries, same commodity, same year)
        comparative_production = execute_query(
            """
            SELECT p.country_code, p.quantity, c.region
            FROM Production p
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

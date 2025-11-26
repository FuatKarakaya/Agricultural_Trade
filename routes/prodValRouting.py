from flask import Blueprint, render_template, request
from database import fetch_query

prod_val_bp = Blueprint("prod_val", __name__)


@prod_val_bp.route("/production-values")
def production_values():
    """Browse production values with filters"""
    try:
        element = request.args.get("element", "")
        year = request.args.get("year", "")
        country_code = request.args.get("country_code", "")

        query = """
            SELECT pv.*, 
                   p.country_code,
                   p.commodity_code,
                   p.item_name,
                   c.region,
                   com.item_group_name
            FROM Production_Value pv
            LEFT JOIN Production p ON pv.production_ID = p.production_ID
            LEFT JOIN Countries c ON p.country_code = c.country_id
            LEFT JOIN Commodities com ON p.commodity_code = com.fao_code
            WHERE 1=1
        """
        params = []

        if element:
            query += " AND pv.element = %s"
            params.append(element)

        if year:
            query += " AND pv.year = %s"
            params.append(year)

        if country_code:
            query += " AND p.country_code = %s"
            params.append(country_code)

        query += " ORDER BY pv.year DESC, pv.value DESC LIMIT 100"

        production_values_list = fetch_query(query, params)
        if production_values_list is None:
            return (
                render_template(
                    "error.html",
                    error="Failed to load production value data. "
                    "Check that the Production_Value table exists and that the query is valid.",
                ),
                500,
            )

        # High-level stats for overview cards
        stats_result = fetch_query(
            """
            SELECT 
                COUNT(*) AS total_records,
                COUNT(DISTINCT element) AS total_elements,
                COUNT(DISTINCT year) AS total_years,
                MIN(year) AS min_year,
                MAX(year) AS max_year,
                SUM(value) AS total_value
            FROM Production_Value
            """
        )
        stats = stats_result[0] if stats_result else {}

        # Get filter options
        elements = fetch_query(
            "SELECT DISTINCT element FROM Production_Value WHERE element IS NOT NULL ORDER BY element"
        )

        years = fetch_query(
            "SELECT DISTINCT year FROM Production_Value ORDER BY year DESC"
        )

        countries = fetch_query(
            "SELECT DISTINCT country_id FROM Countries ORDER BY country_id"
        )

        return render_template(
            "production_values.html",
            production_values=production_values_list,
            stats=stats,
            elements=elements,
            years=years,
            countries=countries,
            selected_element=element,
            selected_year=year,
            selected_country=country_code,
        )
    except Exception as e:
        return render_template("error.html", error=str(e)), 500


@prod_val_bp.route("/production-value/<int:production_value_id>")
def production_value_detail(production_value_id):
    """View production value details"""
    try:
        # Get production value details
        production_value = fetch_query(
            """
            SELECT pv.*, 
                   p.country_code,
                   p.commodity_code,
                   p.item_name,
                   p.quantity as production_quantity,
                   p.unit as production_unit,
                   c.region,
                   c.subregion,
                   com.item_name as commodity_name,
                   com.item_group_name
            FROM Production_Value pv
            JOIN Production p ON pv.production_ID = p.production_ID
            JOIN Countries c ON p.country_code = c.country_id
            JOIN Commodities com ON p.commodity_code = com.fao_code
            WHERE pv.production_value_ID = %s
            """,
            [production_value_id],
        )

        if not production_value:
            return (
                render_template("error.html", error="Production value not found"),
                404,
            )
        production_value = production_value[0]

        # Get time series for same production record
        time_series = fetch_query(
            """
            SELECT year, element, value, unit
            FROM Production_Value
            WHERE production_ID = %s
            ORDER BY year DESC, element
            """,
            [production_value["production_id"]],
        )

        # Get element comparison across countries (same commodity, year, element)
        element_comparison = fetch_query(
            """
            SELECT pv.value, pv.unit, p.country_code, c.region
            FROM Production_Value pv
            JOIN Production p ON pv.production_ID = p.production_ID
            JOIN Countries c ON p.country_code = c.country_id
            WHERE p.commodity_code = %s
                AND pv.year = %s
                AND pv.element = %s
                AND pv.production_value_ID != %s
                AND pv.value IS NOT NULL
            ORDER BY pv.value DESC
            LIMIT 10
            """,
            [
                production_value["commodity_code"],
                production_value["year"],
                production_value["element"],
                production_value_id,
            ],
        )

        # Get yearly trends for same element
        yearly_trends = fetch_query(
            """
            SELECT 
                pv.year,
                AVG(pv.value) as avg_value,
                MIN(pv.value) as min_value,
                MAX(pv.value) as max_value,
                COUNT(*) as record_count
            FROM Production_Value pv
            WHERE pv.element = %s
                AND pv.value IS NOT NULL
            GROUP BY pv.year
            ORDER BY pv.year DESC
            LIMIT 10
            """,
            [production_value["element"]],
        )

        return render_template(
            "production_value_detail.html",
            production_value=production_value,
            time_series=time_series,
            element_comparison=element_comparison,
            yearly_trends=yearly_trends,
        )
    except Exception as e:
        return render_template("error.html", error=str(e)), 500

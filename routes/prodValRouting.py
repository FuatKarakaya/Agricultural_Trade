from flask import Blueprint, render_template, request
from database import fetch_query

prod_val_bp = Blueprint("prod_val", __name__)


@prod_val_bp.route("/production-values")
def production_values():
    """Browse production values - SAFE MODE (Single Table Queries)"""
    try:
        selected_element = request.args.get("element")
        selected_year = request.args.get("year")

        query = "SELECT * FROM Production_Value WHERE 1=1"
        params = []

        if selected_element:
            query += " AND element = %s"
            params.append(selected_element)

        if selected_year:
            query += " AND year = %s"
            params.append(selected_year)

        query += " ORDER BY year DESC, value DESC LIMIT 50"

        production_values_list = fetch_query(query, params)

        if production_values_list is None:
            return render_template("error.html", error="Database query failed."), 500

        stats_result = fetch_query(
            "SELECT COUNT(*) as total_records, SUM(value) as total_value FROM Production_Value"
        )
        stats = stats_result[0] if stats_result else {}

        elements = fetch_query(
            "SELECT DISTINCT element FROM Production_Value ORDER BY element"
        )
        years = fetch_query(
            "SELECT DISTINCT year FROM Production_Value ORDER BY year DESC"
        )

        # Countries require joining the Production table, so we leave this empty in Safe Mode
        countries = []

        return render_template(
            "production_values.html",
            production_values=production_values_list,
            stats=stats,
            elements=elements,
            years=years,
            countries=countries,
            selected_element=selected_element,
            selected_year=selected_year,
            selected_country="",
        )

    except Exception as e:
        print(f"Error in production_values: {e}")
        return render_template("error.html", error=str(e)), 500


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

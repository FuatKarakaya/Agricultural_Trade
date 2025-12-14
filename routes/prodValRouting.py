from flask import Blueprint, render_template, request
from database import fetch_query

prod_val_bp = Blueprint("prod_val", __name__)


@prod_val_bp.route("/production-values")
def production_values():
    """Browse production values with enhanced joins, pagination, sorting, and search"""
    try:
        # Get filter parameters
        selected_element = request.args.get("element", "")
        selected_year = request.args.get("year", "")
        country_code = request.args.get("country_code", "")
        
        # Get pagination parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
        
        # Get sorting parameters
        sort_by = request.args.get("sort_by", "year")
        sort_order = request.args.get("sort_order", "desc")
        
        # Get search parameter
        search = request.args.get("search", "").strip()

        # Valid sort columns
        valid_sort_columns = {
            "year": "pv.year",
            "value": "pv.value",
            "element": "pv.element",
            "country": "c.country_name",
            "commodity": "co.item_name"
        }
        
        sort_column = valid_sort_columns.get(sort_by, "pv.year")
        sort_direction = "ASC" if sort_order == "asc" else "DESC"

        # Enhanced query with multiple JOINs similar to production page
        query = """
            SELECT 
                pv.production_value_ID,
                pv.production_ID,
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
            
        # Add search filter
        if search:
            query += """ AND (
                c.country_name LIKE %s OR
                co.item_name LIKE %s OR
                pv.element LIKE %s OR
                CAST(pv.year AS CHAR) LIKE %s OR
                CAST(pv.value AS CHAR) LIKE %s
            )"""
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param, search_param])

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
        count_result = fetch_query(count_query, params)
        total_records = count_result[0]['total'] if count_result else 0
        
        # Calculate pagination
        total_pages = (total_records + per_page - 1) // per_page
        offset = (page - 1) * per_page

        # Add sorting and pagination
        query += f" ORDER BY {sort_column} {sort_direction}, pv.production_value_ID DESC"
        query += f" LIMIT {per_page} OFFSET {offset}"

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
        
        # Get chart data - Top 10 production values
        chart_data = fetch_query(
            """
            SELECT 
                c.country_name,
                co.item_name,
                pv.value,
                pv.year
            FROM Production_Value pv
            INNER JOIN Production p ON pv.production_ID = p.production_ID
            INNER JOIN Countries c ON p.country_code = c.country_id
            INNER JOIN Commodities co ON p.commodity_code = co.fao_code
            WHERE pv.value IS NOT NULL
            ORDER BY pv.value DESC
            LIMIT 10
            """
        )

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

        return render_template(
            "production_values.html",
            production_values=production_values_list,
            stats=stats,
            elements=elements,
            years=years,
            countries=countries,
            selected_element=selected_element,
            selected_year=selected_year,
            selected_country=country_code,
            # Pagination
            page=page,
            per_page=per_page,
            total_records=total_records,
            total_pages=total_pages,
            # Sorting
            sort_by=sort_by,
            sort_order=sort_order,
            # Search
            search=search,
            # Chart data
            chart_data=chart_data or []
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

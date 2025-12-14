from flask import Blueprint, render_template, request
from database import fetch_query

prod_bp = Blueprint("prod", __name__)


@prod_bp.route("/production")
def production():
    """Browse production records with filters, pagination, sorting, and search"""
    try:
        # Get filter parameters
        country_code = request.args.get("country_code", "")
        commodity_code = request.args.get("commodity_code", "")
        year = request.args.get("year", "")
        
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
            "year": "p.year",
            "quantity": "p.quantity",
            "country": "c.country_name",
            "item": "co.item_name",
            "value": "pv.value"
        }
        
        # Default to year if invalid sort column
        sort_column = valid_sort_columns.get(sort_by, "p.year")
        sort_direction = "ASC" if sort_order == "asc" else "DESC"

        # Build query
        query = """
            SELECT 
                p.production_ID,
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
            
        # Add search filter
        if search:
            query += """ AND (
                c.country_name LIKE %s OR
                co.item_name LIKE %s OR
                CAST(p.year AS CHAR) LIKE %s OR
                CAST(p.quantity AS CHAR) LIKE %s
            )"""
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
        count_result = fetch_query(count_query, params)
        total_records = count_result[0]['total'] if count_result else 0
        
        # Calculate pagination
        total_pages = (total_records + per_page - 1) // per_page
        offset = (page - 1) * per_page

        # Add sorting and pagination
        query += f" ORDER BY {sort_column} {sort_direction}, p.production_ID DESC"
        query += f" LIMIT {per_page} OFFSET {offset}"

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
            "SELECT DISTINCT country_id FROM Countries ORDER BY country_id"
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
            # Pagination
            page=page,
            per_page=per_page,
            total_records=total_records,
            total_pages=total_pages,
            # Sorting
            sort_by=sort_by,
            sort_order=sort_order,
            # Search
            search=search
        )
    except Exception as e:
        return render_template("error.html", error=str(e)), 500



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

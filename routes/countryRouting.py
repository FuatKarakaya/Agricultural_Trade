from flask import Blueprint, render_template, request, jsonify
from database import execute_query, fetch_query

country_bp = Blueprint("country", __name__)


@country_bp.route("/countries")
def countries_dashboard():
    
    # Get filter parameters from URL query string
    selected_region = request.args.get('region', '')
    sort_by = request.args.get('sort', 'name')

    query = "SELECT * FROM Countries"
    params = []
    
    # Apply region filter if selected
    if selected_region:
        query += " WHERE region = %s"  
        params.append(selected_region)
    
    # Apply sorting
    if sort_by == 'population':
        query += " ORDER BY population DESC"
    elif sort_by == 'land_area':
        query += " ORDER BY land_area_sq_km DESC"
    else:
        query += " ORDER BY country_name ASC"
    
    # Fetch countries - store the result!
    countries = fetch_query(query, tuple(params))
    
    
    
    # Calculate statistics
    stats_query = """
        SELECT 
            COUNT(*) as total_countries,
            SUM(population) as total_population,
            SUM(land_area_sq_km) as total_land_area,
            COUNT(DISTINCT region) as total_regions
        FROM Countries
    """
    stats_result = fetch_query(stats_query)
    stats = stats_result[0] if stats_result else {}
    
    
    return render_template(
        'countries.html',
        countries=countries or [],
        
        selected_region=selected_region,
        sort_by=sort_by,
        total_countries=stats.get('total_countries', 0),
        total_population=stats.get('total_population', 0),
        total_land_area=stats.get('total_land_area', 0),
        total_regions=stats.get('total_regions', 0)
    )


@country_bp.route("/countries/<int:country_id>")
def countries_detailed(country_id):
    # Fetch specific country by ID
    query = "SELECT * FROM Countries WHERE country_id = %s"
    result = fetch_query(query, (country_id,))
    
    if not result or len(result) == 0:
        return "Country not found", 404
    
    country = result[0]
    
    
    return render_template(
        'country_detail.html',
        country=country
    )



@country_bp.route("/countries/test")
def test_countries():
    """Simple endpoint to test database connection"""
    try:
        # Try to fetch all countries
        countries = fetch_query("SELECT * FROM Countries LIMIT 5")
        
        if countries:
            return jsonify({
                "status": "success",
                "message": "Database connection works!",
                "sample_data": countries,
                "count": len(countries)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No data returned from database"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
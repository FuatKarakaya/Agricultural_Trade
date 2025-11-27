from flask import Blueprint, render_template
from database import fetch_query

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    
    try:
        # Fetch summary statistics for the dashboard

        # Countries statistics
        country_stats = fetch_query("""
            SELECT
                COUNT(*) as total_countries,
                SUM(population) as total_population,
                SUM(land_area_sq_km) as total_land_area,
                COUNT(DISTINCT region) as total_regions
            FROM Countries
        """)

        # Production statistics
        production_stats = fetch_query("""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT country_code) as countries_with_production,
                COUNT(DISTINCT commodity_code) as total_commodities,
                MIN(year) as min_year,
                MAX(year) as max_year
            FROM Production
        """)

        # Trade statistics
        trade_stats = fetch_query("""
            SELECT COUNT(*) as total_trade_records
            FROM Trade_data_long
        """)

        # Producer prices count
        producer_price_stats = fetch_query("""
            SELECT COUNT(*) as total_producer_prices
            FROM Producer_prices
        """)

        # Consumer prices count
        consumer_price_stats = fetch_query("""
            SELECT COUNT(*) as total_consumer_prices
            FROM Consumer_prices
        """)

        # Land use count
        land_use_stats = fetch_query("""
            SELECT COUNT(*) as total_land_use
            FROM Land_use
        """)

        # Production value count
        production_value_stats = fetch_query("""
            SELECT COUNT(*) as total_production_values
            FROM Production_value
        """)

        # Combine all stats
        stats = {
            'country_stats': country_stats[0] if country_stats else {},
            'production_stats': production_stats[0] if production_stats else {},
            'trade_stats': trade_stats[0] if trade_stats else {},
            'producer_price_stats': producer_price_stats[0] if producer_price_stats else {},
            'consumer_price_stats': consumer_price_stats[0] if consumer_price_stats else {},
            'land_use_stats': land_use_stats[0] if land_use_stats else {},
            'production_value_stats': production_value_stats[0] if production_value_stats else {},
        }

        return render_template("dashboard.html", stats=stats)

    except Exception as e:
        print(f"Dashboard Error: {e}")
        return render_template("dashboard.html", stats=None, error=str(e))
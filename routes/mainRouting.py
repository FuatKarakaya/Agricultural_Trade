from flask import Blueprint, render_template
from database import fetch_query

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    """
    Serves the main dashboard page with summary statistics from the database.
    """
    try:
        # Fetch summary statistics for the dashboard cards
        country_count_result = fetch_query("SELECT COUNT(*) as count FROM Countries")
        production_count_result = fetch_query("SELECT COUNT(*) as count FROM Production")
        latest_year_result = fetch_query("SELECT MAX(year) as year FROM Production")

        stats = {
            "country_count": country_count_result[0]['count'] if country_count_result else 0,
            "production_record_count": production_count_result[0]['count'] if production_count_result else 0,
            "latest_year": latest_year_result[0]['year'] if latest_year_result else 'N/A'
        }

        return render_template("dashboard.html", stats=stats)
    except Exception as e:
        print(f"Dashboard Error: {e}")
        # Render the page without stats in case of a database error
        return render_template("dashboard.html", stats=None, error=str(e))
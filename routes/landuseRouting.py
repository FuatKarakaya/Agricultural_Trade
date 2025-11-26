from flask import Blueprint
from flask import Flask, render_template,request
from database import execute_query, fetch_query

landuse_bp = Blueprint("landuse", __name__)

@landuse_bp.route('/landuse')
def landUsePage():
    year = request.args.get("year", 2023, type=int)
    country_id = request.args.get("country_id", type=int)  # <-- yeni parametre

    # Dropdown için tüm yıllar (FAOSTAT standardı)
    years = list(range(1961, 2024))

    # Ülke dropdown’ı için liste
    countries_query = """
        SELECT DISTINCT country_id, country_name
        FROM land_use
        WHERE country_id IS NOT NULL
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    # Ana tablo sorgusu
    base_query = """
        SELECT
            country_name,
            country_id,
            year,
            unit,
            MAX(CASE WHEN land_type = 'Country area' THEN land_usage_value END) AS country_area,
            MAX(CASE WHEN land_type = 'Land area' THEN land_usage_value END) AS land_area,
            MAX(CASE WHEN land_type = 'Inland waters' THEN land_usage_value END) AS inland_waters,
            MAX(CASE WHEN land_type = 'Arable land' THEN land_usage_value END) AS arable_land,
            MAX(CASE WHEN land_type = 'Permanent crops' THEN land_usage_value END) AS permanent_crops,
            MAX(CASE WHEN land_type = 'Permanent meadows and pastures' THEN land_usage_value END)
                AS permanent_meadows_and_pastures,
            MAX(CASE WHEN land_type = 'Forest land' THEN land_usage_value END) AS forest_land,
            (
                MAX(CASE WHEN land_type = 'Land area' THEN land_usage_value END)
                -
                (
                    COALESCE(MAX(CASE WHEN land_type = 'Arable land' THEN land_usage_value END), 0) +
                    COALESCE(MAX(CASE WHEN land_type = 'Permanent crops' THEN land_usage_value END), 0) +
                    COALESCE(MAX(CASE WHEN land_type = 'Permanent meadows and pastures' THEN land_usage_value END), 0) +
                    COALESCE(MAX(CASE WHEN land_type = 'Forest land' THEN land_usage_value END), 0)
                )
            ) AS other_land
        FROM land_use
        WHERE year = %s
    """
    params = [year]

    if country_id is not None:
        base_query += " AND country_id = %s"
        params.append(country_id)

    base_query += """
        GROUP BY country_name, country_id, year, unit
        ORDER BY country_name ASC;
    """

    records = fetch_query(base_query, tuple(params))

    # İstatistikler
    stats_query = """
        SELECT 
            COUNT(DISTINCT country_name) AS total_countries,
            COUNT(*) AS total_rows
        FROM (
            SELECT country_name, country_id, year, unit
            FROM land_use
            WHERE year = %s
    """
    stats_params = [year]

    if country_id is not None:
        stats_query += " AND country_id = %s"
        stats_params.append(country_id)

    stats_query += """
            GROUP BY country_name, country_id, year, unit
        ) t;
    """

    stats_result = fetch_query(stats_query, tuple(stats_params))
    stats = stats_result[0] if stats_result else {}

    return render_template(
        "land_use.html",
        records=records or [],
        year=year,
        years=years,
        total_countries=stats.get("total_countries", 0),
        total_rows=stats.get("total_rows", 0),
        countries=countries,
        selected_country_id=country_id,
    )



@landuse_bp.route('/investments')
def investmentsPage():
    return
from flask import Blueprint
from flask import Flask, render_template,request,redirect,url_for,flash
from database import execute_query, fetch_query

landuse_bp = Blueprint("landuse", __name__)

@landuse_bp.route('/landuse')

def landUsePage():
    # Yıl: yoksa 2023
    year = request.args.get("year", 2023, type=int)

    # Ülke: yoksa None (yani "All Countries" modu)
    country_id = request.args.get("country_id", type=int)

    # Yıl dropdown'u
    years = list(range(1961, 2026))

    # Ülke dropdown'u: Countries tablosundan
    countries_query = """
        SELECT country_id, country_name
        FROM Countries
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    # --- ANA TABLO SORGUSU ---
    base_query = """
        SELECT
            t.country_name,
            t.country_id,
            t.year,
            t.unit,
            t.country_area,
            t.land_area,
            t.inland_waters,
            t.arable_land,
            t.permanent_crops,
            t.permanent_meadows_and_pastures,
            t.forest_land,
            (
                t.land_area
                - COALESCE(t.arable_land, 0)
                - COALESCE(t.permanent_crops, 0)
                - COALESCE(t.permanent_meadows_and_pastures, 0)
                - COALESCE(t.forest_land, 0)
            ) AS other_land
        FROM (
            SELECT
                lu.country_name,
                lu.country_id,
                lu.year,
                lu.unit,
                MAX(CASE WHEN lu.land_type = 'Country area' THEN lu.land_usage_value END) AS country_area,
                MAX(CASE WHEN lu.land_type = 'Land area' THEN lu.land_usage_value END) AS land_area,
                MAX(CASE WHEN lu.land_type = 'Inland waters' THEN lu.land_usage_value END) AS inland_waters,
                MAX(CASE WHEN lu.land_type = 'Arable land' THEN lu.land_usage_value END) AS arable_land,
                MAX(CASE WHEN lu.land_type = 'Permanent crops' THEN lu.land_usage_value END) AS permanent_crops,
                MAX(CASE WHEN lu.land_type = 'Permanent meadows and pastures' THEN lu.land_usage_value END)
                    AS permanent_meadows_and_pastures,
                MAX(CASE WHEN lu.land_type = 'Forest land' THEN lu.land_usage_value END) AS forest_land
            FROM Land_Use AS lu
            WHERE lu.year = %s
    """
    params = [year]

    # Ülke filtresi SEÇİLİRSE eklenir
    if country_id is not None:
        base_query += " AND lu.country_id = %s"
        params.append(country_id)

    base_query += """
            GROUP BY lu.country_name, lu.country_id, lu.year, lu.unit
        ) AS t
        ORDER BY t.country_name ASC;
    """

    records = fetch_query(base_query, tuple(params)) or []

    # İstatistikler
    total_rows = len(records)
    total_countries = len({row["country_id"] for row in records}) if records else 0

    # Tarımsal arazi oranı:
    # (arable + permanent crops + permanent meadows & pastures) / land_area
    total_agri_land = 0.0
    total_land_area = 0.0

    for row in records:
        land_area = row["land_area"] or 0
        agri = (row["arable_land"] or 0) \
             + (row["permanent_crops"] or 0) \
             + (row["permanent_meadows_and_pastures"] or 0)

        total_land_area += land_area
        total_agri_land += agri

    agri_share = (total_agri_land / total_land_area * 100) if total_land_area > 0 else None

    pie_query = """
        SELECT
            SUM(CASE WHEN lu.land_type = 'Arable land' THEN lu.land_usage_value ELSE 0 END) AS total_arable,
            SUM(CASE WHEN lu.land_type = 'Permanent crops' THEN lu.land_usage_value ELSE 0 END) AS total_permanent_crops,
            SUM(CASE WHEN lu.land_type = 'Permanent meadows and pastures' THEN lu.land_usage_value ELSE 0 END) AS total_meadows,
            SUM(CASE WHEN lu.land_type = 'Forest land' THEN lu.land_usage_value ELSE 0 END) AS total_forest,
            SUM(CASE WHEN lu.land_type = 'Inland waters' THEN lu.land_usage_value ELSE 0 END) AS total_inland_waters,
            SUM(CASE WHEN lu.land_type = 'Land area' THEN lu.land_usage_value ELSE 0 END) AS total_land_area
        FROM Land_Use AS lu
        WHERE lu.year = %s
    """
    
    pie_params = [year]
    
    if country_id is not None:
        pie_query += " AND lu.country_id = %s"
        pie_params.append(country_id)
    
    pie_data_row = fetch_query(pie_query, tuple(pie_params))
    
    if pie_data_row and pie_data_row[0]:
        pie_row = pie_data_row[0]
        total_land = pie_row['total_land_area'] or 0
        
        # Other land hesaplama
        other_land = total_land - (
            (pie_row['total_arable'] or 0) +
            (pie_row['total_permanent_crops'] or 0) +
            (pie_row['total_meadows'] or 0) +
            (pie_row['total_forest'] or 0)
        )
        
        pie_chart_data = {
            'arable_land': pie_row['total_arable'] or 0,
            'permanent_crops': pie_row['total_permanent_crops'] or 0,
            'meadows_pastures': pie_row['total_meadows'] or 0,
            'forest_land': pie_row['total_forest'] or 0,
            'other_land': other_land,
            'inland_waters': pie_row['total_inland_waters'] or 0
        }
    else:
        pie_chart_data = {
            'arable_land': 0,
            'permanent_crops': 0,
            'meadows_pastures': 0,
            'forest_land': 0,
            'other_land': 0,
            'inland_waters': 0
        }

    return render_template(
        "land_use.html",
        records=records,
        year=year,
        years=years,
        total_countries=total_countries,
        total_rows=total_rows,
        agri_share=agri_share,
        countries=countries,
        selected_country_id=country_id,
        pie_chart_data=pie_chart_data,
    )

@landuse_bp.route("/land-use/new", methods=["GET"])
def add_land_use_form():
    # Default yıl
    year = request.args.get("year", 2023, type=int)
    selected_country_id = request.args.get("country_id", type=int)

    # Yıl listesi
    years = list(range(1961, 2026))

    # Ülke dropdown'u için Countries tablosu
    countries_query = """
        SELECT country_id, country_name
        FROM Countries
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    return render_template(
        "land_use_add.html",
        years=years,
        year=year,
        countries=countries,
        selected_country_id=selected_country_id,
    )

@landuse_bp.route("/land-use/add", methods=["POST"])
def add_land_use():
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = "1000 ha"

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")

    def get_val(name):
        return request.form.get(name, type=float)

    values = {
        "Country area": get_val("country_area"),
        "Land area": get_val("land_area"),
        "Inland waters": get_val("inland_waters"),
        "Arable land": get_val("arable_land"),
        "Permanent crops": get_val("permanent_crops"),
        "Permanent meadows and pastures": get_val("permanent_meadows_and_pastures"),
        "Forest land": get_val("forest_land"),
    }

    for lt, v in values.items():
        if v is None:
            errors.append(f"{lt} value is required.")
        elif v < 0:
            errors.append(f"{lt} value must be >= 0.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year or 2023, country_id=country_id)
        )

    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year or 2023, country_id=country_id)
        )

    country_name = country_row[0]["country_name"]

    land_type_list = list(values.keys())
    placeholders = ", ".join(["%s"] * len(land_type_list))

    existing = fetch_query(
        f"""
        SELECT land_type
        FROM Land_Use
        WHERE country_id = %s
          AND year = %s
          AND land_type IN ({placeholders});
        """,
        (country_id, year, *land_type_list),
    )

    # ==== BURASI SADELEŞTİ ====
    if existing:
        flash("Already existing record.", "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year, country_id=country_id)
        )
    # ==========================

    params = []
    for lt, v in values.items():
        params.extend([country_name, lt, unit, v, year, country_id])

    values_sql = ", ".join(["(%s, %s, %s, %s, %s, %s)"] * len(values))

    execute_query(
        f"""
        INSERT INTO Land_Use (
            country_name,
            land_type,
            unit,
            land_usage_value,
            year,
            country_id
        )
        VALUES {values_sql};
        """,
        tuple(params),
    )

    flash("Land use records added successfully.", "success")

    return redirect(
        url_for("landuse.add_land_use_form", year=year, country_id=country_id)
    )

@landuse_bp.route("/land-use/delete", methods=["POST"])
def delete_land_use():
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    redirect_country_id = request.form.get("redirect_country_id", type=int)

    if not country_id or not year:
        flash("Error.", "error")
        return redirect(url_for("landuse.landUsePage", year=year or 2023))

    # İlgili ülke + yıl için tüm girdileri sil
    execute_query(
        """
        DELETE FROM Land_Use
        WHERE country_id = %s AND year = %s;
        """,
        (country_id, year),
    )

    flash("Deleted Successfully.", "success")

    # Aynı yıl ve önceki filtre ile sayfaya dön
    return redirect(
        url_for(
            "landuse.landUsePage",
            year=year,
            country_id=redirect_country_id,  # All countries ise boş gelir
        )
    )
@landuse_bp.route("/land-use/edit", methods=["GET"])
def edit_land_use_form():
    """
    Belirli bir (country_id, year) için var olan Land_Use kayıtlarını
    düzenlemek üzere form sayfası.
    """
    country_id = request.args.get("country_id", type=int)
    year = request.args.get("year", type=int)

    if not country_id or not year:
        flash("Geçersiz ülke veya yıl.", "error")
        return redirect(url_for("landuse.landUsePage", year=year or 2023))

    # Ülke adı
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Seçilen ülke Countries tablosunda bulunamadı.", "error")
        return redirect(url_for("landuse.landUsePage", year=year or 2023))

    country_name = country_row[0]["country_name"]

    # Bu ülke + yıl için mevcut Land_Use satırlarını çek
    land_type_list = [
        "Country area",
        "Land area",
        "Inland waters",
        "Arable land",
        "Permanent crops",
        "Permanent meadows and pastures",
        "Forest land",
    ]

    rows = fetch_query(
        """
        SELECT land_type, land_usage_value, unit
        FROM Land_Use
        WHERE country_id = %s AND year = %s;
        """,
        (country_id, year),
    ) or []

    # Varsayılan değerler: None
    land_values = {lt: None for lt in land_type_list}
    unit = "1000 ha"

    for r in rows:
        lt = r["land_type"]
        if lt in land_values:
            land_values[lt] = r["land_usage_value"]
            if r.get("unit"):
                unit = r["unit"]

    # Hiç kayıt yoksa edit'in anlamı yok
    if not rows:
        flash("Bu ülke ve yıl için düzenlenecek kayıt bulunamadı.", "error")
        return redirect(url_for("landuse.landUsePage", year=year))

    return render_template(
        "land_use_edit.html",
        country_id=country_id,
        country_name=country_name,
        year=year,
        unit=unit,
        land_values=land_values,
    )

@landuse_bp.route("/land-use/update", methods=["POST"])
def update_land_use():
    """
    Bir (country_id, year) için tüm land_type değerlerini tek formdan günceller.
    Gerekirse eksik tipler için yeni satır INSERT eder.
    """
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = "1000 ha"

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")

    def get_val(name):
        return request.form.get(name, type=float)

    values = {
        "Country area": get_val("country_area"),
        "Land area": get_val("land_area"),
        "Inland waters": get_val("inland_waters"),
        "Arable land": get_val("arable_land"),
        "Permanent crops": get_val("permanent_crops"),
        "Permanent meadows and pastures": get_val("permanent_meadows_and_pastures"),
        "Forest land": get_val("forest_land"),
    }

    for lt, v in values.items():
        if v is None:
            errors.append(f"{lt} value is required.")
        elif v < 0:
            errors.append(f"{lt} value must be >= 0.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("landuse.edit_land_use_form", country_id=country_id, year=year or 2023)
        )

    # Ülke adı doğrula
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("landuse.edit_land_use_form", country_id=country_id, year=year or 2023)
        )

    country_name = country_row[0]["country_name"]

    # Mevcut tipleri bul
    land_type_list = list(values.keys())
    placeholders = ", ".join(["%s"] * len(land_type_list))

    existing_rows = fetch_query(
        f"""
        SELECT land_type
        FROM Land_Use
        WHERE country_id = %s
          AND year = %s
          AND land_type IN ({placeholders});
        """,
        (country_id, year, *land_type_list),
    ) or []

    existing_types = {r["land_type"] for r in existing_rows}

    # Her tip için UPDATE veya gerekirse INSERT (upsert mantığı)
    for lt in land_type_list:
        v = values[lt]
        if lt in existing_types:
            execute_query(
                """
                UPDATE Land_Use
                SET land_usage_value = %s,
                    unit = %s,
                    country_name = %s
                WHERE country_id = %s
                  AND year = %s
                  AND land_type = %s;
                """,
                (v, unit, country_name, country_id, year, lt),
            )
        else:
            execute_query(
                """
                INSERT INTO Land_Use (
                    country_name,
                    land_type,
                    unit,
                    land_usage_value,
                    year,
                    country_id
                )
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (country_name, lt, unit, v, year, country_id),
            )

    flash("Records updated successfully.", "success")

    # Edit sayfasında kal, flash mesajı orada gör
    return redirect(
        url_for("landuse.edit_land_use_form", country_id=country_id, year=year)
    )


@landuse_bp.route('/investments')
def investmentsPage():
    return
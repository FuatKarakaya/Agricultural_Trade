from flask import Blueprint
from flask import Flask, render_template,request,redirect,url_for,flash
from database import execute_query, fetch_query
from routes.auth_routes import login_required, admin_required

landuse_bp = Blueprint("landuse", __name__)

@landuse_bp.route('/landuse')
@login_required
def landUsePage():
    # Yıl: yoksa 2023
    year = request.args.get("year", 2023, type=int)

    # Ülke: yoksa None (yani "All Countries" modu)
    country_id = request.args.get("country_id", type=int)
    
    # Sıralama parametreleri
    sort_by = request.args.get("sort", "country_name")  # varsayılan: country_name
    order = request.args.get("order", "asc")  # varsayılan: asc
    
    # Geçerli sıralama sütunları
    valid_sort_columns = [
        "country_name", "country_area", "land_area", "inland_waters",
        "arable_land", "permanent_crops", "permanent_meadows_and_pastures",
        "forest_land", "other_land"
    ]
    
    # Güvenlik kontrolü
    if sort_by not in valid_sort_columns:
        sort_by = "country_name"
    
    if order not in ["asc", "desc"]:
        order = "asc"

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
                c.country_name,
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
            INNER JOIN Countries AS c ON lu.country_id = c.country_id
            WHERE lu.year = %s
    """
    params = [year]

    # Ülke filtresi SEÇİLİRSE eklenir
    if country_id is not None:
        base_query += " AND lu.country_id = %s"
        params.append(country_id)

    base_query += """
            GROUP BY c.country_name, lu.country_id, lu.year, lu.unit
        ) AS t
    """
    
    # Dinamik ORDER BY ekleme
    # "other_land" hesaplanmış bir alan olduğu için özel işlem
    if sort_by == "other_land":
        # Hesaplanmış alanı doğrudan ORDER BY'da kullan
        base_query += f"""
        ORDER BY (
            t.land_area
            - COALESCE(t.arable_land, 0)
            - COALESCE(t.permanent_crops, 0)
            - COALESCE(t.permanent_meadows_and_pastures, 0)
            - COALESCE(t.forest_land, 0)
        ) {order.upper()} NULLS LAST;
        """
    else:
        # Diğer sütunlar için normal sıralama
        base_query += f" ORDER BY t.{sort_by} {order.upper()} NULLS LAST;"

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
        sort_by=sort_by,
        order=order,
    )

@landuse_bp.route("/land-use/new", methods=["GET"])
@admin_required
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
    
    # Unit seçenekleri
    unit_options = ["1000 ha", "km^2"]

    return render_template(
        "land_use_add.html",
        years=years,
        year=year,
        countries=countries,
        selected_country_id=selected_country_id,
        unit_options=unit_options,
    )

@landuse_bp.route("/land-use/add", methods=["POST"])
@admin_required
def add_land_use():
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = request.form.get("unit", "1000 ha")  # Form'dan al, varsayılan "1000 ha"

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")
    if unit not in ["1000 ha", "km^2"]:
        errors.append("Invalid unit selected.")

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

    # --- VALIDATION RULES ---
    country_area = values["Country area"]
    land_area = values["Land area"]
    inland_waters = values["Inland waters"]
    arable_land = values["Arable land"]
    permanent_crops = values["Permanent crops"]
    meadows_pastures = values["Permanent meadows and pastures"]
    forest_land = values["Forest land"]

    # Rule 1: Country area = Land area + Inland waters
    expected_country_area = land_area + inland_waters
    tolerance = 0.01  # Küçük yuvarlama hataları için tolerans
    
    if abs(country_area - expected_country_area) > tolerance:
        errors.append(
            f"Country area ({country_area}) must equal Land area ({land_area}) + "
            f"Inland waters ({inland_waters}) = {expected_country_area}"
        )

    # Rule 2: Agricultural land types + Forest land <= Land area
    agricultural_and_forest_total = (
        arable_land + 
        permanent_crops + 
        meadows_pastures + 
        forest_land
    )
    
    if agricultural_and_forest_total > land_area + tolerance:
        errors.append(
            f"Sum of Arable land ({arable_land}) + Permanent crops ({permanent_crops}) + "
            f"Meadows & pastures ({meadows_pastures}) + Forest land ({forest_land}) = "
            f"{agricultural_and_forest_total} cannot exceed Land area ({land_area})"
        )

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year or 2023, country_id=country_id)
        )

    # Ülke kontrolü
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year or 2023, country_id=country_id)
        )

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

    if existing:
        flash("Already existing record.", "error")
        return redirect(
            url_for("landuse.add_land_use_form", year=year, country_id=country_id)
        )

    # INSERT
    params = []
    for lt, v in values.items():
        params.extend([lt, unit, v, year, country_id])

    values_sql = ", ".join(["(%s, %s, %s, %s, %s)"] * len(values))

    execute_query(
        f"""
        INSERT INTO Land_Use (
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
@admin_required
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
            country_id=redirect_country_id,
        )
    )

@landuse_bp.route("/land-use/edit", methods=["GET"])
@admin_required
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
    unit = "1000 ha"  # Varsayılan unit

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
    
    # Unit seçenekleri
    unit_options = ["1000 ha", "km^2"]

    return render_template(
        "land_use_edit.html",
        country_id=country_id,
        country_name=country_name,
        year=year,
        unit=unit,
        land_values=land_values,
        unit_options=unit_options,
    )

@landuse_bp.route("/land-use/update", methods=["POST"])
@admin_required
def update_land_use():
    """
    Bir (country_id, year) için tüm land_type değerlerini tek formdan günceller.
    Gerekirse eksik tipler için yeni satır INSERT eder.
    """
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = request.form.get("unit", "1000 ha")  # Form'dan al

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")
    if unit not in ["1000 ha", "km^2"]:
        errors.append("Invalid unit selected.")

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

    # --- VALIDATION RULES ---
    country_area = values["Country area"]
    land_area = values["Land area"]
    inland_waters = values["Inland waters"]
    arable_land = values["Arable land"]
    permanent_crops = values["Permanent crops"]
    meadows_pastures = values["Permanent meadows and pastures"]
    forest_land = values["Forest land"]

    # Rule 1: Country area = Land area + Inland waters
    expected_country_area = land_area + inland_waters
    tolerance = 0.01  # Küçük yuvarlama hataları için tolerans
    
    if abs(country_area - expected_country_area) > tolerance:
        errors.append(
            f"Country area ({country_area}) must equal Land area ({land_area}) + "
            f"Inland waters ({inland_waters}) = {expected_country_area}"
        )

    # Rule 2: Agricultural land types + Forest land <= Land area
    agricultural_and_forest_total = (
        arable_land + 
        permanent_crops + 
        meadows_pastures + 
        forest_land
    )
    
    if agricultural_and_forest_total > land_area + tolerance:
        errors.append(
            f"Sum of Arable land ({arable_land}) + Permanent crops ({permanent_crops}) + "
            f"Meadows & pastures ({meadows_pastures}) + Forest land ({forest_land}) = "
            f"{agricultural_and_forest_total} cannot exceed Land area ({land_area})"
        )

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("landuse.edit_land_use_form", country_id=country_id, year=year or 2023)
        )

    # Ülke doğrula
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("landuse.edit_land_use_form", country_id=country_id, year=year or 2023)
        )

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
            # UPDATE
            execute_query(
                """
                UPDATE Land_Use
                SET land_usage_value = %s,
                    unit = %s
                WHERE country_id = %s
                  AND year = %s
                  AND land_type = %s;
                """,
                (v, unit, country_id, year, lt),
            )
        else:
            # INSERT
            execute_query(
                """
                INSERT INTO Land_Use (
                    land_type,
                    unit,
                    land_usage_value,
                    year,
                    country_id
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (lt, unit, v, year, country_id),
            )

    flash("Records updated successfully.", "success")

    # Edit sayfasında kal, flash mesajı orada gör
    return redirect(
        url_for("landuse.edit_land_use_form", country_id=country_id, year=year)
    )

@landuse_bp.route('/landuse/country-timeline')
@login_required
def country_timeline():
    """
    Belirli bir ülkenin 1961-2025 arası tüm land use verilerini gösterir.
    """
    country_id = request.args.get("country_id", type=int)
    
    # Sıralama parametreleri
    sort_by = request.args.get("sort", "year")  # varsayılan: year
    order = request.args.get("order", "desc")  # varsayılan: desc (en yeni üstte)
    
    # Geçerli sıralama sütunları
    valid_sort_columns = [
        "year", "country_area", "land_area", "inland_waters",
        "arable_land", "permanent_crops", "permanent_meadows_and_pastures",
        "forest_land", "other_land"
    ]
    
    # Güvenlik kontrolü
    if sort_by not in valid_sort_columns:
        sort_by = "year"
    
    if order not in ["asc", "desc"]:
        order = "desc"

    # Ülke dropdown'u için Countries tablosu
    countries_query = """
        SELECT country_id, country_name
        FROM Countries
        ORDER BY country_name ASC;
    """
    countries = fetch_query(countries_query, ())

    # Eğer ülke seçilmemişse sadece form göster
    if not country_id:
        return render_template(
            "land_use_timeline.html",
            countries=countries,
            selected_country_id=None,
            country_name=None,
            records=[],
            sort_by=sort_by,
            order=order,
        )

    # Seçilen ülkenin adını al
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    
    if not country_row:
        flash("Selected country not found.", "error")
        return redirect(url_for("landuse.country_timeline"))
    
    country_name = country_row[0]["country_name"]

    # Seçilen ülkenin TÜM yıllar için land use verilerini çek
    base_query = """
        SELECT
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
            WHERE lu.country_id = %s
            GROUP BY lu.year, lu.unit
        ) AS t
    """
    
    # Dinamik ORDER BY ekleme
    if sort_by == "other_land":
        base_query += f"""
        ORDER BY (
            t.land_area
            - COALESCE(t.arable_land, 0)
            - COALESCE(t.permanent_crops, 0)
            - COALESCE(t.permanent_meadows_and_pastures, 0)
            - COALESCE(t.forest_land, 0)
        ) {order.upper()} NULLS LAST;
        """
    else:
        base_query += f" ORDER BY t.{sort_by} {order.upper()} NULLS LAST;"

    records = fetch_query(base_query, (country_id,)) or []

    # İstatistikler
    total_years = len(records)
    
    # Grafik için veri hazırla (sadece 1990 ve sonrası)
    chart_data = {
        'years': [],
        'arable_land': [],
        'permanent_crops': [],
        'meadows_pastures': [],
        'forest_land': [],
        'other_land': [],
    }
    
    # Grafik için kayıtları yıla göre sırala ve 1990+ filtrele
    sorted_records = sorted(records, key=lambda x: x['year'])
    filtered_records = [r for r in sorted_records if r['year'] >= 1990]
    
    for row in filtered_records:
        chart_data['years'].append(row['year'])
        chart_data['arable_land'].append(row['arable_land'] or 0)
        chart_data['permanent_crops'].append(row['permanent_crops'] or 0)
        chart_data['meadows_pastures'].append(row['permanent_meadows_and_pastures'] or 0)
        chart_data['forest_land'].append(row['forest_land'] or 0)
        chart_data['other_land'].append(row['other_land'] if row['other_land'] is not None else 0)

    return render_template(
        "land_use_timeline.html",
        countries=countries,
        selected_country_id=country_id,
        country_name=country_name,
        records=records,
        total_years=total_years,
        sort_by=sort_by,
        order=order,
        chart_data=chart_data,
    )

@landuse_bp.route('/landuse/land-efficiency-analysis')
@login_required
def land_efficiency_analysis():
    """
    Land Use Efficiency Analysis: Sadece Land Use, Production, Commodities, Countries
    Investments verisi olmadan güvenilir land use analizi
    """
    year = request.args.get("year", 2023, type=int)
    
    # Sıralama parametreleri
    sort_by = request.args.get("sort", "country_name")
    order = request.args.get("order", "asc")
    
    valid_sort_columns = [
        "country_name", "region", "agricultural_land_total", "forest_land",
        "land_productivity_index", "production_density", "crop_diversity_score"
    ]
    
    if sort_by not in valid_sort_columns:
        sort_by = "country_name"
    
    if order not in ["asc", "desc"]:
        order = "asc"
    
    # LAND USE FOCUSED QUERY: 4 tables (NO Investments)
    land_efficiency_query = f"""
        WITH LandTypeBreakdown AS (
            -- Nested Query 1: Her ülkenin detaylı land type dağılımı
            SELECT
                lu.country_id,
                lu.year,
                MAX(CASE WHEN lu.land_type = 'Country area' THEN lu.land_usage_value END) AS country_area,
                MAX(CASE WHEN lu.land_type = 'Land area' THEN lu.land_usage_value END) AS land_area,
                MAX(CASE WHEN lu.land_type = 'Inland waters' THEN lu.land_usage_value END) AS inland_waters,
                MAX(CASE WHEN lu.land_type = 'Arable land' THEN lu.land_usage_value END) AS arable_land,
                MAX(CASE WHEN lu.land_type = 'Permanent crops' THEN lu.land_usage_value END) AS permanent_crops,
                MAX(CASE WHEN lu.land_type = 'Permanent meadows and pastures' THEN lu.land_usage_value END) AS meadows_pastures,
                MAX(CASE WHEN lu.land_type = 'Forest land' THEN lu.land_usage_value END) AS forest_land,
                -- Agricultural land toplamı
                COALESCE(MAX(CASE WHEN lu.land_type = 'Arable land' THEN lu.land_usage_value END), 0) +
                COALESCE(MAX(CASE WHEN lu.land_type = 'Permanent crops' THEN lu.land_usage_value END), 0) +
                COALESCE(MAX(CASE WHEN lu.land_type = 'Permanent meadows and pastures' THEN lu.land_usage_value END), 0) 
                    AS agricultural_land_total,
                -- Other land hesaplama
                COALESCE(MAX(CASE WHEN lu.land_type = 'Land area' THEN lu.land_usage_value END), 0) -
                COALESCE(MAX(CASE WHEN lu.land_type = 'Arable land' THEN lu.land_usage_value END), 0) -
                COALESCE(MAX(CASE WHEN lu.land_type = 'Permanent crops' THEN lu.land_usage_value END), 0) -
                COALESCE(MAX(CASE WHEN lu.land_type = 'Permanent meadows and pastures' THEN lu.land_usage_value END), 0) -
                COALESCE(MAX(CASE WHEN lu.land_type = 'Forest land' THEN lu.land_usage_value END), 0)
                    AS other_land
            FROM Land_Use lu
            WHERE lu.year = %s
            GROUP BY lu.country_id, lu.year
        ),
        AgriculturalProduction AS (
            -- Nested Query 2: Tarımsal üretim detayları
            SELECT
                p.country_code AS country_id,
                p.year,
                SUM(p.quantity) AS total_agricultural_production,
                COUNT(DISTINCT p.commodity_code) AS crop_diversity,
                AVG(p.quantity) AS avg_crop_yield,
                MAX(p.quantity) AS max_single_crop_production,
                MIN(p.quantity) AS min_crop_production
            FROM Production p
            WHERE p.year = %s
                AND p.quantity IS NOT NULL
                AND p.quantity > 0
            GROUP BY p.country_code, p.year
        ),
        TopCommodityPerCountry AS (
            -- Nested Query 3: Her ülkenin en çok ürettiği ürün
            SELECT DISTINCT ON (p.country_code)
                p.country_code AS country_id,
                p.year,
                c.item_name AS top_commodity,
                p.quantity AS top_commodity_quantity,
                c.cpc_code
            FROM Production p
            INNER JOIN Commodities c ON p.commodity_code = c.fao_code
            WHERE p.year = %s
                AND p.quantity IS NOT NULL
                AND p.quantity > 0
            ORDER BY p.country_code, p.quantity DESC
        ),
        RegionalLandStats AS (
            -- Nested Query 4: Bölgesel land use ortalamaları
            SELECT
                c.region,
                AVG(lt.agricultural_land_total) AS region_avg_agri_land,
                AVG(lt.forest_land) AS region_avg_forest,
                AVG(lt.land_area) AS region_avg_land_area,
                COUNT(DISTINCT lt.country_id) AS countries_in_region
            FROM Countries c
            LEFT JOIN LandTypeBreakdown lt ON c.country_id = lt.country_id
            WHERE c.region IS NOT NULL
                AND lt.agricultural_land_total >= 10  -- Bölgesel ortalama için de filtre
            GROUP BY c.region
        )
        -- MAIN QUERY: 4 main tables joined
        SELECT
            c.country_id,
            c.country_name,
            c.region,
            c.population,
            
            -- LAND USE DATA (CORE)
            COALESCE(lt.country_area, 0) AS country_area,
            COALESCE(lt.land_area, 0) AS land_area,
            COALESCE(lt.inland_waters, 0) AS inland_waters,
            COALESCE(lt.arable_land, 0) AS arable_land,
            COALESCE(lt.permanent_crops, 0) AS permanent_crops,
            COALESCE(lt.meadows_pastures, 0) AS meadows_pastures,
            COALESCE(lt.forest_land, 0) AS forest_land,
            COALESCE(lt.other_land, 0) AS other_land,
            COALESCE(lt.agricultural_land_total, 0) AS agricultural_land_total,
            
            -- PRODUCTION DATA
            COALESCE(ap.total_agricultural_production, 0) AS total_agricultural_production,
            COALESCE(ap.crop_diversity, 0) AS crop_diversity,
            COALESCE(ap.avg_crop_yield, 0) AS avg_crop_yield,
            COALESCE(ap.max_single_crop_production, 0) AS max_single_crop_production,
            
            -- TOP COMMODITY
            COALESCE(tcp.top_commodity, 'N/A') AS top_commodity,
            COALESCE(tcp.top_commodity_quantity, 0) AS top_commodity_quantity,
            
            -- REGIONAL COMPARISON
            COALESCE(rls.region_avg_agri_land, 0) AS region_avg_agri_land,
            COALESCE(rls.region_avg_forest, 0) AS region_avg_forest,
            COALESCE(rls.countries_in_region, 0) AS countries_in_region,
            
            -- LAND USE PERCENTAGES
            CASE 
                WHEN lt.land_area > 0 
                THEN (lt.agricultural_land_total / lt.land_area * 100)
                ELSE 0
            END AS agricultural_land_percentage,
            
            CASE 
                WHEN lt.land_area > 0 
                THEN (lt.forest_land / lt.land_area * 100)
                ELSE 0
            END AS forest_land_percentage,
            
            CASE 
                WHEN lt.land_area > 0 
                THEN (lt.arable_land / lt.land_area * 100)
                ELSE 0
            END AS arable_land_percentage,
            
            CASE 
                WHEN lt.agricultural_land_total > 0 
                THEN (lt.arable_land / lt.agricultural_land_total * 100)
                ELSE 0
            END AS arable_of_agricultural,
            
            CASE 
                WHEN lt.agricultural_land_total > 0 
                THEN (lt.permanent_crops / lt.agricultural_land_total * 100)
                ELSE 0
            END AS crops_of_agricultural,
            
            -- PRODUCTION EFFICIENCY METRICS
            CASE 
                WHEN lt.agricultural_land_total > 0 AND ap.total_agricultural_production > 0
                THEN (ap.total_agricultural_production / lt.agricultural_land_total)
                ELSE 0
            END AS production_density,
            
            CASE 
                WHEN lt.arable_land > 0 AND ap.total_agricultural_production > 0
                THEN (ap.total_agricultural_production / lt.arable_land)
                ELSE 0
            END AS production_per_arable_land,
            
            -- CROP DIVERSITY SCORE (diversity * production density)
            CASE 
                WHEN lt.agricultural_land_total > 0 AND ap.crop_diversity > 0
                THEN (ap.crop_diversity * LN((ap.total_agricultural_production / lt.agricultural_land_total) + 1))
                ELSE 0
            END AS crop_diversity_score,
            
            -- LAND PRODUCTIVITY INDEX (without investment data)
            CASE 
                WHEN lt.agricultural_land_total > 0 AND ap.total_agricultural_production > 0
                THEN (
                    (ap.total_agricultural_production / lt.agricultural_land_total) * 0.75 +
                    (ap.crop_diversity * 100) * 0.25
                )
                ELSE 0
            END AS land_productivity_index,
            
            -- PER CAPITA METRICS
            CASE
                WHEN c.population > 0
                THEN (lt.agricultural_land_total * 1000 / c.population)
                ELSE 0
            END AS agricultural_land_per_capita,
            
            CASE
                WHEN c.population > 0
                THEN (lt.arable_land * 1000 / c.population)
                ELSE 0
            END AS arable_land_per_capita,
            
            CASE
                WHEN c.population > 0
                THEN (lt.forest_land * 1000 / c.population)
                ELSE 0
            END AS forest_land_per_capita,
            
            CASE
                WHEN c.population > 0 AND ap.total_agricultural_production > 0
                THEN (ap.total_agricultural_production / c.population)
                ELSE 0
            END AS production_per_capita,
            
            -- REGIONAL PERFORMANCE (vs regional average)
            CASE
                WHEN rls.region_avg_agri_land > 0
                THEN (lt.agricultural_land_total / rls.region_avg_agri_land * 100)
                ELSE 0
            END AS agri_land_vs_region_avg,
            
            CASE
                WHEN rls.region_avg_forest > 0
                THEN (lt.forest_land / rls.region_avg_forest * 100)
                ELSE 0
            END AS forest_vs_region_avg
            
        FROM Countries c
        
        -- LEFT OUTER JOIN 1: Land Type Breakdown (PRIMARY DATA)
        LEFT OUTER JOIN LandTypeBreakdown lt 
            ON c.country_id = lt.country_id
        
        -- LEFT OUTER JOIN 2: Agricultural Production
        LEFT OUTER JOIN AgriculturalProduction ap 
            ON c.country_id = ap.country_id
        
        -- LEFT OUTER JOIN 3: Top Commodity Details
        LEFT OUTER JOIN TopCommodityPerCountry tcp 
            ON c.country_id = tcp.country_id
        
        -- LEFT OUTER JOIN 4: Regional Statistics
        LEFT OUTER JOIN RegionalLandStats rls 
            ON c.region = rls.region
        
        WHERE c.country_id IS NOT NULL
            AND COALESCE(lt.agricultural_land_total, 0) >= 200  -- critic part for agricultural land minimum 100
        ORDER BY {sort_by} {order.upper()} NULLS LAST;
    """
    
    records = fetch_query(land_efficiency_query, (year, year, year)) or []
    
    # İstatistikler
    total_countries = len(records)
    
    # Global land use totals
    global_stats = {
        'total_land_area': sum((row["land_area"] or 0) for row in records),
        'total_agricultural_land': sum((row["agricultural_land_total"] or 0) for row in records),
        'total_arable_land': sum((row["arable_land"] or 0) for row in records),
        'total_forest_land': sum((row["forest_land"] or 0) for row in records),
        'total_production': sum((row["total_agricultural_production"] or 0) for row in records),
        'avg_crop_diversity': sum((row["crop_diversity"] or 0) for row in records) / total_countries if total_countries > 0 else 0,
    }
    
    # Sıfır bölme hatasını önle
    if global_stats['total_land_area'] > 0:
        global_stats['global_agricultural_percentage'] = (global_stats['total_agricultural_land'] / global_stats['total_land_area'] * 100)
        global_stats['global_forest_percentage'] = (global_stats['total_forest_land'] / global_stats['total_land_area'] * 100)
    else:
        global_stats['global_agricultural_percentage'] = 0
        global_stats['global_forest_percentage'] = 0
    
    # Top performers
    top_by_productivity = sorted(
        [r for r in records if (r.get("land_productivity_index") or 0) > 0],
        key=lambda x: (x.get("land_productivity_index") or 0),
        reverse=True
    )[:10]
    
    top_by_production_density = sorted(
        [r for r in records if (r.get("production_density") or 0) > 0],
        key=lambda x: (x.get("production_density") or 0),
        reverse=True
    )[:10]
    
    top_by_crop_diversity = sorted(
        [r for r in records if (r.get("crop_diversity") or 0) > 0],
        key=lambda x: (x.get("crop_diversity") or 0),
        reverse=True
    )[:10]
    
    top_by_diversity_score = sorted(
        [r for r in records if (r.get("crop_diversity_score") or 0) > 0],
        key=lambda x: (x.get("crop_diversity_score") or 0),
        reverse=True
    )[:10]
    
    top_by_agricultural_percentage = sorted(
        [r for r in records if (r.get("agricultural_land_percentage") or 0) > 0],
        key=lambda x: (x.get("agricultural_land_percentage") or 0),
        reverse=True
    )[:10]
    
    years = list(range(1961, 2026))
    
    return render_template(
        "landuse_efficiency.html",
        records=records,
        year=year,
        years=years,
        total_countries=total_countries,
        global_stats=global_stats,
        top_by_productivity=top_by_productivity,
        top_by_production_density=top_by_production_density,
        top_by_crop_diversity=top_by_crop_diversity,
        top_by_diversity_score=top_by_diversity_score,
        top_by_agricultural_percentage=top_by_agricultural_percentage,
        sort_by=sort_by,
        order=order,
    )
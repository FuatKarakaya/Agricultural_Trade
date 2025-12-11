from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import execute_query, fetch_query

investments_bp = Blueprint("investments", __name__)

@investments_bp.route('/investments')
@investments_bp.route('/investments')
def investmentsPage():
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
            t.total_expenditure,
            t.agriculture_forestry_fishing,
            t.environmental_protection,
            t.biodiversity_landscape,
            t.rd_environmental_protection
        FROM (
            SELECT
                inv.country_name,
                inv.country_id,
                inv.year,
                inv.unit,
                MAX(CASE WHEN inv.expenditure_type = 'Total Expenditure (general government)' 
                    THEN inv.expenditure_value END) AS total_expenditure,
                MAX(CASE WHEN inv.expenditure_type = 'Agriculture, forestry, fishing (general government expenditure)' 
                    THEN inv.expenditure_value END) AS agriculture_forestry_fishing,
                MAX(CASE WHEN inv.expenditure_type = 'Environmental protection (general government expenditure)' 
                    THEN inv.expenditure_value END) AS environmental_protection,
                MAX(CASE WHEN inv.expenditure_type = 'Protection of Biodiversity and Landscape (general government expenditure)' 
                    THEN inv.expenditure_value END) AS biodiversity_landscape,
                MAX(CASE WHEN inv.expenditure_type = 'R&D Environmental Protection (general government expenditure)' 
                    THEN inv.expenditure_value END) AS rd_environmental_protection
            FROM Investments AS inv
            WHERE inv.year = %s
    """
    params = [year]

    # Ülke filtresi SEÇİLİRSE eklenir
    if country_id is not None:
        base_query += " AND inv.country_id = %s"
        params.append(country_id)

    base_query += """
            GROUP BY inv.country_name, inv.country_id, inv.year, inv.unit
        ) AS t
        ORDER BY t.country_name ASC;
    """

    records = fetch_query(base_query, tuple(params)) or []

    # Yüzde hesaplamalarını ekle
    for row in records:
        total = row["total_expenditure"] or 0
        if total > 0:
            row["agriculture_pct"] = (row["agriculture_forestry_fishing"] or 0) / total * 100
            row["environmental_pct"] = (row["environmental_protection"] or 0) / total * 100
            row["biodiversity_pct"] = (row["biodiversity_landscape"] or 0) / total * 100
            row["rd_pct"] = (row["rd_environmental_protection"] or 0) / total * 100
        else:
            row["agriculture_pct"] = None
            row["environmental_pct"] = None
            row["biodiversity_pct"] = None
            row["rd_pct"] = None

    # İstatistikler
    total_rows = len(records)
    total_countries = len({row["country_id"] for row in records}) if records else 0

    # Pie chart için data
    pie_query = """
        SELECT
            SUM(CASE WHEN inv.expenditure_type = 'Total Expenditure (general government)' 
                THEN inv.expenditure_value ELSE 0 END) AS total_expenditure,
            SUM(CASE WHEN inv.expenditure_type = 'Agriculture, forestry, fishing (general government expenditure)' 
                THEN inv.expenditure_value ELSE 0 END) AS total_agriculture,
            SUM(CASE WHEN inv.expenditure_type = 'Environmental protection (general government expenditure)' 
                THEN inv.expenditure_value ELSE 0 END) AS total_environmental,
            SUM(CASE WHEN inv.expenditure_type = 'Protection of Biodiversity and Landscape (general government expenditure)' 
                THEN inv.expenditure_value ELSE 0 END) AS total_biodiversity,
            SUM(CASE WHEN inv.expenditure_type = 'R&D Environmental Protection (general government expenditure)' 
                THEN inv.expenditure_value ELSE 0 END) AS total_rd
        FROM Investments AS inv
        WHERE inv.year = %s
    """
    
    pie_params = [year]
    
    if country_id is not None:
        pie_query += " AND inv.country_id = %s"
        pie_params.append(country_id)
    
    pie_data_row = fetch_query(pie_query, tuple(pie_params))
    
    if pie_data_row and pie_data_row[0]:
        pie_row = pie_data_row[0]
        
        pie_chart_data = {
            'agriculture_forestry_fishing': pie_row['total_agriculture'] or 0,
            'environmental_protection': pie_row['total_environmental'] or 0,
            'biodiversity_landscape': pie_row['total_biodiversity'] or 0,
            'rd_environmental_protection': pie_row['total_rd'] or 0
        }
    else:
        pie_chart_data = {
            'agriculture_forestry_fishing': 0,
            'environmental_protection': 0,
            'biodiversity_landscape': 0,
            'rd_environmental_protection': 0
        }

    # Total expenditure sum
    total_expenditure_sum = sum(row["total_expenditure"] or 0 for row in records)

    return render_template(
        "investments.html",
        records=records,
        year=year,
        years=years,
        total_countries=total_countries,
        total_rows=total_rows,
        countries=countries,
        selected_country_id=country_id,
        pie_chart_data=pie_chart_data,
        total_expenditure_sum=total_expenditure_sum,
    )

@investments_bp.route("/investments/new", methods=["GET"])
def add_investment_form():
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
        "investments_add.html",
        years=years,
        year=year,
        countries=countries,
        selected_country_id=selected_country_id,
    )

@investments_bp.route("/investments/add", methods=["POST"])
def add_investment():
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = request.form.get("unit", "Million USD")

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")

    def get_val(name):
        return request.form.get(name, type=float)

    values = {
        "Total Expenditure (general government)": get_val("total_expenditure"),
        "Agriculture, forestry, fishing (general government expenditure)": get_val("agriculture_forestry_fishing"),
        "Environmental protection (general government expenditure)": get_val("environmental_protection"),
        "Protection of Biodiversity and Landscape (general government expenditure)": get_val("biodiversity_landscape"),
        "R&D Environmental Protection (general government expenditure)": get_val("rd_environmental_protection"),
    }

    for et, v in values.items():
        if v is None:
            errors.append(f"{et} value is required.")
        elif v < 0:
            errors.append(f"{et} value must be >= 0.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("investments.add_investment_form", year=year or 2023, country_id=country_id)
        )

    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("investments.add_investment_form", year=year or 2023, country_id=country_id)
        )

    country_name = country_row[0]["country_name"]

    expenditure_type_list = list(values.keys())
    placeholders = ", ".join(["%s"] * len(expenditure_type_list))

    existing = fetch_query(
        f"""
        SELECT expenditure_type
        FROM Investments
        WHERE country_id = %s
          AND year = %s
          AND expenditure_type IN ({placeholders});
        """,
        (country_id, year, *expenditure_type_list),
    )

    if existing:
        flash("Already existing record.", "error")
        return redirect(
            url_for("investments.add_investment_form", year=year, country_id=country_id)
        )

    params = []
    for et, v in values.items():
        params.extend([country_name, et, unit, v, year, country_id])

    values_sql = ", ".join(["(%s, %s, %s, %s, %s, %s)"] * len(values))

    execute_query(
        f"""
        INSERT INTO Investments (
            country_name,
            expenditure_type,
            unit,
            expenditure_value,
            year,
            country_id
        )
        VALUES {values_sql};
        """,
        tuple(params),
    )

    flash("Investment records added successfully.", "success")

    return redirect(
        url_for("investments.add_investment_form", year=year, country_id=country_id)
    )

@investments_bp.route("/investments/delete", methods=["POST"])
def delete_investment():
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    redirect_country_id = request.form.get("redirect_country_id", type=int)

    if not country_id or not year:
        flash("Error.", "error")
        return redirect(url_for("investments.investmentsPage", year=year or 2023))

    # İlgili ülke + yıl için tüm girdileri sil
    execute_query(
        """
        DELETE FROM Investments
        WHERE country_id = %s AND year = %s;
        """,
        (country_id, year),
    )

    flash("Deleted Successfully.", "success")

    # Aynı yıl ve önceki filtre ile sayfaya dön
    return redirect(
        url_for(
            "investments.investmentsPage",
            year=year,
            country_id=redirect_country_id,
        )
    )

@investments_bp.route("/investments/edit", methods=["GET"])
def edit_investment_form():
    """
    Belirli bir (country_id, year) için var olan Investments kayıtlarını
    düzenlemek üzere form sayfası.
    """
    country_id = request.args.get("country_id", type=int)
    year = request.args.get("year", type=int)

    if not country_id or not year:
        flash("Invalid country or year.", "error")
        return redirect(url_for("investments.investmentsPage", year=year or 2023))

    # Ülke adı
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(url_for("investments.investmentsPage", year=year or 2023))

    country_name = country_row[0]["country_name"]

    # Bu ülke + yıl için mevcut Investments satırlarını çek
    expenditure_type_list = [
        "Total Expenditure (general government)",
        "Agriculture, forestry, fishing (general government expenditure)",
        "Environmental protection (general government expenditure)",
        "Protection of Biodiversity and Landscape (general government expenditure)",
        "R&D Environmental Protection (general government expenditure)",
    ]

    rows = fetch_query(
        """
        SELECT expenditure_type, expenditure_value, unit
        FROM Investments
        WHERE country_id = %s AND year = %s;
        """,
        (country_id, year),
    ) or []

    # Varsayılan değerler: None
    expenditure_values = {et: None for et in expenditure_type_list}
    unit = "Million USD"

    for r in rows:
        et = r["expenditure_type"]
        if et in expenditure_values:
            expenditure_values[et] = r["expenditure_value"]
            if r.get("unit"):
                unit = r["unit"]

    # Hiç kayıt yoksa edit'in anlamı yok
    if not rows:
        flash("No records found for this country and year.", "error")
        return redirect(url_for("investments.investmentsPage", year=year))

    return render_template(
        "investments_edit.html",
        country_id=country_id,
        country_name=country_name,
        year=year,
        unit=unit,
        expenditure_values=expenditure_values,
    )

@investments_bp.route("/investments/update", methods=["POST"])
def update_investment():
    """
    Bir (country_id, year) için tüm expenditure_type değerlerini tek formdan günceller.
    Gerekirse eksik tipler için yeni satır INSERT eder.
    """
    country_id = request.form.get("country_id", type=int)
    year = request.form.get("year", type=int)
    unit = request.form.get("unit", "Million USD")

    errors = []
    if not country_id:
        errors.append("Country is required.")
    if not year:
        errors.append("Year is required.")

    def get_val(name):
        return request.form.get(name, type=float)

    values = {
        "Total Expenditure (general government)": get_val("total_expenditure"),
        "Agriculture, forestry, fishing (general government expenditure)": get_val("agriculture_forestry_fishing"),
        "Environmental protection (general government expenditure)": get_val("environmental_protection"),
        "Protection of Biodiversity and Landscape (general government expenditure)": get_val("biodiversity_landscape"),
        "R&D Environmental Protection (general government expenditure)": get_val("rd_environmental_protection"),
    }

    for et, v in values.items():
        if v is None:
            errors.append(f"{et} value is required.")
        elif v < 0:
            errors.append(f"{et} value must be >= 0.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(
            url_for("investments.edit_investment_form", country_id=country_id, year=year or 2023)
        )

    # Ülke adı doğrula
    country_row = fetch_query(
        "SELECT country_name FROM Countries WHERE country_id = %s;",
        (country_id,)
    )
    if not country_row:
        flash("Selected country not found in Countries table.", "error")
        return redirect(
            url_for("investments.edit_investment_form", country_id=country_id, year=year or 2023)
        )

    country_name = country_row[0]["country_name"]

    # Mevcut tipleri bul
    expenditure_type_list = list(values.keys())
    placeholders = ", ".join(["%s"] * len(expenditure_type_list))

    existing_rows = fetch_query(
        f"""
        SELECT expenditure_type
        FROM Investments
        WHERE country_id = %s
          AND year = %s
          AND expenditure_type IN ({placeholders});
        """,
        (country_id, year, *expenditure_type_list),
    ) or []

    existing_types = {r["expenditure_type"] for r in existing_rows}

    # Her tip için UPDATE veya gerekirse INSERT (upsert mantığı)
    for et in expenditure_type_list:
        v = values[et]
        if et in existing_types:
            execute_query(
                """
                UPDATE Investments
                SET expenditure_value = %s,
                    unit = %s,
                    country_name = %s
                WHERE country_id = %s
                  AND year = %s
                  AND expenditure_type = %s;
                """,
                (v, unit, country_name, country_id, year, et),
            )
        else:
            execute_query(
                """
                INSERT INTO Investments (
                    country_name,
                    expenditure_type,
                    unit,
                    expenditure_value,
                    year,
                    country_id
                )
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (country_name, et, unit, v, year, country_id),
            )

    flash("Records updated successfully.", "success")

    # Edit sayfasında kal, flash mesajı orada gör
    return redirect(
        url_for("investments.edit_investment_form", country_id=country_id, year=year)
    )
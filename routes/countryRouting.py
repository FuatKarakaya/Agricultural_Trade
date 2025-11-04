from flask import Blueprint, render_template, request

country_bp = Blueprint("country", __name__)


@country_bp.route("/countries")
def countries_dashboard():
    return 



@country_bp.route("/countries/<int:country_id>")
def countries_detailed(country_id):
    return 
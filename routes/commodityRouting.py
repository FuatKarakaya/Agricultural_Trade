from flask import Blueprint, render_template, request

commodity_bp = Blueprint("commodity", __name__)

@commodity_bp.route("/commodities")
def commodities_dashboard():
    return "commodities"
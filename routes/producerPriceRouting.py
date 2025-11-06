from flask import Blueprint, render_template, request

producer_price_bp = Blueprint("producer_price", __name__)

@producer_price_bp.route("/producer_prices")
def producer_prices_dashboard():
    return "producer prices"
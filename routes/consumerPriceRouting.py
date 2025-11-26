from flask import Blueprint, render_template, request

consumer_price_bp = Blueprint("consumer_price", __name__)

@consumer_price_bp.route("/consumer_prices")
def consumer_prices_dashboard():
    return "consumer prices"
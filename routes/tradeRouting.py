from flask import Blueprint, render_template, request

trade_bp = Blueprint("trade", __name__)


@trade_bp.route("/trades")
def trade_dashboard():
    return 



@trade_bp.route("/trades/<int:trade_id>")
def trade_detailed(trade_id):
    return 
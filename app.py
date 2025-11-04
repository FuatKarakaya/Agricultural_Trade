from flask import Flask, render_template, request, jsonify
from database import execute_query, execute_update, test_connection
import os
from datetime import datetime

# routes directory will be created later
from routes import (
    main_bp,
    country_bp,
    commodity_bp,
    trade_bp,
    prices_bp,
    landuse_bp,
    prod_bp,
    prod_val_bp,
)

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(country_bp)
app.register_blueprint(commodity_bp)
app.register_blueprint(trade_bp)
app.register_blueprint(prices_bp)
app.register_blueprint(landuse_bp)
app.register_blueprint(prod_bp)
app.register_blueprint(prod_val_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

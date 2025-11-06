from flask import Flask, render_template, request, jsonify
from database import test_connection, get_db_connection, execute_query
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# routes directory will be created later
from routes import (
    # main_bp,
    country_bp,
    consumer_price_bp,
    producer_price_bp,
    commodity_bp,
    trade_bp,
    # landuse_bp,
    prod_bp,
    prod_val_bp,
)

app = Flask(__name__)

#app.register_blueprint(main_bp)
app.register_blueprint(country_bp)
app.register_blueprint(commodity_bp)
app.register_blueprint(consumer_price_bp)
app.register_blueprint(producer_price_bp)
app.register_blueprint(trade_bp)
#app.register_blueprint(landuse_bp)
app.register_blueprint(prod_bp)
app.register_blueprint(prod_val_bp)


if __name__ == "__main__":
    # test_connection() --> This should work OK
    app.run(host="0.0.0.0", debug=True)

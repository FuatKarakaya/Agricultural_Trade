from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from routes import (
    main_bp,
    country_bp,
    trade_bp,
    landuse_bp,
    prod_bp,
    prod_val_bp,
)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(landuse_bp)
    app.register_blueprint(prod_bp)
    app.register_blueprint(prod_val_bp)

    return app


if __name__ == "__main__":
    # test_connection() --> This should work OK
    app = create_app() # Creates the Flask app instance
    # Runs the app on port 5000, accessible from any network interface
    app.run(host="0.0.0.0", port=5000, debug=True)

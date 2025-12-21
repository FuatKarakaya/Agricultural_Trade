from flask import Flask, session
from dotenv import load_dotenv
import os
load_dotenv()

from routes import (
    main_bp,
    country_bp,
    consumer_price_bp,
    producer_price_bp,
    price_statistics_bp,
    commodity_bp,
    trade_bp,
    landuse_bp,
    prod_bp,
    prod_val_bp,
    investments_bp
)
from routes.auth_routes import auth_bp #admin panel


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.urandom(24) #to use flask.flash

    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    # Template'lerde session değişkenlerine kolay erişim
    @app.context_processor
    def inject_user():
        return dict(
            user_logged_in=session.get('logged_in', False),
            username=session.get('username'),
            is_admin=session.get('is_admin', False)
        )


    app.register_blueprint(auth_bp) #admin panel

    app.register_blueprint(main_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(landuse_bp)
    app.register_blueprint(prod_bp)
    app.register_blueprint(prod_val_bp)
    app.register_blueprint(commodity_bp)
    app.register_blueprint(consumer_price_bp)
    app.register_blueprint(producer_price_bp)
    app.register_blueprint(price_statistics_bp)
    app.register_blueprint(investments_bp)
    return app


if __name__ == "__main__":
    # test_connection() --> This should work OK
    app = create_app() # Creates the Flask app instance
    # Runs the app on port 5000, accessible from any network interface
    app.run(host="0.0.0.0", port=5000, debug=True)

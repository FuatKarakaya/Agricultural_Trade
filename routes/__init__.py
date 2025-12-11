from .mainRouting import main_bp
from .countryRouting import country_bp
from .commodityRouting import commodity_bp
from .tradeRouting import trade_bp
from .landuseRouting import landuse_bp
from .prodRouting import prod_bp
from .prodValRouting import prod_val_bp
from .consumerPriceRouting import consumer_price_bp
from .producerPriceRouting import producer_price_bp
from .investments import investments_bp

__all__ = [
    "main_bp",
    "country_bp",
    "consumer_price_bp",
    "producer_price_bp",
    "commodity_bp",
    "trade_bp",
    "landuse_bp",
    "investments_bp",
    "prod_bp",
    "prod_val_bp",
]

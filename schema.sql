-- Countries table
CREATE TABLE COUNTRIES (
    country_id INTEGER PRIMARY KEY,
    population BIGINT,
    region VARCHAR,
    country_name VARCHAR,
    land_area_sq_km BIGINT
);

-- Commodities table
CREATE TABLE COMMODITIES (
    fao_code INTEGER PRIMARY KEY,
    item_name VARCHAR,
    cpc_code VARCHAR
);

-- Consumer Prices table
CREATE TABLE CONSUMER_PRICES (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER,
    year INTEGER,
    month SMALLINT,
    value DOUBLE PRECISION,
    type SMALLINT
);

-- Investments table
CREATE TABLE INVESTMENTS (
    unique_id INTEGER PRIMARY KEY,
    expenditure_type VARCHAR,
    unit VARCHAR,
    expenditure_value DOUBLE PRECISION,
    year INTEGER,
    country_id INTEGER
);

-- Land Use table
CREATE TABLE LAND_USE (
    unique_id INTEGER PRIMARY KEY,
    land_type VARCHAR,
    unit VARCHAR,
    land_usage_value DOUBLE PRECISION,
    year INTEGER,
    country_id INTEGER
);

-- Producer Prices table
CREATE TABLE PRODUCER_PRICES (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER,
    commodity_id INTEGER,
    month SMALLINT,
    year INTEGER,
    unit VARCHAR,
    value DOUBLE PRECISION
);

-- Production table
CREATE TABLE PRODUCTION (
    production_id INTEGER PRIMARY KEY,
    country_code INTEGER,
    commodity_code INTEGER,
    year INTEGER,
    unit VARCHAR,
    quantity NUMERIC
);

-- Production Value table
CREATE TABLE PRODUCTION_VALUE (
    production_value_id INTEGER PRIMARY KEY,
    production_id INTEGER,
    element VARCHAR,
    unit VARCHAR,
    value NUMERIC
);

-- Trade Data Final table
CREATE TABLE TRADE_DATA_FINAL (
    unique_id INTEGER PRIMARY KEY,
    reporter_code INTEGER,
    partner_code INTEGER,
    item_code INTEGER,
    year INTEGER,
    trade_type VARCHAR,
    qty_tonnes NUMERIC,
    val_1k_usd NUMERIC
);



ALTER TABLE CONSUMER_PRICES ADD CONSTRAINT fk_consumer_country 
    FOREIGN KEY (country_id) REFERENCES COUNTRIES(country_id);

ALTER TABLE INVESTMENTS ADD CONSTRAINT fk_investment_country 
    FOREIGN KEY (country_id) REFERENCES COUNTRIES(country_id);

ALTER TABLE LAND_USE ADD CONSTRAINT fk_landuse_country 
    FOREIGN KEY (country_id) REFERENCES COUNTRIES(country_id);

ALTER TABLE PRODUCER_PRICES ADD CONSTRAINT fk_producer_country 
    FOREIGN KEY (country_id) REFERENCES COUNTRIES(country_id);

ALTER TABLE PRODUCER_PRICES ADD CONSTRAINT fk_producer_commodity 
    FOREIGN KEY (commodity_id) REFERENCES COMMODITIES(fao_code);

ALTER TABLE PRODUCTION ADD CONSTRAINT fk_production_country 
    FOREIGN KEY (country_code) REFERENCES COUNTRIES(country_id);

ALTER TABLE PRODUCTION ADD CONSTRAINT fk_production_commodity 
    FOREIGN KEY (commodity_code) REFERENCES COMMODITIES(fao_code);

ALTER TABLE PRODUCTION_VALUE ADD CONSTRAINT fk_prodvalue_production 
    FOREIGN KEY (production_id) REFERENCES PRODUCTION(production_id);

ALTER TABLE TRADE_DATA_FINAL ADD CONSTRAINT fk_trade_reporter 
    FOREIGN KEY (reporter_code) REFERENCES COUNTRIES(country_id);

ALTER TABLE TRADE_DATA_FINAL ADD CONSTRAINT fk_trade_partner 
    FOREIGN KEY (partner_code) REFERENCES COUNTRIES(country_id);

ALTER TABLE TRADE_DATA_FINAL ADD CONSTRAINT fk_trade_item 
    FOREIGN KEY (item_code) REFERENCES COMMODITIES(fao_code);
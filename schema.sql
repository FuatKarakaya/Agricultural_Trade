CREATE TABLE Countries (
    country_id INTEGER PRIMARY KEY,
    population BIGINT,
    region VARCHAR(56),
    subregion VARCHAR(56),
    latitude FLOAT,
    longitude FLOAT,
);
CREATE INDEX idx_countries_region ON Countries(region);

-- Production table
CREATE TABLE Production (
    production_ID SERIAL PRIMARY KEY,
    country_code INTEGER NOT NULL,
    commodity_code INTEGER NOT NULL,
    item_name VARCHAR(128) NOT NULL,
    year INTEGER NOT NULL,
    unit varchar(7),
    quantity DECIMAL(12, 3),
    
    FOREIGN KEY (country_code) REFERENCES Countries(country_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (commodity_code) REFERENCES Commodities(fao_code) 
        ON DELETE CASCADE,
    
    UNIQUE(country_code, commodity_code, year)
);
CREATE INDEX idx_production_country_year ON Production(country_code, year);
CREATE INDEX idx_production_commodity_year ON Production(commodity_code, year);

-- Production_Value table
CREATE TABLE Production_Value (
    production_value_ID SERIAL PRIMARY KEY,
    production_ID INTEGER NOT NULL,
    element VARCHAR(56),
    year INTEGER NOT NULL,
    unit VARCHAR(9),
    value DECIMAL(15, 3),
    
    FOREIGN KEY (production_ID) REFERENCES Production(production_ID) 
        ON DELETE CASCADE,

);


-- Trade_Flows table
CREATE TABLE Trade_Flows (
    unique_id SERIAL PRIMARY KEY,
    reporter_country INTEGER NOT NULL,
    partner_country INTEGER NOT NULL,
    trade_type VARCHAR(56),
    trade_item INTEGER NOT NULL,
    year INTEGER NOT NULL,
    unit VARCHAR(56),
    value INTEGER NOT NULL,
    
    
    FOREIGN KEY (reporter_country) REFERENCES Countries(country_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (partner_country) REFERENCES Countries(country_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (trade_item) REFERENCES Commodities(fao_code) 
        ON DELETE CASCADE,
    
    CHECK (exporter_country_code != importer_country_code),
    
    UNIQUE(reporter_country, partner_country, trade_item, year)
);
CREATE INDEX idx_trade_flows_exporter_year ON Trade_Flows(reporter_country, year);
CREATE INDEX idx_trade_flows_importer_year ON Trade_Flows(partner_country, year);
CREATE INDEX idx_trade_flows_commodity_year ON Trade_Flows(trade_item, year);
-- Land_Use table
CREATE TABLE Land_Use (
    unique_id SERIAL PRIMARY KEY,
    country_name INTEGER REFERENCES Countries(country_id) NOT NULL ON DELETE CASCADE,
    land_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    land_usage_value INTEGER NOT NULL CHECK (land_usage_value >= 0),
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    UNIQUE (country_name, year, land_type)

);
-- investments table
CREATE TABLE Investments (
    unique_id SERIAL PRIMARY KEY,
    country_name INTEGER REFERENCES Countries(country_id) NOT NULL ON DELETE CASCADE,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    unit VARCHAR(50) NOT NULL,
    expenditure_value INTEGER NOT NULL CHECK (expenditure_value >= 0),
    expenditure_type VARCHAR(100) NOT NULL,
    UNIQUE (country_name, year, expenditure_type)
);

CREATE TABLE Commodities (
    fao_code INTEGER PRIMARY KEY,
    item_name VARCHAR(256) NOT NULL UNIQUE,
    cpc_code INTEGER,
    item_group_name (256),
);

CREATE TABLE Producer_Prices (
    unique_id SERIAL PRIMARY KEY,
    country_id INTEGER,
    commodity_id INTEGER,
    price_unit VARCHAR(20),
    year INTEGER,
    month SMALLINT,
    value FLOAT,
    
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code),
    UNIQUE(country_id, commodity_id, year, month)
);

CREATE TABLE Consumer_Prices (
    unique_id SERIAL PRIMARY KEY,
    country_id INTEGER,
    commodity_id INTEGER,
    year INTEGER,
    month SMALLINT,
    value FLOAT,

    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code),
    UNIQUE(country_id, commodity_id, year, month)
);
CREATE TABLE Countries (
    country_id INTEGER PRIMARY KEY,
    population BIGINT,
    region VARCHAR(56),
    subregion VARCHAR(56),
    latitude FLOAT,
    longitude FLOAT,
);
CREATE INDEX idx_countries_region ON Countries(region);


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
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100)
);
-- investments table
CREATE TABLE Investments (
    unique_id SERIAL PRIMARY KEY,
    country_name INTEGER REFERENCES Countries(country_id) NOT NULL ON DELETE CASCADE,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    unit VARCHAR(50) NOT NULL,
    expenditure_value INTEGER NOT NULL CHECK (expenditure_value >= 0),
    expenditure_type VARCHAR(100) NOT NULL
);

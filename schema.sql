CREATE TABLE Countries (
    country_id INTEGER PRIMARY KEY,
    population BIGINT,
    region VARCHAR(56),
    subregion VARCHAR(56),
    latitude FLOAT,
    longitude FLOAT
);
CREATE INDEX idx_countries_region ON Countries(region);

CREATE TABLE Commodities (
    fao_code INTEGER PRIMARY KEY,
    item_name VARCHAR(256) NOT NULL UNIQUE,
    cpc_code VARCHAR(256),
    -- item_group_name VARCHAR(256) kaldırıldı
);


CREATE TABLE Production (
    production_ID SERIAL PRIMARY KEY,
    country_code INTEGER NOT NULL,
    commodity_code INTEGER NOT NULL,
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


CREATE TABLE Production_Value (
    production_value_ID SERIAL PRIMARY KEY,
    production_ID INTEGER NOT NULL,
    element VARCHAR(56),
    unit VARCHAR(9),
    value DECIMAL(15, 3),
    
    FOREIGN KEY (production_ID) REFERENCES Production(production_ID) 
        ON DELETE CASCADE
);


/* Eski hali
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
    
    CHECK (reporter_country != partner_country),
    
    UNIQUE(reporter_country, partner_country, trade_item, year)
);*/

CREATE TABLE Trade_data_long (
    unique_id SERIAL PRIMARY KEY,
    reporter_countries INTEGER NOT NULL,
    partner_countries INTEGER NOT NULL,
    item_code INTEGER NOT NULL,
    element TEXT,
    unit VARCHAR(56),
    year INTEGER NOT NULL,
    value NUMERIC NOT NULL,
    
    
    FOREIGN KEY (reporter_countries) REFERENCES Countries(country_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (partner_countries) REFERENCES Countries(country_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (item_code) REFERENCES Commodities(fao_code) 
        ON DELETE CASCADE,
    
    CHECK (reporter_country != partner_country),

);
CREATE INDEX idx_trade_flows_exporter_year ON Trade_Flows(reporter_country, year);
CREATE INDEX idx_trade_flows_importer_year ON Trade_Flows(partner_country, year);
CREATE INDEX idx_trade_flows_commodity_year ON Trade_Flows(trade_item, year);

CREATE TABLE Land_Use (
    unique_id SERIAL PRIMARY KEY,
    land_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    land_usage_value FLOAT NOT NULL CHECK (land_usage_value >= 0),
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id) ON DELETE CASCADE,
    UNIQUE (country_id, year, land_type,unit)
);

CREATE TABLE Investments (
    unique_id SERIAL PRIMARY KEY,
    expenditure_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    expenditure_value FLOAT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id) ON DELETE CASCADE,
    UNIQUE (country_id, year, expenditure_type,unit)
);

-- eski hali
    -- CREATE TABLE Producer_Prices (
    --     unique_id SERIAL PRIMARY KEY,
    --     country_id INTEGER,
    --     commodity_id INTEGER,
    --     price_unit VARCHAR(20), --silindi hepsi LCU
    --     year INTEGER,
    --     month SMALLINT,
    --     value FLOAT,
    --     FOREIGN KEY (country_id) REFERENCES countries(country_id) ON UPDATE CASCADE,
    --     FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code) ON UPDATE CASCADE,
    --     UNIQUE(country_id, commodity_id, year, month)
    -- );
-- yanlışlıkla silindi
-- CREATE TABLE Producer_Prices (
--     unique_id SERIAL PRIMARY KEY,
--     country_id INTEGER,
--     commodity_id INTEGER,
--     month SMALLINT,
--     Y2010 FLOAT,Y2011 FLOAT,Y2012 FLOAT,Y2013 FLOAT,
--     Y2014 FLOAT,Y2015 FLOAT,Y2016 FLOAT,Y2017 FLOAT,Y2018 FLOAT,
--     Y2019 FLOAT,Y2020 FLOAT,Y2021 FLOAT,Y2022 FLOAT,Y2023 FLOAT,
--     FOREIGN KEY (country_id) REFERENCES countries(country_id) ON UPDATE CASCADE,
--     FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code) ON UPDATE CASCADE,
-- );

CREATE TABLE Producer_Prices (
    unique_id SERIAL PRIMARY KEY,
    country_id INTEGER,
    commodity_id INTEGER,
    month SMALLINT,
    year INTEGER,
    unit VARCHAR(10),
    value FLOAT,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id) ON UPDATE CASCADE,
    FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code) ON UPDATE CASCADE,
    UNIQUE(country_id, commodity_id, month, year)
);

-- eski hali
    -- CREATE TABLE Consumer_Prices (
    --     unique_id SERIAL PRIMARY KEY,
    --     country_id INTEGER,
    --     commodity_id INTEGER, --Silinecek
    --     -- type SMALLINT, --eklenecek
    --     -- type = 1 -> Consumer Prices, General Indices (2015 = 100), 2 -> Consumer Prices, Food Indices (2015 = 100)
    --     year INTEGER,
    --     month SMALLINT,
    --     value FLOAT,

    --     FOREIGN KEY (country_id) REFERENCES countries(country_id) ON UPDATE CASCADE,
    --     FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code) ON UPDATE CASCADE,
    --     UNIQUE(country_id, commodity_id, year, month)
    -- );

CREATE TABLE Consumer_Prices (
    unique_id SERIAL PRIMARY KEY,
    country_id INTEGER,
    type SMALLINT,
    year INTEGER,
    month SMALLINT,
    value FLOAT,
    FOREIGN KEY (country_id) REFERENCES countries(country_id) ON UPDATE CASCADE,
    FOREIGN KEY (commodity_id) REFERENCES Commodities(fao_code) ON UPDATE CASCADE,
);
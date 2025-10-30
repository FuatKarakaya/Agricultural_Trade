-- Land_Use table
CREATE TABLE Land_Use (
    unique_id SERIAL PRIMARY KEY,
    country_name INTEGER REFERENCES Countries(country_id) NOT NULL,
    land_type VARCHAR(100),
    unit VARCHAR(50),
    land_usage_value INTEGER,
    year INTEGER
);
-- investments table
CREATE TABLE Investments (
    unique_id SERIAL PRIMARY KEY,
    country_name INTEGER REFERENCES Countries(country_id) NOT NULL,
    year INTEGER,
    unit VARCHAR(50),
    expenditure_value INTEGER,
    expenditure_type VARCHAR(100)
);
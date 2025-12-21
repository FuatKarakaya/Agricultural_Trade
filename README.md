# 🌾 Agricultural Trade Database System

A comprehensive database management system for analyzing global agricultural trade, production, prices, land use, and investment data. Built with Flask and PostgreSQL.

![ER Diagram](BLG%20317E.Week%208.ER%20Modeling%20and%20Functional%20Dependencies.pdf)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Database Schema](#database-schema)
- [ER Diagram](#er-diagram)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Routes](#api-routes)
- [Contributing](#contributing)
- [License](#license)

---

## 🌍 Overview

This project is a full-stack web application designed to manage and analyze agricultural data from around the world. It provides insights into:

- **Global Trade Flows** - Import/Export data between countries
- **Agricultural Production** - Commodity production quantities and values
- **Price Tracking** - Consumer and producer price indices
- **Land Use** - Agricultural land usage statistics by country
- **Investment Data** - Government and private agricultural expenditure

The system supports complex queries, data visualization, and administrative data management through a web interface.

---

## ✨ Features

- 🔐 **Authentication System** - Admin panel with role-based access control
- 📊 **Data Visualization** - Interactive charts and reports
- 🔍 **Advanced Search** - Filter and query across multiple dimensions
- 📈 **Analytics Dashboard** - Key metrics and insights
- 🗺️ **Geographic Analysis** - Country and region-based data exploration
- 📝 **CRUD Operations** - Full create, read, update, delete functionality
- 🌐 **RESTful API** - Well-structured blueprint-based routing
- 💾 **Robust Schema** - Normalized database with referential integrity

---

## 🗄️ Database Schema

The database consists of **9 core tables** with the following relationships:

### Core Entities

#### 1. **Countries**
Stores country information and geographic metadata.
```sql
country_id (PK) | population | region | subregion | latitude | longitude
```

#### 2. **Commodities**
Agricultural products and items tracked in the system.
```sql
fao_code (PK) | item_name | cpc_code
```

### Transaction Tables

#### 3. **Production**
Agricultural production data by country and commodity.
```sql
production_id (PK) | country_code (FK) | commodity_code (FK) | year | unit | quantity
```
- **Total Participation**: Every production record MUST have a country and commodity

#### 4. **Production_Value**
Economic valuation of production records.
```sql
production_value_id (PK) | production_id (FK) | element | unit | value
```
- **Total Participation**: Every value record MUST reference a production record

#### 5. **Trade_Data_Final**
International trade flows between countries.
```sql
unique_id (PK) | reporter_code (FK) | partner_code (FK) | item_code (FK) | 
year | trade_type | qty_tonnes | val_1k_usd
```

#### 6. **Producer_Prices**
Monthly producer price indices by commodity and country.
```sql
unique_id (PK) | country_id (FK) | commodity_id (FK) | month | 
Y2010-Y2023 (yearly columns)
```

#### 7. **Consumer_Prices**
Consumer price indices and food inflation rates.
```sql
unique_id (PK) | country_id (FK) | year | month | value | type
```
Types: 
- `1` → General Consumer Prices (2015=100)
- `2` → Food Price Index (2015=100)
- `3` → Food Price Inflation

#### 8. **Land_Use**
Agricultural land usage by type and country.
```sql
unique_id (PK) | country_id (FK) | land_type | unit | 
land_usage_value | year
```
- **Total Participation**: Every record MUST reference a country

#### 9. **Investments**
Government and private agricultural expenditure.
```sql
unique_id (PK) | country_id (FK) | expenditure_type | unit | 
expenditure_value | year
```
- **Total Participation**: Every record MUST reference a country

---

## 🔗 ER Diagram

The Entity-Relationship diagram follows **Chen notation** with:
- **Rectangles** for entities
- **Ellipses** for attributes (underlined for primary keys)
- **Diamonds** for relationships
- **Double lines** for total participation constraints

### Key Relationships

| Relationship | Cardinality | Participation |
|--------------|-------------|---------------|
| Countries → Consumer_Prices | 1:N | Partial |
| Countries → Investments | 1:N | **Total** (double line) |
| Countries → Land_Use | 1:N | **Total** (double line) |
| Countries → Producer_Prices | 1:N | Partial |
| Countries → Production | 1:N | **Total** (double line) |
| Commodities → Producer_Prices | 1:N | Partial |
| Commodities → Production | 1:N | **Total** (double line) |
| Production → Production_Value | 1:N | **Total** (double line) |
| Countries → Trade_Data (reporter) | 1:N | Partial |
| Countries → Trade_Data (partner) | 1:N | Partial |
| Commodities → Trade_Data | 1:N | Partial |

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.x
- Flask (Web Framework)
- PostgreSQL (Database)
- psycopg2 (PostgreSQL adapter)

**Frontend:**
- HTML5/CSS3
- JavaScript
- Jinja2 Templates

**Development:**
- dotenv (Environment variables)
- Flask Sessions (Authentication)

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/FuatKarakaya/Agricultural_Trade.git
cd Agricultural_Trade
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
psql -U postgres
CREATE DATABASE agricultural_trade;
\c agricultural_trade
\i schema.sql
\i countries.sql
```

5. **Configure environment variables**
Create a `.env` file in the root directory:
```env
DB_NAME=agricultural_trade
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

6. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## 🚀 Usage

### Admin Panel
Access the admin panel at `/login` with credentials:
- Manage database records
- Import/export data
- View system statistics

### Public Interface
- **Homepage**: `/` - Overview and quick stats
- **Countries**: `/countries` - Browse by country
- **Commodities**: `/commodities` - Agricultural products catalog
- **Trade**: `/trade` - International trade flows
- **Production**: `/production` - Production statistics
- **Prices**: `/prices` - Price indices and inflation
- **Land Use**: `/landuse` - Agricultural land statistics
- **Investments**: `/investments` - Expenditure tracking

---

## 📁 Project Structure

```
Agricultural_Trade/
├── app.py                    # Main Flask application
├── database.py               # Database connection handler
├── settings.py               # Application settings
├── schema.sql                # Database schema definition
├── countries.sql             # Country data initialization
├── .env                      # Environment variables (not in repo)
├── .gitignore               # Git ignore rules
├── LICENSE                   # GNU GPL v3.0
├── README.md                 # This file
│
├── routes/                   # Blueprint route modules
│   ├── __init__.py          # Route registration
│   ├── mainRouting.py       # Homepage and dashboard
│   ├── auth_routes.py       # Authentication & admin
│   ├── countryRouting.py    # Country-related endpoints
│   ├── commodityRouting.py  # Commodity catalog
│   ├── tradeRouting.py      # Trade flow queries
│   ├── prodRouting.py       # Production data
│   ├── prodValRouting.py    # Production values
│   ├── consumerPriceRouting.py  # Consumer prices
│   ├── producerPriceRouting.py  # Producer prices
│   ├── landuseRouting.py    # Land use statistics
│   └── investments.py       # Investment tracking
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   ├── login.html           # Authentication
│   └── ...                  # Feature-specific templates
│
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Images and icons
│
├── one use python files for importing and shaping/
│   └── ...                  # Data import utilities
│
└── __pycache__/             # Python cache (auto-generated)
```

---

## 🛣️ API Routes

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /admin` - Admin dashboard

### Core Resources

#### Countries
- `GET /countries` - List all countries
- `GET /countries/<id>` - Get country details
- `GET /countries/region/<region>` - Filter by region

#### Commodities
- `GET /commodities` - List all commodities
- `GET /commodities/<id>` - Get commodity details

#### Trade
- `GET /trade` - Trade flow explorer
- `GET /trade/reporter/<country_id>` - Export data
- `GET /trade/partner/<country_id>` - Import data
- `GET /trade/commodity/<commodity_id>` - Trade by commodity

#### Production
- `GET /production` - Production statistics
- `GET /production/country/<id>` - Country production
- `GET /production/commodity/<id>` - Commodity production
- `GET /production/year/<year>` - Yearly production

#### Prices
- `GET /consumer-prices` - Consumer price indices
- `GET /producer-prices` - Producer price indices
- `GET /prices/country/<id>` - Country-specific prices

#### Land Use
- `GET /landuse` - Land use statistics
- `GET /landuse/country/<id>` - Country land use
- `GET /landuse/type/<type>` - By land type

#### Investments
- `GET /investments` - Investment data
- `GET /investments/country/<id>` - Country investments
- `GET /investments/year/<year>` - Yearly investments

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Fuat Karakaya** - [GitHub Profile](https://github.com/FuatKarakaya)

---

## 📞 Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/FuatKarakaya/Agricultural_Trade/issues).

---

## 🙏 Acknowledgments

- FAO (Food and Agriculture Organization) for agricultural data standards
- PostgreSQL community for excellent documentation
- Flask framework contributors

---

**Built with ❤️ for agricultural data analysis**

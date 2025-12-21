#  Agricultural Trade Database System

> A comprehensive web application for analyzing global agricultural trade, production, prices, land use, and investment data.


##  Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Database Schema](#%EF%B8%8F-database-schema)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Routes](#%EF%B8%8F-api-routes)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)
- [Authors](#-authors)

---

## 🌍 Overview

The Agricultural Trade Database System is a full-stack web application designed to manage and analyze comprehensive agricultural data from around the world. Built with Flask and PostgreSQL, it provides powerful tools for researchers, policymakers, and analysts to explore:

- **🌐 Global Trade Flows** - Bilateral import/export data between 200+ countries
- **🌱 Agricultural Production** - Commodity production quantities and economic values
- **💰 Price Tracking** - Consumer and producer price indices with inflation metrics
- **🗺️ Land Use Analysis** - Agricultural land usage statistics and trends
- **💼 Investment Data** - Government and private sector agricultural expenditure

The system features an intuitive web interface, RESTful API architecture, advanced filtering capabilities, and role-based access control for data management.

---

## ✨ Features

### Core Functionality
- 🔐 **Authentication & Authorization** - Secure admin panel with role-based access control
- 📊 **Interactive Data Visualization** - Dynamic charts and reports using JavaScript
- 🔍 **Advanced Search & Filtering** - Multi-dimensional queries across all datasets
- 📈 **Analytics Dashboard** - Key performance indicators and trend analysis
- 🗺️ **Geographic Analysis** - Country and region-based data exploration
- ⏱️ **Time Series Analysis** - Timeline visualizations for trends over years

### Data Management
- 📝 **Full CRUD Operations** - Create, read, update, and delete functionality for all entities
- 🔄 **Data Import Tools** - Utilities for importing CSV and cleaning datasets
- ✅ **Data Validation** - Referential integrity and constraint enforcement
- 📤 **Export Capabilities** - Download filtered results for offline analysis

### Technical Features
- 🌐 **RESTful API Design** - Well-structured blueprint-based routing
- 💾 **Normalized Database** - Efficient schema with proper indexing and foreign keys
- 🎨 **Responsive UI** - Mobile-friendly interface with modern design
- ⚡ **Optimized Queries** - Fast data retrieval with connection pooling

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Primary programming language
- **Flask 2.0+** - Lightweight WSGI web application framework
- **PostgreSQL 12+** - Robust relational database management system
- **psycopg2** - PostgreSQL database adapter for Python
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5/CSS3** - Modern markup and styling
- **JavaScript (ES6+)** - Interactive client-side functionality
- **Chart.js / D3.js** - Data visualization libraries
- **Jinja2** - Server-side templating engine

### Database Hosting
- **Neon Database** - Serverless PostgreSQL with autoscaling

### Development Tools
- **Git** - Version control
- **Flask Sessions** - User session management
- **Virtual Environment** - Dependency isolation

---

## 🗄️ Database Schema

The database consists of **9 core tables** with referential integrity constraints enforcing data consistency.

### Core Entities

#### 1. COUNTRIES
Stores country information and geographic metadata.
```sql
CREATE TABLE COUNTRIES (
    country_id INTEGER PRIMARY KEY,
    population BIGINT,
    region VARCHAR,
    country_name VARCHAR,
    land_area_sq_km BIGINT
);
```

#### 2. COMMODITIES
Agricultural products tracked in the system (FAO classification).
```sql
CREATE TABLE COMMODITIES (
    fao_code INTEGER PRIMARY KEY,
    item_name VARCHAR,
    cpc_code VARCHAR
);
```

### Transaction Tables

#### 3. PRODUCTION
Agricultural production data by country, commodity, and year.
```sql
CREATE TABLE PRODUCTION (
    production_id INTEGER PRIMARY KEY,
    country_code INTEGER REFERENCES COUNTRIES(country_id),
    commodity_code INTEGER REFERENCES COMMODITIES(fao_code),
    year INTEGER,
    unit VARCHAR,
    quantity NUMERIC
);
```

#### 4. PRODUCTION_VALUE
Economic valuation of production records.
```sql
CREATE TABLE PRODUCTION_VALUE (
    production_value_id INTEGER PRIMARY KEY,
    production_id INTEGER REFERENCES PRODUCTION(production_id),
    element VARCHAR,
    unit VARCHAR,
    value NUMERIC
);
```

#### 5. TRADE_DATA_FINAL
International trade flows between countries.
```sql
CREATE TABLE TRADE_DATA_FINAL (
    unique_id INTEGER PRIMARY KEY,
    reporter_code INTEGER REFERENCES COUNTRIES(country_id),
    partner_code INTEGER REFERENCES COUNTRIES(country_id),
    item_code INTEGER REFERENCES COMMODITIES(fao_code),
    year INTEGER,
    trade_type VARCHAR,
    qty_tonnes NUMERIC,
    val_1k_usd NUMERIC
);
```

#### 6. PRODUCER_PRICES
Monthly producer price indices by commodity and country.
```sql
CREATE TABLE PRODUCER_PRICES (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER REFERENCES COUNTRIES(country_id),
    commodity_id INTEGER REFERENCES COMMODITIES(fao_code),
    month SMALLINT,
    year INTEGER,
    unit VARCHAR,
    value DOUBLE PRECISION
);
```

#### 7. CONSUMER_PRICES
Consumer price indices and food inflation rates.
```sql
CREATE TABLE CONSUMER_PRICES (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER REFERENCES COUNTRIES(country_id),
    year INTEGER,
    month SMALLINT,
    value DOUBLE PRECISION,
    type SMALLINT  -- 1: General CPI, 2: Food Price Index, 3: Food Inflation
);
```

#### 8. LAND_USE
Agricultural land usage by type and country.
```sql
CREATE TABLE LAND_USE (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER REFERENCES COUNTRIES(country_id),
    land_type VARCHAR,
    unit VARCHAR,
    land_usage_value DOUBLE PRECISION,
    year INTEGER
);
```

#### 9. INVESTMENTS
Government and private agricultural expenditure.
```sql
CREATE TABLE INVESTMENTS (
    unique_id INTEGER PRIMARY KEY,
    country_id INTEGER REFERENCES COUNTRIES(country_id),
    expenditure_type VARCHAR,
    unit VARCHAR,
    expenditure_value DOUBLE PRECISION,
    year INTEGER
);
```

### Entity Relationships

| From Table | To Table | Relationship Type | Constraint |
|------------|----------|-------------------|------------|
| PRODUCTION | COUNTRIES | N:1 | Foreign Key (country_code) |
| PRODUCTION | COMMODITIES | N:1 | Foreign Key (commodity_code) |
| PRODUCTION_VALUE | PRODUCTION | N:1 | Foreign Key (production_id) |
| TRADE_DATA_FINAL | COUNTRIES (reporter) | N:1 | Foreign Key (reporter_code) |
| TRADE_DATA_FINAL | COUNTRIES (partner) | N:1 | Foreign Key (partner_code) |
| TRADE_DATA_FINAL | COMMODITIES | N:1 | Foreign Key (item_code) |
| PRODUCER_PRICES | COUNTRIES | N:1 | Foreign Key (country_id) |
| PRODUCER_PRICES | COMMODITIES | N:1 | Foreign Key (commodity_id) |
| CONSUMER_PRICES | COUNTRIES | N:1 | Foreign Key (country_id) |
| LAND_USE | COUNTRIES | N:1 | Foreign Key (country_id) |
| INVESTMENTS | COUNTRIES | N:1 | Foreign Key (country_id) |

---

## 📦 Installation

### Prerequisites

Ensure you have the following installed on your system:
- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **pip** (comes with Python)
- **PostgreSQL account** (or use Neon serverless PostgreSQL)

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/FuatKarakaya/Agricultural_Trade.git
cd Agricultural_Trade
```

#### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install flask psycopg2-binary python-dotenv
```

> **Note:** If there's a `requirements.txt` file, use: `pip install -r requirements.txt`

#### 4. Set Up the Database

**Option A: Using Neon (Serverless PostgreSQL)**
1. Sign up at [Neon](https://neon.tech/)
2. Create a new project
3. Copy the connection string provided

**Option B: Local PostgreSQL**
```bash
# Start PostgreSQL service
# Windows: Services → PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
psql -U postgres
CREATE DATABASE agricultural_trade;
\q
```

#### 5. Initialize Database Schema
```bash
# Using psql
psql -U postgres -d agricultural_trade -f schema.sql
psql -U postgres -d agricultural_trade -f countries.sql

# Or if using Neon, use their SQL editor to run schema.sql and countries.sql
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root directory:

```env
# For Neon Database (Recommended)
DATABASE_URL="postgresql://username:password@host.region.aws.neon.tech/database_name?sslmode=require"

# Or for local PostgreSQL
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/agricultural_trade"
```

**Important:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

### Application Settings

The application uses the following default configurations (defined in [app.py](app.py)):
- **Host:** `0.0.0.0` (accessible from any network interface)
- **Port:** `5000`
- **Debug Mode:** `True` (disable in production)
- **Session Lifetime:** 3600 seconds (1 hour)

---

## 🚀 Usage

### Starting the Application

```bash
# Make sure virtual environment is activated
python app.py
```

You should see output similar to:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Access the application at: **http://localhost:5000**

### Admin Panel

To access administrative features:
1. Navigate to `/login`
2. Enter admin credentials (configure in database)
3. Manage database records through the admin interface

**Admin Capabilities:**
- Add/Edit/Delete records in all tables
- Import bulk data from CSV files
- View system statistics and logs
- Manage user accounts and permissions

### Public Interface

Available routes for data exploration:
- **Homepage**: `/` - Dashboard with overview statistics
- **Countries**: `/countries` - Browse countries with filtering by region
- **Country Details**: `/countries/<id>` - Detailed country profile
- **Commodities**: `/commodities` - Agricultural products catalog
- **Trade Flows**: `/trade` - International trade analysis
- **Production**: `/production` - Production quantity statistics
- **Production Values**: `/production-values` - Economic production data
- **Consumer Prices**: `/consumer-prices` - CPI and food inflation
- **Producer Prices**: `/producer-prices` - Producer price indices
- **Land Use**: `/landuse` - Agricultural land statistics
- **Land Use Timeline**: `/landuse/timeline` - Time series visualization
- **Investments**: `/investments` - Expenditure tracking
- **Investments Timeline**: `/investments/timeline` - Investment trends

---

## 📁 Project Structure

```
Agricultural_Trade/
│
├── 📄 app.py                          # Main Flask application entry point
├── 🔌 database.py                     # PostgreSQL connection handler
├── ⚙️ settings.py                     # Application configuration settings
├── 📊 schema.sql                      # Database schema definition (DDL)
├── 🌍 countries.sql                   # Country reference data initialization
├── 🔐 .env                            # Environment variables (not in repo)
├── 🚫 .gitignore                      # Git ignore rules
├── 📜 LICENSE                         # GNU General Public License v3.0
├── 📖 README.md                       # This documentation file
├── 📝 log.sql                         # SQL operation logs
│
├── 📂 routes/                         # Flask Blueprint modules
│   ├── __init__.py                   # Blueprint registration and exports
│   ├── mainRouting.py                # Homepage and dashboard routes
│   ├── auth_routes.py                # Authentication & authorization
│   ├── countryRouting.py             # Country-related endpoints
│   ├── commodityRouting.py           # Commodity catalog endpoints
│   ├── tradeRouting.py               # Trade flow queries
│   ├── prodRouting.py                # Production data routes
│   ├── prodValRouting.py             # Production values routes
│   ├── consumerPriceRouting.py       # Consumer price endpoints
│   ├── producerPriceRouting.py       # Producer price endpoints
│   ├── priceStatisticsRouting.py     # Price analytics routes
│   ├── landuseRouting.py             # Land use statistics
│   └── investments.py                # Investment tracking routes
│
├── �� templates/                      # Jinja2 HTML templates
│   ├── layout.html                   # Base template with common elements
│   ├── dashboard.html                # Main dashboard
│   ├── login.html                    # Authentication page
│   ├── error.html                    # Error page template
│   │
│   ├── countries.html                # Country list view
│   ├── country_detail.html           # Country profile page
│   ├── commodities.html              # Commodity catalog
│   │
│   ├── trade_statistics.html         # Trade flow explorer
│   ├── trade_flows.html              # Detailed trade analysis
│   │
│   ├── production.html               # Production statistics
│   ├── production_add.html           # Add production record
│   ├── production_edit.html          # Edit production record
│   ├── production_values.html        # Production values view
│   ├── production_value_add.html     # Add production value
│   ├── production_value_edit.html    # Edit production value
│   │
│   ├── consumer_prices.html          # Consumer price index
│   ├── consumer_price_add.html       # Add consumer price
│   ├── consumer_price_edit.html      # Edit consumer price
│   ├── producer_prices.html          # Producer price index
│   ├── producer_price_add.html       # Add producer price
│   ├── producer_price_edit.html      # Edit producer price
│   ├── price_statistics.html         # Price analytics dashboard
│   │
│   ├── land_use.html                 # Land use statistics
│   ├── land_use_add.html             # Add land use record
│   ├── land_use_edit.html            # Edit land use record
│   ├── land_use_timeline.html        # Land use time series
│   ├── landuse_efficiency.html       # Land use efficiency metrics
│   │
│   ├── investments.html              # Investment data view
│   ├── investments_add.html          # Add investment record
│   ├── investments_edit.html         # Edit investment record
│   └── investments_timeline.html     # Investment trends
│
├── 📂 static/                         # Static assets
│   ├── css/                          # Stylesheets
│   ├── js/                           # JavaScript files
│   │   ├── land_use.js              # Land use page interactions
│   │   ├── land_use_timeline.js     # Land use timeline charts
│   │   ├── investments.js           # Investment page interactions
│   │   ├── investments_timeline.js  # Investment timeline charts
│   │   └── trade_statistics.js      # Trade statistics visualizations
│   └── images/                       # Images and icons
│
├── 📂 one use python files for importing and shaping/
│   ├── fill_CP.py                    # Import consumer price data
│   ├── fill_PP.py                    # Import producer price data
│   ├── fill_Commodities.py           # Import commodity reference data
│   ├── temp_import_cp.py             # Temporary import utilities
│   ├── temp_table_importer.py        # Table import helper
│   ├── table_cleaner.py              # Data cleaning utilities
│   ├── filter.py                     # Data filtering scripts
│   ├── fixcsv.py                     # CSV repair utilities
│   ├── pandascode.py                 # Pandas data transformation
│   ├── scaler.py                     # Data normalization
│   ├── shaveandclean.py              # Data preprocessing
│   ├── delete_numeric_commodities.py # Remove invalid commodity entries
│   └── normalize_producer_prices.py  # Price normalization
│
├── 🔧 csv_cleaner.py                  # CSV data cleaning utility
├── 📏 size_checker.py                 # Database size monitoring
├── 🔍 find_missing_countries.py       # Data validation script
├── 📄 missing_countries_report.txt    # Validation results
├── 🧪 temp.py                         # Temporary testing script
│
└── 📂 __pycache__/                    # Python bytecode cache (auto-generated)
```

---

## 🛣️ API Routes

### Authentication Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/login` | Display login page | No |
| POST | `/login` | Authenticate user | No |
| GET | `/logout` | End user session | Yes |
| GET | `/dashboard` | Admin dashboard | Yes (Admin) |

### Country Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/countries` | List all countries with optional region filter |
| GET | `/countries/<id>` | Get detailed country information |
| GET | `/countries/region/<region>` | Filter countries by region |

### Commodity Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commodities` | List all agricultural commodities |
| GET | `/commodities/<fao_code>` | Get commodity details |
| GET | `/commodities/search?q=<query>` | Search commodities by name |

### Trade Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trade` | Trade flow explorer interface |
| GET | `/trade/statistics` | Aggregated trade statistics |
| GET | `/trade/reporter/<country_id>` | Export data for specific country |
| GET | `/trade/partner/<country_id>` | Import data for specific country |
| GET | `/trade/commodity/<commodity_id>` | Trade volume by commodity |
| GET | `/trade/year/<year>` | Trade data for specific year |

### Production Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/production` | Production statistics overview | No |
| GET | `/production/<id>` | Get specific production record | No |
| POST | `/production/add` | Add new production record | Yes (Admin) |
| PUT | `/production/edit/<id>` | Update production record | Yes (Admin) |
| DELETE | `/production/delete/<id>` | Delete production record | Yes (Admin) |
| GET | `/production/country/<country_id>` | Filter by country | No |
| GET | `/production/commodity/<commodity_id>` | Filter by commodity | No |

### Production Value Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/production-values` | List production values | No |
| POST | `/production-values/add` | Add new value record | Yes (Admin) |
| PUT | `/production-values/edit/<id>` | Update value record | Yes (Admin) |
| DELETE | `/production-values/delete/<id>` | Delete value record | Yes (Admin) |

### Consumer Price Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/consumer-prices` | Consumer price indices | No |
| GET | `/consumer-prices/<id>` | Specific price record | No |
| POST | `/consumer-prices/add` | Add price record | Yes (Admin) |
| PUT | `/consumer-prices/edit/<id>` | Update price record | Yes (Admin) |
| DELETE | `/consumer-prices/delete/<id>` | Delete price record | Yes (Admin) |
| GET | `/consumer-prices/country/<country_id>` | Filter by country | No |

### Producer Price Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/producer-prices` | Producer price indices | No |
| POST | `/producer-prices/add` | Add price record | Yes (Admin) |
| PUT | `/producer-prices/edit/<id>` | Update price record | Yes (Admin) |
| DELETE | `/producer-prices/delete/<id>` | Delete price record | Yes (Admin) |

### Land Use Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/landuse` | Land use statistics | No |
| GET | `/landuse/timeline` | Time series visualization | No |
| POST | `/landuse/add` | Add land use record | Yes (Admin) |
| PUT | `/landuse/edit/<id>` | Update land use record | Yes (Admin) |
| DELETE | `/landuse/delete/<id>` | Delete land use record | Yes (Admin) |
| GET | `/landuse/country/<country_id>` | Filter by country | No |
| GET | `/landuse/efficiency` | Calculate efficiency metrics | No |

### Investment Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/investments` | Investment data overview | No |
| GET | `/investments/timeline` | Investment trends over time | No |
| POST | `/investments/add` | Add investment record | Yes (Admin) |
| PUT | `/investments/edit/<id>` | Update investment record | Yes (Admin) |
| DELETE | `/investments/delete/<id>` | Delete investment record | Yes (Admin) |
| GET | `/investments/country/<country_id>` | Filter by country | No |

---

## 📸 Screenshots

> Add screenshots of your application here to showcase the user interface

### Dashboard
![Dashboard](docs/images/dashboard.png)

### Trade Statistics
![Trade Statistics](docs/images/trade.png)

### Country Details
![Country Details](docs/images/country-detail.png)

### Price Analysis
![Price Analysis](docs/images/prices.png)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Agricultural_Trade.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guide for Python
   - Add comments for complex logic
   - Update documentation as needed

4. **Test your changes**
   ```bash
   python app.py
   # Verify all functionality works
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Wait for code review

### Coding Standards

- Use **PEP 8** style guide for Python code
- Write descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Use SQL parameterized queries to prevent injection

### Reporting Bugs

If you find a bug, please open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Your environment details (OS, Python version, etc.)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

You are free to:
- ✅ Use the software for any purpose
- ✅ Study and modify the source code
- ✅ Share copies of the software
- ✅ Share modified versions

Under the conditions:
- 📋 Same license (copyleft)
- 📝 State changes made to the code
- 💾 Disclose source code
- 🔗 Include original license and copyright

See the [LICENSE](LICENSE) file for full details.

---

## 👥 Authors

**Fuat Karakaya**
- GitHub: [@FuatKarakaya](https://github.com/FuatKarakaya)
- Project Link: [Agricultural_Trade](https://github.com/FuatKarakaya/Agricultural_Trade)

---

## 📞 Support

Need help or have questions?

- 📧 Open an issue on [GitHub Issues](https://github.com/FuatKarakaya/Agricultural_Trade/issues)
- 💬 Start a discussion in [GitHub Discussions](https://github.com/FuatKarakaya/Agricultural_Trade/discussions)
- 📖 Check the [Wiki](https://github.com/FuatKarakaya/Agricultural_Trade/wiki) for detailed guides

---

## 🙏 Acknowledgments

- **FAO (Food and Agriculture Organization)** - Agricultural data standards and classifications
- **PostgreSQL Community** - Excellent documentation and robust database system
- **Flask Framework** - Lightweight and flexible web framework
- **Neon Database** - Serverless PostgreSQL hosting platform
- **Open Source Community** - For continuous inspiration and support

---

## 🔮 Future Enhancements

- [ ] Add data export to CSV/Excel functionality
- [ ] Implement advanced data visualization with interactive maps
- [ ] Add API documentation with Swagger/OpenAPI
- [ ] Create automated data import pipelines
- [ ] Implement caching for improved performance
- [ ] Add unit and integration tests
- [ ] Support multiple languages (i18n)
- [ ] Create mobile-responsive design improvements
- [ ] Add real-time data updates with WebSockets
- [ ] Implement machine learning models for price prediction

---

## 📊 Project Statistics

- **9 Database Tables** with full referential integrity
- **200+ Countries** in the reference database
- **100+ Agricultural Commodities** tracked
- **Multiple Years** of historical data (2010-2023)
- **17 Route Blueprints** for organized API structure
- **30+ HTML Templates** for comprehensive UI coverage

---

<div align="center">

**Built with ❤️ for agricultural data analysis and global food security research**

⭐ **Star this repository** if you find it helpful!

</div>

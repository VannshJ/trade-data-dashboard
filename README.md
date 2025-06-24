# Trade Data Intelligence Dashboard

A comprehensive full-stack dashboard that extracts international trade data from the UN Comtrade API, stores it in a local database, and provides an interactive web-based interface for visualizing and analyzing trade flows.

## 🌟 Features

- **Data Extraction**: Automated fetching from UN Comtrade API
- **Interactive Dashboard**: Modern web-based UI with multiple filters
- **Real-time Visualizations**: Charts showing trade trends, top partners, and product analysis
- **Comprehensive Filtering**: Filter by country, trade direction, HS code, and time period
- **Data Export**: Download filtered data as CSV
- **Sample Data Generation**: Built-in sample data for demonstration

## 🏗️ Architecture

```
trade-data-dashboard/
├── src/
│   ├── data_extractor.py      # UN Comtrade API data extraction
│   ├── database_manager.py    # SQLite database operations
│   └── app.py                 # Streamlit dashboard application
├── config/
│   └── config.py              # Configuration settings
├── data/
│   └── trade_data.db          # SQLite database (auto-created)
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- VS Code (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/trade-data-dashboard.git
cd trade-data-dashboard
```

2. **Create virtual environment**
```bash
python -m venv trade_env

# Activate (Windows)
trade_env\Scripts\activate

# Activate (macOS/Linux)
source trade_env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create directory structure**
```bash
mkdir -p data config src
```

5. **Set up environment variables** (Optional)
Create `.env` file:
```
COMTRADE_API_KEY=your_api_key_here
DATABASE_PATH=data/trade_data.db
```

### Running the Application

#### Step 1: Extract Data
```bash
cd src
python data_extractor.py
```
Choose option 1 for full extraction with sample data.

#### Step 2: Launch Dashboard
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## 📊 Dashboard Features

### Main Visualizations
1. **Summary Metrics**: Total records, trade value, countries, and product categories
2. **Trade Value Trends**: Time series analysis of trade flows
3. **Top Trading Partners**: Horizontal bar charts of leading importers/exporters
4. **Product Category Analysis**: Pie charts showing trade distribution by HS codes
5. **Import vs Export Comparison**: Trade flow direction analysis
6. **Detailed Data Table**: Sortable, filterable data grid with export functionality

### Available Filters
- **Year**: Filter by specific year or view all years
- **Reporter Country**: Select reporting country
- **Partner Country**: Select trading partner
- **Trade Flow**: Import, Export, or both
- **HS Code Category**: Product classification codes

## 🗃️ Database Schema

### Trade Data Table
- `year`: Trade year
- `month`: Trade month (if available)
- `reporter_code`: Reporting country code
- `reporter_name`: Reporting country name
- `partner_code`: Partner country code
- `partner_name`: Partner country name
- `trade_flow`: Import/Export direction
- `hs_code`: Harmonized System product code
- `hs_description`: Product description
- `trade_value`: Trade value in USD
- `quantity`: Trade quantity
- `unit`: Quantity unit

### Reference Tables
- **Countries**: Country codes, names, and regions
- **HS Codes**: Product classification codes and descriptions

## 🔧 Configuration

### API Configuration
The system supports both free and premium UN Comtrade API access:

- **Free Tier**: 100 requests/hour, limited data
- **Premium Tier**: 10,000 requests/hour, full access

### Data Sources
- **Primary**: UN Comtrade API (https://comtradeapi.un.org/)
- **Fallback**: Generated sample data for demonstration

### Supported Countries
USA, China, Germany, Japan, UK, France, India, Italy, Brazil, Canada, Russia, South Korea, Spain, Australia, Mexico, Indonesia, Netherlands, Saudi Arabia, Turkey, Switzerland

### Supported HS Codes
- 01: Live animals
- 02: Meat and edible meat offal
- 03: Fish and crustaceans
- 10: Cereals
- 27: Mineral fuels, oils and waxes
- 84: Nuclear reactors, boilers, machinery
- 85: Electrical machinery and equipment
- 87: Vehicles other than railway

## 🛠️ Development

### Code Structure

#### data_extractor.py
- Handles UN Comtrade API requests
- Implements rate limiting
- Processes and cleans raw data
- Generates sample data when needed

#### database_manager.py
- SQLite database operations
- Data insertion and retrieval
- Query optimization with indexes
- Summary statistics generation

#### app.py
- Streamlit web application
- Interactive visualizations with Plotly
- Real-time filtering and data updates
- Export functionality

#### config.py
- Centralized configuration management
- API settings and rate limits
- Default parameters and mappings

### VS Code Setup
1. Open project in VS Code: `code .`
2. Install Python extension
3. Select interpreter: `Ctrl/Cmd + Shift + P` → "Python: Select Interpreter"
4. Choose the virtual environment interpreter

### Testing
```bash
# Test database operations
python src/database_manager.py

# Test data extraction
python src/data_extractor.py

# Run dashboard
streamlit run src/app.py
```

## 📈 Usage Examples

### Extract Specific Country Data
```python
from data_extractor import ComtradeDataExtractor

extractor = ComtradeDataExtractor()
# Extract USA trade data for 2023
extractor.extract_specific_data('USA', year=2023)
```

### Query Database
```python
from database_manager import DatabaseManager

db = DatabaseManager()
# Get all trade data for Germany
data = db.get_trade_data({'reporter_code': 'DEU'})
```

### Dashboard Filters
- Select "Germany" as Reporter Country
- Choose "2023" as Year
- Filter by "Import" trade flow
- View automotive sector (HS Code 87)

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip list`

2. **API Rate Limits**
   - Free tier: 100 requests/hour
   - Add delays between requests
   - Consider using sample data for development

3. **Database Errors**
   - Check file permissions in `data/` directory
   - Ensure SQLite is available: `python -c "import sqlite3; print('OK')"`

4. **Dashboard Not Loading**
   - Verify Streamlit installation: `streamlit --version`
   - Check port availability (default: 8501)
   - Run data extraction first if no data available

### Error Messages

- **"No data available"**: Run data extractor first
- **"Rate limit exceeded"**: Wait for rate limit reset
- **"Database connection failed"**: Check file permissions

## 📝 API Usage Notes

- Free UN Comtrade API has usage limits
- Some endpoints require registration
- Data availability varies by country and time period
- Historical data may be incomplete

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is for educational purposes. Please check UN Comtrade API terms of service for data usage restrictions.

## 🔗 Resources

- [UN Comtrade Database](https://comtrade.un.org/)
- [UN Comtrade API Documentation](https://comtradeapi.un.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
"""
Configuration file for Trade Data Intelligence Dashboard
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
COMTRADE_API_KEY = os.getenv('COMTRADE_API_KEY', '')
BASE_URL = "https://comtradeapi.un.org/data/v1/get/"
FREE_API_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/"

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', '../data/trade_data.db')

# API Rate Limits
RATE_LIMIT_FREE = 100  # requests per hour
RATE_LIMIT_PREMIUM = 10000  # requests per hour

# Data Extraction Settings
DEFAULT_COUNTRIES = ['USA', 'CHN', 'DEU', 'JPN', 'GBR', 'FRA', 'IND', 'ITA', 'BRA', 'CAN']
DEFAULT_YEARS = [2020, 2021, 2022, 2023]
DEFAULT_HS_CODES = ['01', '02', '03', '10', '27', '84', '85', '87']  # Sample HS codes

# Trade Flow Codes
TRADE_FLOWS = {
    'M': 'Import',
    'X': 'Export',
    'Re-Import': 'Re-Import',
    'Re-Export': 'Re-Export'
}

# Common HS Code Categories for dashboard
HS_CATEGORIES = {
    '01': 'Live animals',
    '02': 'Meat and edible meat offal',
    '03': 'Fish and crustaceans',
    '04': 'Dairy produce',
    '05': 'Products of animal origin',
    '06': 'Live trees and other plants',
    '07': 'Edible vegetables',
    '08': 'Edible fruit and nuts',
    '09': 'Coffee, tea, mate and spices',
    '10': 'Cereals',
    '27': 'Mineral fuels, oils and waxes',
    '84': 'Nuclear reactors, boilers, machinery',
    '85': 'Electrical machinery and equipment',
    '87': 'Vehicles other than railway'
}

# Dashboard Configuration
DASHBOARD_TITLE = "Trade Data Intelligence Dashboard"
DASHBOARD_SUBTITLE = "International Trade Flow Analysis using UN Comtrade Data"

# Chart Colors
CHART_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]
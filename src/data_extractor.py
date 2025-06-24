"""
Data Extractor for UN Comtrade API
Fetches international trade data and stores it in the database
"""

import requests
import pandas as pd
import time
import logging
from datetime import datetime
import json
import sys
import os

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from config import *
from database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComtradeDataExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key or COMTRADE_API_KEY
        self.base_url = BASE_URL
        self.free_api_url = FREE_API_URL
        self.db_manager = DatabaseManager()
        self.request_count = 0
        self.session = requests.Session()
        
        # Rate limiting
        self.max_requests_per_hour = RATE_LIMIT_PREMIUM if self.api_key else RATE_LIMIT_FREE
        self.requests_made = []
    
    def check_rate_limit(self):
        """Check if we're within rate limits"""
        now = datetime.now()
        # Remove requests older than 1 hour
        self.requests_made = [req_time for req_time in self.requests_made 
                             if (now - req_time).seconds < 3600]
        
        if len(self.requests_made) >= self.max_requests_per_hour:
            logger.warning("Rate limit reached. Waiting...")
            time.sleep(3600)  # Wait 1 hour
            self.requests_made = []
    
    def make_request(self, url, params=None):
        """Make API request with rate limiting"""
        self.check_rate_limit()
        
        try:
            headers = {}
            if self.api_key:
                headers['Ocp-Apim-Subscription-Key'] = self.api_key
            
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            self.requests_made.append(datetime.now())
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
    
    def get_country_codes(self):
        """Get country codes and names"""
        try:
            # Use a simplified approach for country codes
            countries_data = [
                ('USA', 'United States of America', 'Americas'),
                ('CHN', 'China', 'Asia'),
                ('DEU', 'Germany', 'Europe'),
                ('JPN', 'Japan', 'Asia'),
                ('GBR', 'United Kingdom', 'Europe'),
                ('FRA', 'France', 'Europe'),
                ('IND', 'India', 'Asia'),
                ('ITA', 'Italy', 'Europe'),
                ('BRA', 'Brazil', 'Americas'),
                ('CAN', 'Canada', 'Americas'),
                ('RUS', 'Russian Federation', 'Europe'),
                ('KOR', 'Republic of Korea', 'Asia'),
                ('ESP', 'Spain', 'Europe'),
                ('AUS', 'Australia', 'Oceania'),
                ('MEX', 'Mexico', 'Americas'),
                ('IDN', 'Indonesia', 'Asia'),
                ('NLD', 'Netherlands', 'Europe'),
                ('SAU', 'Saudi Arabia', 'Asia'),
                ('TUR', 'Turkey', 'Asia'),
                ('CHE', 'Switzerland', 'Europe')
            ]
            
            self.db_manager.insert_countries(countries_data)
            logger.info("Country codes updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating country codes: {e}")
    
    def get_hs_codes(self):
        """Get HS codes and descriptions"""
        try:
            hs_codes_data = [
                (code, description, 'Various') 
                for code, description in HS_CATEGORIES.items()
            ]
            
            self.db_manager.insert_hs_codes(hs_codes_data)
            logger.info("HS codes updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating HS codes: {e}")
    
    def extract_trade_data_free_api(self, reporter='USA', partner='all', year=2022, hs_code='all'):
        """Extract trade data using free API endpoint"""
        try:
            # Construct URL for free API
            # Format: /public/v1/preview/C/A/{freq}/{clCode}/{period}/{reporterCode}/{cmdCode}/{partnerCode}/
            url = f"https://comtradeapi.un.org/public/v1/preview/C/A/A/{hs_code}/{year}/{reporter}/{partner}/"
            
            logger.info(f"Fetching data from: {url}")
            
            response = self.make_request(url)
            
            if response and 'data' in response:
                data_records = []
                
                for record in response['data']:
                    try:
                        data_record = (
                            record.get('period', year),  # year
                            None,  # month (annual data)
                            record.get('reporterCode', reporter),  # reporter_code
                            record.get('reporterDesc', ''),  # reporter_name
                            record.get('partnerCode', ''),  # partner_code
                            record.get('partnerDesc', ''),  # partner_name
                            record.get('flowDesc', 'Import'),  # trade_flow (Import/Export)
                            record.get('cmdCode', hs_code),  # hs_code
                            record.get('cmdDesc', ''),  # hs_description
                            float(record.get('tradeValue', 0)) if record.get('tradeValue') else None,  # trade_value
                            float(record.get('qty', 0)) if record.get('qty') else None,  # quantity
                            record.get('qtyUnitAbbr', '')  # unit
                        )
                        data_records.append(data_record)
                        
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error processing record: {e}")
                        continue
                
                if data_records:
                    self.db_manager.insert_trade_data(data_records)
                    logger.info(f"Successfully extracted {len(data_records)} records")
                    return len(data_records)
                else:
                    logger.warning("No valid data records found")
                    return 0
            else:
                logger.warning("No data returned from API")
                return 0
                
        except Exception as e:
            logger.error(f"Error extracting trade data: {e}")
            return 0
    
    def generate_sample_data(self):
        """Generate sample trade data for demonstration"""
        try:
            import random
            
            countries = ['USA', 'CHN', 'DEU', 'JPN', 'GBR', 'FRA', 'IND', 'ITA', 'BRA', 'CAN']
            hs_codes = list(HS_CATEGORIES.keys())
            trade_flows = ['Import', 'Export']
            years = [2020, 2021, 2022, 2023]
            
            sample_data = []
            
            for _ in range(500):  # Generate 500 sample records
                reporter = random.choice(countries)
                partner = random.choice([c for c in countries if c != reporter])
                hs_code = random.choice(hs_codes)
                trade_flow = random.choice(trade_flows)
                year = random.choice(years)
                
                # Generate realistic trade values
                base_value = random.uniform(1000000, 1000000000)  # 1M to 1B USD
                trade_value = round(base_value, 2)
                quantity = round(random.uniform(1000, 100000), 2)
                
                record = (
                    year,  # year
                    random.randint(1, 12),  # month
                    reporter,  # reporter_code
                    next((name for code, name, _ in [
                        ('USA', 'United States of America', 'Americas'),
                        ('CHN', 'China', 'Asia'),
                        ('DEU', 'Germany', 'Europe'),
                        ('JPN', 'Japan', 'Asia'),
                        ('GBR', 'United Kingdom', 'Europe'),
                        ('FRA', 'France', 'Europe'),
                        ('IND', 'India', 'Asia'),
                        ('ITA', 'Italy', 'Europe'),
                        ('BRA', 'Brazil', 'Americas'),
                        ('CAN', 'Canada', 'Americas')
                    ] if code == reporter), reporter),  # reporter_name
                    partner,  # partner_code
                    next((name for code, name, _ in [
                        ('USA', 'United States of America', 'Americas'),
                        ('CHN', 'China', 'Asia'),
                        ('DEU', 'Germany', 'Europe'),
                        ('JPN', 'Japan', 'Asia'),
                        ('GBR', 'United Kingdom', 'Europe'),
                        ('FRA', 'France', 'Europe'),
                        ('IND', 'India', 'Asia'),
                        ('ITA', 'Italy', 'Europe'),
                        ('BRA', 'Brazil', 'Americas'),
                        ('CAN', 'Canada', 'Americas')
                    ] if code == partner), partner),  # partner_name
                    trade_flow,  # trade_flow
                    hs_code,  # hs_code
                    HS_CATEGORIES.get(hs_code, 'Unknown'),  # hs_description
                    trade_value,  # trade_value
                    quantity,  # quantity
                    'KG'  # unit
                )
                sample_data.append(record)
            
            self.db_manager.insert_trade_data(sample_data)
            logger.info(f"Generated {len(sample_data)} sample records")
            return len(sample_data)
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            return 0
    
    def run_full_extraction(self):
        """Run full data extraction process"""
        try:
            logger.info("Starting trade data extraction...")
            
            # Update reference data
            self.get_country_codes()
            self.get_hs_codes()
            
            total_records = 0
            
            # Try to extract real data for a few countries and years
            for reporter in DEFAULT_COUNTRIES[:3]:  # Limit to first 3 countries to avoid rate limits
                for year in [2022, 2023]:  # Recent years
                    try:
                        records = self.extract_trade_data_free_api(
                            reporter=reporter, 
                            year=year, 
                            hs_code='TOTAL'
                        )
                        total_records += records
                        
                        # Add delay between requests
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error extracting data for {reporter} {year}: {e}")
                        continue
            
            # If real data extraction didn't work well, generate sample data
            if total_records < 100:
                logger.info("Limited real data extracted, generating sample data...")
                sample_records = self.generate_sample_data()
                total_records += sample_records
            
            logger.info(f"Data extraction completed. Total records: {total_records}")
            
            # Print summary statistics
            stats = self.db_manager.get_summary_stats()
            print("\n=== EXTRACTION SUMMARY ===")
            print(f"Total Records: {stats.get('total_records', 0)}")
            print(f"Year Range: {stats.get('year_range', 'N/A')}")
            print(f"Unique Reporters: {stats.get('unique_reporters', 0)}")
            print(f"Unique Partners: {stats.get('unique_partners', 0)}")
            print(f"Total Trade Value: ${stats.get('total_trade_value', 0):,.2f}")
            print("=========================\n")
            
            return total_records
            
        except Exception as e:
            logger.error(f"Error in full extraction: {e}")
            return 0
    
    def extract_specific_data(self, reporter_code, partner_code='all', year=2023, hs_code='TOTAL'):
        """Extract specific trade data based on parameters"""
        try:
            logger.info(f"Extracting data for {reporter_code} -> {partner_code}, Year: {year}, HS: {hs_code}")
            
            records = self.extract_trade_data_free_api(
                reporter=reporter_code,
                partner=partner_code,
                year=year,
                hs_code=hs_code
            )
            
            return records
            
        except Exception as e:
            logger.error(f"Error extracting specific data: {e}")
            return 0
    
    def update_recent_data(self):
        """Update with most recent available data"""
        try:
            current_year = datetime.now().year
            recent_years = [current_year - 1, current_year - 2]  # Last 2 years
            
            total_records = 0
            
            for year in recent_years:
                for reporter in DEFAULT_COUNTRIES[:5]:  # Top 5 countries
                    try:
                        records = self.extract_trade_data_free_api(
                            reporter=reporter,
                            year=year,
                            hs_code='TOTAL'
                        )
                        total_records += records
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"Error updating data for {reporter} {year}: {e}")
                        continue
            
            logger.info(f"Updated {total_records} recent records")
            return total_records
            
        except Exception as e:
            logger.error(f"Error updating recent data: {e}")
            return 0

def main():
    """Main function to run data extraction"""
    print("=== UN Comtrade Data Extractor ===")
    print("1. Full Extraction (with sample data)")
    print("2. Update Recent Data")
    print("3. Extract Specific Country Data")
    print("4. Generate Sample Data Only")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    extractor = ComtradeDataExtractor()
    
    if choice == '1':
        print("\nRunning full extraction...")
        extractor.run_full_extraction()
        
    elif choice == '2':
        print("\nUpdating recent data...")
        extractor.update_recent_data()
        
    elif choice == '3':
        reporter = input("Enter reporter country code (e.g., USA): ").strip().upper()
        year = input("Enter year (e.g., 2023): ").strip()
        
        try:
            year = int(year)
            print(f"\nExtracting data for {reporter}, year {year}...")
            extractor.extract_specific_data(reporter, year=year)
        except ValueError:
            print("Invalid year format")
            
    elif choice == '4':
        print("\nGenerating sample data...")
        extractor.generate_sample_data()
        
    else:
        print("Invalid choice. Running full extraction...")
        extractor.run_full_extraction()
    
    print("\nExtraction completed!")

if __name__ == "__main__":
    main()
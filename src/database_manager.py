"""
Database Manager for Trade Data Intelligence Dashboard
Handles SQLite database operations for storing and retrieving trade data
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='../data/trade_data.db'):
        self.db_path = db_path
        self.ensure_directory_exists()
        self.init_database()
    
    def ensure_directory_exists(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create trade data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trade_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        year INTEGER,
                        month INTEGER,
                        reporter_code VARCHAR(3),
                        reporter_name VARCHAR(100),
                        partner_code VARCHAR(3),
                        partner_name VARCHAR(100),
                        trade_flow VARCHAR(20),
                        hs_code VARCHAR(10),
                        hs_description TEXT,
                        trade_value REAL,
                        quantity REAL,
                        unit VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create countries reference table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS countries (
                        code VARCHAR(3) PRIMARY KEY,
                        name VARCHAR(100),
                        region VARCHAR(50)
                    )
                ''')
                
                # Create HS codes reference table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS hs_codes (
                        code VARCHAR(10) PRIMARY KEY,
                        description TEXT,
                        section VARCHAR(100)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON trade_data(year)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reporter ON trade_data(reporter_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_partner ON trade_data(partner_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_hs_code ON trade_data(hs_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_flow ON trade_data(trade_flow)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_trade_data(self, data_list):
        """Insert trade data records"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                    INSERT OR REPLACE INTO trade_data 
                    (year, month, reporter_code, reporter_name, partner_code, partner_name,
                     trade_flow, hs_code, hs_description, trade_value, quantity, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data_list)
                
                conn.commit()
                logger.info(f"Inserted {len(data_list)} trade data records")
                
        except Exception as e:
            logger.error(f"Error inserting trade data: {e}")
            raise
    
    def insert_countries(self, countries_data):
        """Insert countries reference data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                    INSERT OR REPLACE INTO countries (code, name, region)
                    VALUES (?, ?, ?)
                ''', countries_data)
                
                conn.commit()
                logger.info(f"Inserted {len(countries_data)} country records")
                
        except Exception as e:
            logger.error(f"Error inserting countries: {e}")
            raise
    
    def insert_hs_codes(self, hs_codes_data):
        """Insert HS codes reference data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany('''
                    INSERT OR REPLACE INTO hs_codes (code, description, section)
                    VALUES (?, ?, ?)
                ''', hs_codes_data)
                
                conn.commit()
                logger.info(f"Inserted {len(hs_codes_data)} HS code records")
                
        except Exception as e:
            logger.error(f"Error inserting HS codes: {e}")
            raise
    
    def get_trade_data(self, filters=None):
        """Get trade data with optional filters"""
        try:
            query = '''
                SELECT 
                    year, month, reporter_code, reporter_name, 
                    partner_code, partner_name, trade_flow,
                    hs_code, hs_description, trade_value, quantity, unit
                FROM trade_data
                WHERE 1=1
            '''
            params = []
            
            if filters:
                if 'year' in filters and filters['year']:
                    query += ' AND year = ?'
                    params.append(filters['year'])
                
                if 'reporter_code' in filters and filters['reporter_code']:
                    query += ' AND reporter_code = ?'
                    params.append(filters['reporter_code'])
                
                if 'partner_code' in filters and filters['partner_code']:
                    query += ' AND partner_code = ?'
                    params.append(filters['partner_code'])
                
                if 'trade_flow' in filters and filters['trade_flow']:
                    query += ' AND trade_flow = ?'
                    params.append(filters['trade_flow'])
                
                if 'hs_code' in filters and filters['hs_code']:
                    query += ' AND hs_code LIKE ?'
                    params.append(f"{filters['hs_code']}%")
            
            query += ' ORDER BY year DESC, trade_value DESC'
            
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                
            return df
            
        except Exception as e:
            logger.error(f"Error getting trade data: {e}")
            return pd.DataFrame()
    
    def get_countries(self):
        """Get all countries"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query('SELECT * FROM countries ORDER BY name', conn)
            return df
        except Exception as e:
            logger.error(f"Error getting countries: {e}")
            return pd.DataFrame()
    
    def get_hs_codes(self):
        """Get all HS codes"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query('SELECT * FROM hs_codes ORDER BY code', conn)
            return df
        except Exception as e:
            logger.error(f"Error getting HS codes: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self):
        """Get summary statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Total records
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM trade_data')
                stats['total_records'] = cursor.fetchone()[0]
                
                # Year range
                cursor.execute('SELECT MIN(year), MAX(year) FROM trade_data')
                min_year, max_year = cursor.fetchone()
                stats['year_range'] = f"{min_year}-{max_year}" if min_year else "No data"
                
                # Unique countries
                cursor.execute('SELECT COUNT(DISTINCT reporter_code) FROM trade_data')
                stats['unique_reporters'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT partner_code) FROM trade_data')
                stats['unique_partners'] = cursor.fetchone()[0]
                
                # Total trade value
                cursor.execute('SELECT SUM(trade_value) FROM trade_data WHERE trade_value IS NOT NULL')
                total_value = cursor.fetchone()[0]
                stats['total_trade_value'] = total_value if total_value else 0
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return {}
    
    def get_top_traders(self, trade_flow='Import', limit=10):
        """Get top trading countries by value"""
        try:
            query = '''
                SELECT 
                    reporter_name,
                    SUM(trade_value) as total_value,
                    COUNT(*) as record_count
                FROM trade_data 
                WHERE trade_flow = ? AND trade_value IS NOT NULL
                GROUP BY reporter_code, reporter_name
                ORDER BY total_value DESC
                LIMIT ?
            '''
            
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=[trade_flow, limit])
                
            return df
            
        except Exception as e:
            logger.error(f"Error getting top traders: {e}")
            return pd.DataFrame()
    
    def get_trade_trends(self, country_code=None):
        """Get trade trends over time"""
        try:
            if country_code:
                query = '''
                    SELECT 
                        year,
                        trade_flow,
                        SUM(trade_value) as total_value
                    FROM trade_data 
                    WHERE reporter_code = ? AND trade_value IS NOT NULL
                    GROUP BY year, trade_flow
                    ORDER BY year
                '''
                params = [country_code]
            else:
                query = '''
                    SELECT 
                        year,
                        trade_flow,
                        SUM(trade_value) as total_value
                    FROM trade_data 
                    WHERE trade_value IS NOT NULL
                    GROUP BY year, trade_flow
                    ORDER BY year
                '''
                params = []
            
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                
            return df
            
        except Exception as e:
            logger.error(f"Error getting trade trends: {e}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, days_old=30):
        """Clean up old data records"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM trade_data 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old records")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

if __name__ == "__main__":
    # Test the database manager
    db = DatabaseManager()
    stats = db.get_summary_stats()
    print("Database Summary:", stats)
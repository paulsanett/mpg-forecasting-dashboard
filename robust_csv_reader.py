"""
Robust CSV Reader for Historic Booking Data
Handles all the common issues with reading the daily updated CSV file
"""

import csv
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class RobustCSVReader:
    """
    Robust CSV reader that handles all common issues with the Historic Booking Data file
    """
    
    def __init__(self, filename: str = "HIstoric Booking Data.csv"):
        self.filename = filename
        self.normalized_data = []
        self.field_mapping = {}
        
    def detect_field_names(self, headers: List[str]) -> Dict[str, str]:
        """
        Detect and map actual field names to standardized names
        Uses column positions as primary method, name validation as backup
        """
        field_mapping = {}
        
        # Normalize headers by removing BOM, extra spaces, and special characters
        normalized_headers = []
        for header in headers:
            # Remove BOM (Byte Order Mark)
            clean_header = header.replace('\ufeff', '')
            # Strip whitespace
            clean_header = clean_header.strip()
            normalized_headers.append(clean_header)
        
        print(f"📋 Total columns detected: {len(headers)}")
        
        # PRIMARY METHOD: Map by column positions (Excel columns)
        # Column positions are 0-indexed, so H=7, N=13, T=19, Z=25, AB=27, AJ=35
        # CORRECTED MAPPINGS per user specification 2025-08-06
        column_positions = {
            6: 'gpn_units',        # Column G - Grant Park North Units
            7: 'gpn_revenue',      # Column H - Grant Park North Revenue
            12: 'gps_units',       # Column M - Grant Park South Units  
            13: 'gps_revenue',     # Column N - Grant Park South Revenue
            18: 'lakeside_units',  # Column S - Lakeside Units
            19: 'lakeside_revenue', # Column T - Lakeside Revenue
            24: 'millennium_units', # Column Y - Millennium Park Units
            25: 'millennium_revenue', # Column Z - Millennium Park Revenue
            26: 'online_units',    # Column AA - Online Units
            27: 'online_revenue',  # Column AB - Online Revenue (CORRECTED from AI)
            31: 'total_units',     # Column AF - Total Units
            35: 'total_revenue',   # Column AJ - Total Revenue
            39: 'avg_reservation_value', # Column AN - Average Reservation Value
            44: 'gas_price',       # Column AS - Gas Price (predictor) - "$ of Gas"
            45: 'notes'            # Column AT - Notes (temperature, events)
        }
        
        # Map by position first
        for position, field_key in column_positions.items():
            if position < len(headers):
                field_mapping[field_key] = headers[position]
                print(f"📍 Position {position+1} ({chr(65 + position % 26) if position < 26 else 'A' + chr(65 + position - 26)}): {field_key} -> '{headers[position].strip()}'")
        
        # BACKUP METHOD: Validate by name and find missing columns
        name_validations = {
            'gpn_revenue': ['Grant Park North Total Flex Daily', 'Grant Park North'],
            'gps_revenue': ['Grant Park South Total Flex Daily', 'Grant Park South'],
            'lakeside_revenue': ['Lakeside Total Flex Daily', 'Lakeside'],
            'millennium_revenue': ['Millennium Park Total Flex Daily', 'Millennium'],
            'flex_daily_revenue': ['Flex Daily Revenue'],
            'transient_revenue': ['Transient Revenue'],
            'online_revenue': ['Online Revenue'],
            'total_revenue': ['Total Revenue']
        }
        
        # Check if position-based mapping is correct by validating names
        for field_key, validation_terms in name_validations.items():
            if field_key in field_mapping:
                header_name = field_mapping[field_key].strip()
                # Check if any validation term matches
                is_valid = any(term in header_name for term in validation_terms)
                if is_valid:
                    print(f"✅ {field_key}: Position mapping validated - '{header_name}'")
                else:
                    print(f"⚠️  {field_key}: Position mapping questionable - '{header_name}'")
                    # Try to find by name as backup
                    for i, header in enumerate(headers):
                        if any(term in header.strip() for term in validation_terms):
                            field_mapping[field_key] = headers[i]
                            print(f"🔄 {field_key}: Found by name at position {i+1} - '{header.strip()}'")
                            break
        
        # Find date and day of week fields (these can vary in position)
        for i, header in enumerate(normalized_headers):
            header_lower = header.lower()
            
            # Date field variations
            if any(date_term in header_lower for date_term in ['date', 'day']):
                if 'week' not in header_lower:  # Avoid "Day of Week"
                    field_mapping['date'] = headers[i]
                    print(f"📅 Date field found at position {i+1}: '{header}'")
            
            # Day of week field
            if 'day of week' in header_lower or 'dow' in header_lower:
                field_mapping['day_of_week'] = headers[i]
                print(f"📅 Day of week field found at position {i+1}: '{header}'")
        
        return field_mapping
    
    def clean_currency_value(self, value: str) -> float:
        """
        Clean currency values - remove $, commas, spaces
        Handle various formats: $1,234.56, 1234.56, 1,234, etc.
        """
        if not value or value.strip() == '':
            return 0.0
        
        try:
            # Remove currency symbols, commas, and extra spaces
            clean_value = str(value).replace('$', '').replace(',', '').strip()
            
            # Handle empty or non-numeric values
            if clean_value == '' or clean_value.lower() in ['n/a', 'na', 'null', 'none']:
                return 0.0
            
            return float(clean_value)
        except (ValueError, TypeError):
            print(f"⚠️ Warning: Could not parse currency value: '{value}'")
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date strings in various formats
        Handles: MM/DD/YY, MM/DD/YYYY, YYYY-MM-DD, etc.
        """
        if not date_str or date_str.strip() == '':
            return None
        
        date_str = date_str.strip()
        
        # Common date formats to try
        date_formats = [
            '%m/%d/%y',      # 08/05/25
            '%m/%d/%Y',      # 08/05/2025
            '%Y-%m-%d',      # 2025-08-05
            '%d/%m/%y',      # 05/08/25 (European)
            '%d/%m/%Y',      # 05/08/2025 (European)
            '%m-%d-%y',      # 08-05-25
            '%m-%d-%Y',      # 08-05-2025
        ]
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                
                # Handle 2-digit years (assume 20xx for years < 50, 19xx for years >= 50)
                if parsed_date.year < 1950:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                elif parsed_date.year < 2000:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                
                return parsed_date
            except ValueError:
                continue
        
        print(f"⚠️ Warning: Could not parse date: '{date_str}'")
        return None
    
    def wait_for_file_access(self, max_attempts: int = 5) -> bool:
        """
        Wait for file to be accessible (not locked by Excel or Dropbox sync)
        """
        for attempt in range(max_attempts):
            try:
                # Try to open file in read mode
                with open(self.filename, 'r') as f:
                    f.readline()  # Try to read first line
                return True
            except (PermissionError, IOError) as e:
                print(f"⏳ Attempt {attempt + 1}: File access blocked, waiting 2 seconds...")
                time.sleep(2)
        
        print(f"❌ Could not access file after {max_attempts} attempts")
        return False
    
    def read_csv_robust(self) -> List[Dict]:
        """
        Robust CSV reading with error handling and data cleaning
        """
        print(f"📁 Reading CSV file: {self.filename}")
        
        # Check if file exists
        if not os.path.exists(self.filename):
            print(f"❌ File not found: {self.filename}")
            return []
        
        # Wait for file access
        if not self.wait_for_file_access():
            print("❌ Could not access file - it may be open in Excel or syncing")
            return []
        
        try:
            normalized_data = []
            
            with open(self.filename, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                # Try common delimiters
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Detect field mapping from headers
                headers = reader.fieldnames
                if not headers:
                    print("❌ No headers found in CSV file")
                    return []
                
                self.field_mapping = self.detect_field_names(headers)
                print(f"✅ Detected field mapping: {self.field_mapping}")
                
                # Process each row
                row_count = 0
                valid_rows = 0
                
                for row in reader:
                    row_count += 1
                    
                    # Extract and clean data using field mapping
                    try:
                        # Get date
                        date_field = self.field_mapping.get('date')
                        if not date_field or not row.get(date_field):
                            continue
                        
                        parsed_date = self.parse_date(row[date_field])
                        if not parsed_date:
                            continue
                        
                        # Get revenue
                        revenue_field = self.field_mapping.get('total_revenue')
                        if not revenue_field or not row.get(revenue_field):
                            continue
                        
                        revenue = self.clean_currency_value(row[revenue_field])
                        if revenue <= 0:
                            continue
                        
                        # Get day of week
                        dow_field = self.field_mapping.get('day_of_week')
                        day_of_week = row.get(dow_field, '').strip() if dow_field else parsed_date.strftime('%A')
                        
                        # Create normalized record
                        normalized_record = {
                            'date': parsed_date,
                            'date_str': parsed_date.strftime('%Y-%m-%d'),
                            'day_of_week': day_of_week,
                            'total_revenue': revenue,
                            'raw_row': row  # Keep original for debugging
                        }
                        
                        # Add individual garage revenues if available
                        for garage_key in ['gpn_revenue', 'gps_revenue', 'lakeside_revenue', 'millennium_revenue', 'online_revenue']:
                            field = self.field_mapping.get(garage_key)
                            if field and row.get(field):
                                normalized_record[garage_key] = self.clean_currency_value(row[field])
                        
                        # Add Flex Daily and Transient revenues if available
                        for revenue_key in ['flex_daily_revenue', 'transient_revenue']:
                            field = self.field_mapping.get(revenue_key)
                            if field and row.get(field):
                                normalized_record[revenue_key] = self.clean_currency_value(row[field])
                        
                        normalized_data.append(normalized_record)
                        valid_rows += 1
                        
                    except Exception as e:
                        print(f"⚠️ Warning: Error processing row {row_count}: {e}")
                        continue
                
                print(f"✅ Successfully processed {valid_rows} valid rows out of {row_count} total rows")
                
                # Sort by date
                normalized_data.sort(key=lambda x: x['date'])
                
                self.normalized_data = normalized_data
                return normalized_data
                
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return []
    
    def get_recent_data(self, days: int = 30) -> List[Dict]:
        """Get data from the last N days"""
        if not self.normalized_data:
            self.read_csv_robust()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = [record for record in self.normalized_data if record['date'] >= cutoff_date]
        
        print(f"📊 Found {len(recent_data)} records in the last {days} days")
        return recent_data
    
    def find_date_data(self, target_date: str) -> Optional[Dict]:
        """Find data for a specific date (YYYY-MM-DD format)"""
        if not self.normalized_data:
            self.read_csv_robust()
        
        for record in self.normalized_data:
            if record['date_str'] == target_date:
                return record
        
        print(f"⚠️ No data found for date: {target_date}")
        return None
    
    def generate_data_summary(self) -> str:
        """Generate a summary of the loaded data"""
        if not self.normalized_data:
            self.read_csv_robust()
        
        if not self.normalized_data:
            return "❌ No data loaded"
        
        summary = []
        summary.append(f"📊 DATA SUMMARY")
        summary.append(f"=" * 50)
        summary.append(f"Total records: {len(self.normalized_data)}")
        
        # Date range
        first_date = self.normalized_data[0]['date'].strftime('%Y-%m-%d')
        last_date = self.normalized_data[-1]['date'].strftime('%Y-%m-%d')
        summary.append(f"Date range: {first_date} to {last_date}")
        
        # Revenue statistics
        revenues = [record['total_revenue'] for record in self.normalized_data]
        avg_revenue = sum(revenues) / len(revenues)
        max_revenue = max(revenues)
        min_revenue = min(revenues)
        
        summary.append(f"Average daily revenue: ${avg_revenue:,.0f}")
        summary.append(f"Maximum daily revenue: ${max_revenue:,.0f}")
        summary.append(f"Minimum daily revenue: ${min_revenue:,.0f}")
        
        # Recent data
        recent_data = self.get_recent_data(7)
        if recent_data:
            summary.append(f"\nLast 7 days:")
            for record in recent_data[-7:]:
                summary.append(f"  {record['date_str']} ({record['day_of_week']}): ${record['total_revenue']:,.0f}")
        
        return "\n".join(summary)

# Example usage and testing
if __name__ == "__main__":
    reader = RobustCSVReader()
    
    print("🧪 TESTING ROBUST CSV READER")
    print("=" * 50)
    
    # Test reading the file
    data = reader.read_csv_robust()
    
    if data:
        # Generate summary
        print("\n" + reader.generate_data_summary())
        
        # Test finding specific date (Monday 8/4)
        print(f"\n🔍 SEARCHING FOR MONDAY 8/4/2025:")
        monday_data = reader.find_date_data('2025-08-04')
        if monday_data:
            print(f"✅ Found: ${monday_data['total_revenue']:,.2f}")
        else:
            print("❌ Not found")
        
        # Test recent data
        print(f"\n📅 RECENT DATA (last 10 days):")
        recent = reader.get_recent_data(10)
        for record in recent[-10:]:
            print(f"  {record['date_str']}: ${record['total_revenue']:,.0f}")
    else:
        print("❌ Failed to read CSV data")

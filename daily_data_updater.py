"""
Daily Data Updater - Clean way to add new daily revenue data
Avoids the massive file bloat and formatting issues
"""

import csv
import os
from datetime import datetime
from robust_csv_reader import RobustCSVReader

class DailyDataUpdater:
    """
    Clean, efficient way to update daily revenue data
    """
    
    def __init__(self, clean_filename: str = "Historic_Booking_Data_Clean.csv"):
        self.clean_filename = clean_filename
        self.original_filename = "HIstoric Booking Data.csv"
        
    def create_clean_file_from_original(self):
        """
        Create a clean CSV file from the original bloated file
        One-time operation to fix the file structure
        """
        print("🧹 Creating clean CSV file from original...")
        
        # Use robust reader to get clean data
        reader = RobustCSVReader(self.original_filename)
        clean_data = reader.read_csv_robust()
        
        if not clean_data:
            print("❌ No data to clean")
            return False
        
        # Write clean CSV with proper headers
        with open(self.clean_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write clean headers
            headers = ['Date', 'Day_of_Week', 'Total_Revenue', 'GPN_Revenue', 'GPS_Revenue', 'Lakeside_Revenue', 'Millennium_Revenue']
            writer.writerow(headers)
            
            # Write clean data
            for record in clean_data:
                row = [
                    record['date_str'],
                    record['day_of_week'],
                    f"{record['total_revenue']:.2f}",
                    f"{record.get('gpn_revenue', 0):.2f}",
                    f"{record.get('gps_revenue', 0):.2f}",
                    f"{record.get('lakeside_revenue', 0):.2f}",
                    f"{record.get('millennium_revenue', 0):.2f}"
                ]
                writer.writerow(row)
        
        print(f"✅ Clean file created: {self.clean_filename}")
        print(f"📊 {len(clean_data)} records written")
        print(f"💾 File size reduced from ~{os.path.getsize(self.original_filename)/1024/1024:.1f}MB to ~{os.path.getsize(self.clean_filename)/1024/1024:.1f}MB")
        
        return True
    
    def add_daily_data(self, date_str: str, day_of_week: str, total_revenue: float, 
                      gpn_revenue: float = 0, gps_revenue: float = 0, 
                      lakeside_revenue: float = 0, millennium_revenue: float = 0):
        """
        Add a single day's data to the clean file
        """
        print(f"📅 Adding data for {date_str}...")
        
        # Check if clean file exists
        if not os.path.exists(self.clean_filename):
            print("🧹 Clean file doesn't exist, creating it first...")
            if not self.create_clean_file_from_original():
                return False
        
        # Check if date already exists
        existing_dates = set()
        try:
            with open(self.clean_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_dates.add(row['Date'])
        except FileNotFoundError:
            pass
        
        if date_str in existing_dates:
            print(f"⚠️ Date {date_str} already exists in the file")
            return False
        
        # Append new data
        with open(self.clean_filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            row = [
                date_str,
                day_of_week,
                f"{total_revenue:.2f}",
                f"{gpn_revenue:.2f}",
                f"{gps_revenue:.2f}",
                f"{lakeside_revenue:.2f}",
                f"{millennium_revenue:.2f}"
            ]
            writer.writerow(row)
        
        print(f"✅ Added {date_str}: ${total_revenue:,.2f}")
        return True
    
    def interactive_add_today(self):
        """
        Interactive prompt to add today's data
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        day_of_week = today.strftime('%A').upper()
        
        print(f"📅 Adding data for TODAY: {date_str} ({day_of_week})")
        print("=" * 50)
        
        try:
            total_revenue = float(input("Total Revenue ($): ").replace('$', '').replace(',', ''))
            
            print("\nOptional - Individual Garage Revenues:")
            gpn_revenue = input("Grant Park North ($, or press Enter to skip): ").replace('$', '').replace(',', '')
            gps_revenue = input("Grant Park South ($, or press Enter to skip): ").replace('$', '').replace(',', '')
            lakeside_revenue = input("Lakeside ($, or press Enter to skip): ").replace('$', '').replace(',', '')
            millennium_revenue = input("Millennium ($, or press Enter to skip): ").replace('$', '').replace(',', '')
            
            # Convert to floats
            gpn_revenue = float(gpn_revenue) if gpn_revenue else 0
            gps_revenue = float(gps_revenue) if gps_revenue else 0
            lakeside_revenue = float(lakeside_revenue) if lakeside_revenue else 0
            millennium_revenue = float(millennium_revenue) if millennium_revenue else 0
            
            # Add the data
            success = self.add_daily_data(
                date_str, day_of_week, total_revenue,
                gpn_revenue, gps_revenue, lakeside_revenue, millennium_revenue
            )
            
            if success:
                print(f"\n🎉 Successfully added today's data!")
                print(f"💡 Your forecast scripts will now use the updated data")
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Operation cancelled")
    
    def validate_clean_file(self):
        """
        Validate the clean file structure and data
        """
        if not os.path.exists(self.clean_filename):
            print(f"❌ Clean file not found: {self.clean_filename}")
            return False
        
        print(f"🔍 Validating clean file: {self.clean_filename}")
        
        try:
            with open(self.clean_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check headers
                expected_headers = ['Date', 'Day_of_Week', 'Total_Revenue', 'GPN_Revenue', 'GPS_Revenue', 'Lakeside_Revenue', 'Millennium_Revenue']
                actual_headers = reader.fieldnames
                
                print(f"Headers: {actual_headers}")
                
                # Count rows and validate data
                row_count = 0
                valid_rows = 0
                latest_date = None
                
                for row in reader:
                    row_count += 1
                    
                    # Validate date
                    try:
                        date_obj = datetime.strptime(row['Date'], '%Y-%m-%d')
                        if not latest_date or date_obj > latest_date:
                            latest_date = date_obj
                        valid_rows += 1
                    except ValueError:
                        print(f"⚠️ Invalid date in row {row_count}: {row['Date']}")
                
                print(f"✅ Validation complete:")
                print(f"  Total rows: {row_count}")
                print(f"  Valid rows: {valid_rows}")
                print(f"  Latest date: {latest_date.strftime('%Y-%m-%d') if latest_date else 'None'}")
                print(f"  File size: {os.path.getsize(self.clean_filename)/1024:.1f} KB")
                
                return True
                
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

# Example usage
if __name__ == "__main__":
    updater = DailyDataUpdater()
    
    print("🔧 DAILY DATA UPDATER")
    print("=" * 30)
    print("1. Create clean file from original")
    print("2. Add today's data interactively")
    print("3. Validate clean file")
    print("4. Exit")
    
    choice = input("\nChoose an option (1-4): ")
    
    if choice == "1":
        updater.create_clean_file_from_original()
    elif choice == "2":
        updater.interactive_add_today()
    elif choice == "3":
        updater.validate_clean_file()
    else:
        print("👋 Goodbye!")

#!/usr/bin/env python3
"""
Read Historic Booking Data Excel File
Convert to proper format for forecasting
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def analyze_excel_file():
    """Analyze the historic booking data Excel file"""
    excel_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.xlsx"
    
    print("🚗 Historic Booking Data Analysis")
    print("=" * 50)
    
    if not os.path.exists(excel_file):
        print(f"❌ File not found: {excel_file}")
        return False
    
    file_size = os.path.getsize(excel_file)
    print(f"📊 File found: HIstoric Booking Data.xlsx")
    print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Since we can't directly read Excel with standard library, let's provide instructions
    print(f"\n🔧 To use this data for forecasting:")
    print(f"1. Open: HIstoric Booking Data.xlsx")
    print(f"2. Look for columns like: Date, Revenue, Garage, Amount, etc.")
    print(f"3. Save as CSV format with name: historic_booking_data.csv")
    print(f"4. Make sure it includes:")
    print(f"   - Date column (daily data preferred)")
    print(f"   - Revenue/Amount column")
    print(f"   - Garage/Location column (if multiple locations)")
    
    # Check if CSV version already exists
    csv_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/historic_booking_data.csv"
    if os.path.exists(csv_file):
        print(f"\n✅ Found CSV version: historic_booking_data.csv")
        analyze_csv_data(csv_file)
        return True
    else:
        print(f"\n❌ CSV version not found at: {csv_file}")
        print(f"Please convert the Excel file to CSV format.")
        return False

def analyze_csv_data(csv_file):
    """Analyze the CSV version of the data"""
    print(f"\n📊 Analyzing CSV data...")
    
    try:
        with open(csv_file, 'r') as file:
            # Read first few lines to understand structure
            lines = file.readlines()
            
            print(f"Total lines in file: {len(lines):,}")
            print(f"\nFirst 10 lines:")
            for i, line in enumerate(lines[:10]):
                print(f"{i+1:2d}: {line.strip()}")
            
            if len(lines) > 10:
                print(f"\nLast 5 lines:")
                for i, line in enumerate(lines[-5:], len(lines)-4):
                    print(f"{i:2d}: {line.strip()}")
            
            # Try to parse as CSV and get basic stats
            file.seek(0)
            reader = csv.DictReader(file)
            
            # Get column names
            fieldnames = reader.fieldnames
            print(f"\nColumns found: {fieldnames}")
            
            # Read some sample data
            sample_rows = []
            total_rows = 0
            for row in reader:
                if total_rows < 5:
                    sample_rows.append(row)
                total_rows += 1
            
            print(f"\nTotal data rows: {total_rows:,}")
            print(f"\nSample data rows:")
            for i, row in enumerate(sample_rows, 1):
                print(f"Row {i}: {dict(row)}")
                
            # Try to identify revenue columns
            revenue_columns = []
            for col in fieldnames:
                if any(word in col.lower() for word in ['revenue', 'amount', 'total', 'income', 'sales']):
                    revenue_columns.append(col)
            
            if revenue_columns:
                print(f"\nPotential revenue columns: {revenue_columns}")
            
            # Try to identify date columns
            date_columns = []
            for col in fieldnames:
                if any(word in col.lower() for word in ['date', 'time', 'day', 'month']):
                    date_columns.append(col)
            
            if date_columns:
                print(f"Potential date columns: {date_columns}")
                
    except Exception as e:
        print(f"Error analyzing CSV: {str(e)}")

def create_forecast_with_new_data():
    """Create forecast using the new historic booking data"""
    csv_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/historic_booking_data.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Please convert Excel to CSV first")
        return
    
    print(f"\n🔮 Ready to create forecast with new data!")
    print(f"Once you have the CSV file, I can:")
    print(f"1. Analyze the complete revenue patterns")
    print(f"2. Generate accurate forecasts matching your $1.6M+ monthly revenue")
    print(f"3. Provide detailed seasonality analysis")
    print(f"4. Create reliable daily/weekly/monthly predictions")

if __name__ == "__main__":
    if analyze_excel_file():
        create_forecast_with_new_data()

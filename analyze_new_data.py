#!/usr/bin/env python3
"""
Analyze New Excel Data File
Handle Excel format and provide proper forecasting
"""

import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import os

def read_excel_as_csv():
    """Try to convert Excel to CSV or read if already converted"""
    excel_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/New Monthly Transient Business Tracking- 2017 - 07-29-2025JBHV6[54].xlsx"
    
    print("📊 Attempting to read Excel file...")
    
    # First, let's try to use a simple approach - check if we can convert it
    try:
        # Try to read with basic methods
        print(f"Excel file exists: {os.path.exists(excel_file)}")
        print(f"File size: {os.path.getsize(excel_file) if os.path.exists(excel_file) else 'N/A'} bytes")
        
        # For now, let's ask the user to convert to CSV
        print("\n🔧 To analyze your Excel file, please:")
        print("1. Open the Excel file")
        print("2. Save it as CSV format")
        print("3. Name it 'new_parking_data.csv'")
        print("4. Place it in the same directory")
        print("\nOr tell me the structure of your Excel file so I can help you analyze it properly.")
        
        return None
        
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return None

def analyze_data_structure():
    """Analyze what we know about the data structure"""
    print("\n📋 Based on your description of $1.6M+ monthly revenue:")
    print("Expected daily revenue should be around:")
    print(f"  Monthly: $1,600,000")
    print(f"  Daily average: ${1600000/30:,.2f}")
    print(f"  This is much higher than what we saw in the previous CSV")
    
    print("\n❓ Questions about your new Excel file:")
    print("1. What columns does it contain?")
    print("2. Is it daily data or monthly summaries?")
    print("3. Does it include all garages combined or separate?")
    print("4. What date range does it cover?")

def main():
    print("🚗 New Parking Data Analysis")
    print("=" * 50)
    
    # Try to read the Excel file
    data = read_excel_as_csv()
    
    if data is None:
        analyze_data_structure()
        
        # Check if user has already converted to CSV
        csv_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/new_parking_data.csv"
        if os.path.exists(csv_file):
            print(f"\n✅ Found CSV file: {csv_file}")
            print("Let me analyze this data...")
            
            # Analyze the CSV version
            try:
                with open(csv_file, 'r') as file:
                    # Read first few lines to understand structure
                    lines = file.readlines()[:10]
                    print(f"\nFirst 10 lines of your data:")
                    for i, line in enumerate(lines):
                        print(f"{i+1}: {line.strip()}")
                        
            except Exception as e:
                print(f"Error reading CSV: {str(e)}")
        else:
            print(f"\n❌ CSV file not found at: {csv_file}")
            print("Please convert your Excel file to CSV format.")

if __name__ == "__main__":
    main()

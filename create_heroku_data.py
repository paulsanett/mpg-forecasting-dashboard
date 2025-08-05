#!/usr/bin/env python3
"""
Create essential historical data for Heroku deployment
Extracts only the data needed for Departure-Day Revenue Model v4.0
"""

import csv
import json
from datetime import datetime
from robust_csv_reader import RobustCSVReader

def create_essential_historical_data():
    """Create a compressed version of historical data for Heroku"""
    
    print("📊 Creating essential historical data for Heroku deployment...")
    
    # Load full historical data using robust CSV reader
    csv_reader = RobustCSVReader('HIstoric Booking Data.csv')
    historical_data = csv_reader.read_csv_robust()
    
    if not historical_data:
        print("❌ Error: Could not load historical data")
        return
    
    print(f"✅ Loaded {len(historical_data)} historical records")
    
    # Extract essential data for Departure-Day Revenue Model
    essential_data = []
    
    for record in historical_data:
        # Only keep essential fields needed for v4.0 model
        essential_record = {
            'date': record['date_str'],
            'day_of_week': record['day_of_week'],
            'total_revenue': record['total_revenue'],
            'date_obj': record['date'].isoformat() if hasattr(record['date'], 'isoformat') else str(record['date'])
        }
        essential_data.append(essential_record)
    
    # Sort by date (most recent first)
    essential_data.sort(key=lambda x: x['date'], reverse=True)
    
    # Keep only the most recent 1000 records (sufficient for model calibration)
    essential_data = essential_data[:1000]
    
    # Save as JSON for efficient loading
    with open('essential_historical_data.json', 'w') as f:
        json.dump(essential_data, f, indent=2)
    
    print(f"✅ Created essential_historical_data.json with {len(essential_data)} records")
    
    # Also create a minimal CSV version
    with open('essential_historical_data.csv', 'w', newline='') as f:
        if essential_data:
            writer = csv.DictWriter(f, fieldnames=essential_data[0].keys())
            writer.writeheader()
            writer.writerows(essential_data)
    
    print(f"✅ Created essential_historical_data.csv with {len(essential_data)} records")
    
    # Check file sizes
    import os
    json_size = os.path.getsize('essential_historical_data.json') / 1024 / 1024
    csv_size = os.path.getsize('essential_historical_data.csv') / 1024 / 1024
    
    print(f"📊 File sizes:")
    print(f"   JSON: {json_size:.2f} MB")
    print(f"   CSV: {csv_size:.2f} MB")
    print(f"   Original: 115 MB")
    print(f"   Compression: {((115 - json_size) / 115 * 100):.1f}% reduction")

if __name__ == "__main__":
    create_essential_historical_data()

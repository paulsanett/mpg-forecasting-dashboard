#!/usr/bin/env python3
"""
Simple Gas Price Extractor - reads ALL data without filtering
"""

import csv
import sys
from datetime import datetime

def extract_all_gas_prices():
    """Extract all gas price data without filtering"""
    print("🔍 EXTRACTING ALL GAS PRICE DATA")
    print("=" * 40)
    
    gas_prices = []
    revenues = []
    dates = []
    
    try:
        with open('HIstoric Booking Data.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            print(f"📋 Total columns: {len(headers)}")
            
            # Find gas price column (position 44, "$ of Gas")
            gas_col = 44
            revenue_col = 35  # AJ - Total Revenue
            date_col = 0      # Date column
            
            print(f"⛽ Gas price column: {gas_col} - \"{headers[gas_col]}\"")
            print(f"💰 Revenue column: {revenue_col} - \"{headers[revenue_col]}\"")
            print(f"📅 Date column: {date_col} - \"{headers[date_col]}\"")
            
            row_count = 0
            valid_gas_count = 0
            valid_revenue_count = 0
            both_valid_count = 0
            
            for row in reader:
                row_count += 1
                
                if len(row) <= max(gas_col, revenue_col, date_col):
                    continue
                
                # Extract gas price
                gas_raw = row[gas_col].strip() if len(row) > gas_col else ""
                gas_price = 0
                
                if gas_raw and gas_raw != '-':
                    try:
                        gas_price = float(gas_raw.replace('$', '').replace(',', ''))
                        if gas_price > 0:
                            valid_gas_count += 1
                    except ValueError:
                        pass
                
                # Extract revenue
                revenue_raw = row[revenue_col].strip() if len(row) > revenue_col else ""
                revenue = 0
                
                if revenue_raw and revenue_raw != '-':
                    try:
                        revenue = float(revenue_raw.replace('$', '').replace(',', ''))
                        if revenue > 0:
                            valid_revenue_count += 1
                    except ValueError:
                        pass
                
                # Extract date
                date_raw = row[date_col].strip() if len(row) > date_col else ""
                
                # If both gas price and revenue are valid, add to analysis
                if gas_price > 0 and revenue > 0:
                    gas_prices.append(gas_price)
                    revenues.append(revenue)
                    dates.append(date_raw)
                    both_valid_count += 1
            
            print(f"\n📊 DATA EXTRACTION RESULTS:")
            print(f"   Total rows processed: {row_count}")
            print(f"   Valid gas prices: {valid_gas_count}")
            print(f"   Valid revenues: {valid_revenue_count}")
            print(f"   Both valid: {both_valid_count}")
            
            if both_valid_count > 0:
                print(f"\n⛽ GAS PRICE ANALYSIS:")
                print(f"   Average gas price: ${sum(gas_prices)/len(gas_prices):.2f}")
                print(f"   Gas price range: ${min(gas_prices):.2f} - ${max(gas_prices):.2f}")
                
                print(f"\n💰 REVENUE ANALYSIS:")
                print(f"   Average revenue: ${sum(revenues)/len(revenues):,.0f}")
                print(f"   Revenue range: ${min(revenues):,.0f} - ${max(revenues):,.0f}")
                
                # Calculate correlation
                import numpy as np
                correlation = np.corrcoef(gas_prices, revenues)[0, 1]
                print(f"\n📈 CORRELATION:")
                print(f"   Gas price vs Revenue: {correlation:.3f}")
                
                if abs(correlation) > 0.1:
                    print(f"   ✅ SIGNIFICANT CORRELATION - Gas price is a useful predictor!")
                else:
                    print(f"   ⚠️  Low correlation - Gas price may not be significant predictor")
                
                # Show sample data
                print(f"\n📋 SAMPLE DATA:")
                for i in range(min(5, len(dates))):
                    print(f"   {dates[i]}: Gas=${gas_prices[i]:.2f}, Revenue=${revenues[i]:,.0f}")
                
                return gas_prices, revenues, dates
            else:
                print("❌ No valid gas price + revenue combinations found")
                return [], [], []
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], [], []

if __name__ == "__main__":
    gas_prices, revenues, dates = extract_all_gas_prices()
    
    if len(gas_prices) > 100:
        print(f"\n🎉 SUCCESS! Found {len(gas_prices)} valid gas price records!")
        print("✅ Ready for enhanced modeling with gas price predictor")
    else:
        print(f"\n❌ Insufficient data: Only {len(gas_prices)} valid records")

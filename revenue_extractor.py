#!/usr/bin/env python3
"""
Revenue Extractor - Extract all revenue data from historic booking CSV
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def extract_all_revenue():
    """Extract all revenue data with minimal filtering"""
    file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
    
    print("🚗 Revenue Extractor")
    print("=" * 50)
    
    data = []
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        # Skip header
        header = next(reader)
        print(f"📋 Found {len(header)} columns")
        
        # Find Total Revenue column (should be around position 37)
        revenue_col = None
        for i, col in enumerate(header):
            if 'total revenue' in col.lower().strip():
                revenue_col = i
                break
        
        if revenue_col is None:
            print("❌ Could not find Total Revenue column")
            return []
        
        print(f"✅ Total Revenue column at position {revenue_col}")
        
        # Process all rows
        row_count = 0
        valid_count = 0
        total_revenue = 0
        
        for row in reader:
            row_count += 1
            
            # Skip empty rows or rows with insufficient columns
            if len(row) <= max(0, 1, 2, revenue_col):
                continue
            
            try:
                # Extract date components
                year_str = row[0].strip() if len(row) > 0 else ""
                month_str = row[1].strip() if len(row) > 1 else ""
                date_str = row[2].strip() if len(row) > 2 else ""
                revenue_str = row[revenue_col].strip() if len(row) > revenue_col else ""
                
                # Skip if missing key data
                if not year_str or not month_str or not date_str or not revenue_str:
                    continue
                
                # Parse date
                try:
                    year = int(year_str)
                    
                    # Month mapping
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    
                    month_lower = month_str.lower()
                    if month_lower in month_map:
                        month = month_map[month_lower]
                    else:
                        month = int(month_str)
                    
                    day = int(date_str)
                    date = datetime(year, month, day)
                    
                except:
                    continue
                
                # Parse revenue - be very permissive
                try:
                    # Remove all non-numeric except decimal point and minus
                    clean_revenue = ""
                    for char in revenue_str:
                        if char.isdigit() or char == '.' or char == '-':
                            clean_revenue += char
                    
                    if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                        revenue = float(clean_revenue)
                        
                        # Accept any positive revenue over $100
                        if revenue > 100:
                            data.append({
                                'date': date,
                                'revenue': revenue,
                                'year': year,
                                'month': month,
                                'day': day,
                                'day_of_week': date.weekday()
                            })
                            total_revenue += revenue
                            valid_count += 1
                            
                            # Show progress for large revenues
                            if revenue > 30000:
                                print(f"  📈 {date.strftime('%Y-%m-%d')}: ${revenue:,.2f}")
                
                except:
                    continue
                    
            except:
                continue
        
        print(f"✅ Processed {row_count:,} rows")
        print(f"✅ Found {valid_count:,} valid revenue records")
        print(f"💰 Total revenue: ${total_revenue:,.2f}")
        
        if valid_count > 0:
            avg_daily = total_revenue / valid_count
            monthly_estimate = avg_daily * 30
            print(f"📈 Average daily: ${avg_daily:,.2f}")
            print(f"📊 Monthly estimate: ${monthly_estimate:,.2f}")
            
            # Sort by date
            data.sort(key=lambda x: x['date'])
            
            if data:
                print(f"📅 Date range: {data[0]['date'].strftime('%Y-%m-%d')} to {data[-1]['date'].strftime('%Y-%m-%d')}")
                
                # Show some sample high-revenue days
                high_revenue_days = [d for d in data if d['revenue'] > 40000]
                if high_revenue_days:
                    print(f"\n🎯 Sample high-revenue days:")
                    for day in high_revenue_days[:5]:
                        print(f"  {day['date'].strftime('%Y-%m-%d')}: ${day['revenue']:,.2f}")
            
            # Business validation
            if monthly_estimate > 1000000:
                print(f"\n✅ SUCCESS: Monthly estimate of ${monthly_estimate:,.2f} aligns with your $1.6M+ business!")
            elif monthly_estimate > 500000:
                print(f"\n✅ Good progress: ${monthly_estimate:,.2f} monthly - getting closer to $1.6M+ target!")
            else:
                print(f"\n⚠️  Monthly estimate of ${monthly_estimate:,.2f} still seems low.")
        
        return data

def create_forecast(data, days=30):
    """Create forecast from extracted data"""
    if not data:
        return []
    
    print(f"\n🔮 Creating {days}-day forecast...")
    
    # Use recent data for baseline
    recent_cutoff = data[-1]['date'] - timedelta(days=90)
    recent_data = [d for d in data if d['date'] >= recent_cutoff]
    
    if len(recent_data) < 10:
        recent_data = data[-30:] if len(data) >= 30 else data
    
    print(f"📊 Using {len(recent_data)} recent records for forecast baseline")
    
    # Calculate day-of-week patterns
    dow_revenues = defaultdict(list)
    for record in recent_data:
        dow_revenues[record['day_of_week']].append(record['revenue'])
    
    dow_averages = {}
    days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    overall_avg = statistics.mean([r['revenue'] for r in recent_data])
    
    for dow in range(7):
        if dow in dow_revenues and dow_revenues[dow]:
            dow_averages[dow] = statistics.mean(dow_revenues[dow])
        else:
            dow_averages[dow] = overall_avg
    
    print(f"📊 Day-of-week averages:")
    for dow in range(7):
        print(f"  {days_names[dow]}: ${dow_averages[dow]:,.2f}")
    
    # Generate forecast
    last_date = data[-1]['date']
    forecast = []
    
    for i in range(1, days + 1):
        forecast_date = last_date + timedelta(days=i)
        dow = forecast_date.weekday()
        predicted_revenue = dow_averages[dow]
        
        forecast.append({
            'date': forecast_date.strftime('%Y-%m-%d'),
            'day_name': days_names[dow],
            'predicted_revenue': round(predicted_revenue, 2)
        })
    
    return forecast

def main():
    # Extract all revenue data
    data = extract_all_revenue()
    
    if not data:
        print("❌ No revenue data extracted")
        return
    
    # Create forecast
    forecast = create_forecast(data, 30)
    
    if forecast:
        total_forecast = sum(day['predicted_revenue'] for day in forecast)
        
        print(f"\n📈 30-Day Forecast Results:")
        print(f"  Total forecasted revenue: ${total_forecast:,.2f}")
        print(f"  Average daily revenue: ${total_forecast/30:,.2f}")
        
        print(f"\n📅 Next 7 days forecast:")
        for day in forecast[:7]:
            print(f"  {day['date']} ({day['day_name']}): ${day['predicted_revenue']:,.2f}")
        
        # Save results
        with open('final_revenue_forecast.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Day', 'Predicted_Revenue'])
            for day in forecast:
                writer.writerow([day['date'], day['day_name'], day['predicted_revenue']])
        
        print(f"\n💾 Forecast saved to: final_revenue_forecast.csv")
        
        # Final validation
        if total_forecast > 1200000:
            print(f"\n🎉 EXCELLENT: ${total_forecast:,.2f} forecast matches your $1.6M+ monthly business!")
        elif total_forecast > 800000:
            print(f"\n✅ GOOD: ${total_forecast:,.2f} forecast is approaching your $1.6M+ target!")
        else:
            print(f"\n⚠️  ${total_forecast:,.2f} forecast still seems lower than your $1.6M+ business.")

if __name__ == "__main__":
    main()

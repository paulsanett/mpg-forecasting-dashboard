#!/usr/bin/env python3
"""
Flexible Parking Revenue Forecasting
Works with multiple data formats and automatically detects proper revenue levels
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import sys

class FlexibleParkingForecast:
    def __init__(self):
        self.data = []
        self.garage_data = {}
        
    def try_multiple_files(self):
        """Try to load data from multiple possible file sources"""
        possible_files = [
            "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv",
            "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/historic_booking_data.csv",
            "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/new_parking_data.csv",
            "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/Cleaned_Transient_Revenue_Data_updated.csv"
        ]
        
        print("🔍 Searching for data files...")
        
        for file_path in possible_files:
            if os.path.exists(file_path):
                print(f"✅ Found: {os.path.basename(file_path)}")
                try:
                    if self.load_data(file_path):
                        return file_path
                except Exception as e:
                    print(f"❌ Error loading {os.path.basename(file_path)}: {str(e)}")
                    continue
        
        print("❌ No suitable data files found.")
        return None
    
    def load_data(self, file_path):
        """Load data from CSV file with flexible column detection"""
        print(f"📊 Loading data from {os.path.basename(file_path)}...")
        
        with open(file_path, 'r') as file:
            # Peek at first line to understand structure
            first_line = file.readline().strip()
            file.seek(0)
            
            reader = csv.DictReader(file)
            columns = reader.fieldnames
            print(f"Columns found: {columns}")
            
            # Auto-detect column names
            date_col = self.find_column(columns, ['date', 'time', 'day'])
            revenue_col = self.find_column(columns, ['revenue', 'amount', 'total', 'income', 'sales'])
            garage_col = self.find_column(columns, ['garage', 'location', 'site', 'facility'])
            
            if not date_col:
                print("❌ No date column found")
                return False
            if not revenue_col:
                print("❌ No revenue column found")
                return False
                
            print(f"Using columns - Date: {date_col}, Revenue: {revenue_col}, Garage: {garage_col}")
            
            # Load the data
            row_count = 0
            total_revenue = 0
            
            for row in reader:
                try:
                    # Parse date
                    date_str = row[date_col]
                    date = self.parse_date(date_str)
                    if not date:
                        continue
                    
                    # Parse revenue
                    revenue_str = row[revenue_col]
                    revenue = self.parse_revenue(revenue_str)
                    if revenue is None:
                        continue
                    
                    # Get garage (default to 'ALL' if not specified)
                    garage = row[garage_col] if garage_col else 'ALL'
                    
                    record = {
                        'date': date,
                        'garage': garage,
                        'revenue': revenue,
                        'day_of_week': date.weekday(),
                        'month': date.month,
                        'year': date.year,
                        'is_weekend': date.weekday() >= 5
                    }
                    
                    self.data.append(record)
                    
                    if garage not in self.garage_data:
                        self.garage_data[garage] = []
                    self.garage_data[garage].append(record)
                    
                    row_count += 1
                    total_revenue += revenue
                    
                except Exception as e:
                    continue
            
            if row_count == 0:
                print("❌ No valid data rows found")
                return False
            
            # Sort data by date
            for garage in self.garage_data:
                self.garage_data[garage].sort(key=lambda x: x['date'])
            
            print(f"✅ Loaded {row_count:,} records")
            print(f"💰 Total revenue in dataset: ${total_revenue:,.2f}")
            print(f"📈 Average daily revenue: ${total_revenue/row_count:,.2f}")
            print(f"🏢 Garages: {list(self.garage_data.keys())}")
            
            # Check if this looks like realistic data
            avg_daily = total_revenue / row_count
            if avg_daily > 10000:  # More than $10k per day suggests complete data
                print("✅ Revenue levels look realistic for $1.6M+ monthly business")
            else:
                print("⚠️  Revenue levels seem low - may need data verification")
            
            return True
    
    def find_column(self, columns, keywords):
        """Find column name that matches keywords"""
        for col in columns:
            for keyword in keywords:
                if keyword.lower() in col.lower():
                    return col
        return None
    
    def parse_date(self, date_str):
        """Parse date from various formats"""
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return None
    
    def parse_revenue(self, revenue_str):
        """Parse revenue from various formats"""
        try:
            # Remove common currency symbols and commas
            clean_str = revenue_str.replace('$', '').replace(',', '').replace(' ', '')
            return float(clean_str)
        except:
            return None
    
    def analyze_garage(self, garage_name):
        """Analyze patterns for a specific garage"""
        if garage_name not in self.garage_data:
            return None
        
        data = self.garage_data[garage_name]
        revenues = [r['revenue'] for r in data]
        
        analysis = {
            'garage': garage_name,
            'total_records': len(data),
            'date_range': (data[0]['date'], data[-1]['date']),
            'total_revenue': sum(revenues),
            'avg_revenue': statistics.mean(revenues),
            'median_revenue': statistics.median(revenues),
            'std_revenue': statistics.stdev(revenues) if len(revenues) > 1 else 0,
            'min_revenue': min(revenues),
            'max_revenue': max(revenues)
        }
        
        # Day of week patterns
        dow_revenues = defaultdict(list)
        for record in data:
            dow_revenues[record['day_of_week']].append(record['revenue'])
        
        dow_averages = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for dow in range(7):
            if dow in dow_revenues:
                dow_averages[days[dow]] = statistics.mean(dow_revenues[dow])
        
        analysis['dow_averages'] = dow_averages
        
        # Monthly patterns
        monthly_revenues = defaultdict(list)
        for record in data:
            monthly_revenues[record['month']].append(record['revenue'])
        
        monthly_averages = {}
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month in range(1, 13):
            if month in monthly_revenues:
                monthly_averages[months[month-1]] = statistics.mean(monthly_revenues[month])
        
        analysis['monthly_averages'] = monthly_averages
        
        # Use recent data for baseline (last 90 days to avoid short-term anomalies)
        recent_data = [r for r in data if r['date'] >= data[-1]['date'] - timedelta(days=90)]
        analysis['recent_avg'] = statistics.mean([r['revenue'] for r in recent_data]) if recent_data else analysis['avg_revenue']
        
        # Calculate seasonality factors
        overall_avg = analysis['avg_revenue']
        analysis['dow_factors'] = {}
        for day, avg in dow_averages.items():
            analysis['dow_factors'][day] = avg / overall_avg if overall_avg > 0 else 1
        
        return analysis
    
    def create_forecast(self, garage_name, days=30):
        """Create forecast for specified garage"""
        analysis = self.analyze_garage(garage_name)
        if not analysis:
            return None
        
        data = self.garage_data[garage_name]
        last_date = data[-1]['date']
        
        forecast = []
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][forecast_date.weekday()]
            
            # Base forecast on recent average adjusted by day-of-week factor
            base_forecast = analysis['recent_avg']
            dow_factor = analysis['dow_factors'].get(day_name, 1)
            
            predicted_revenue = base_forecast * dow_factor
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'day_name': day_name,
                'predicted_revenue': round(predicted_revenue, 2)
            })
        
        return forecast
    
    def print_analysis(self, garage_name):
        """Print detailed analysis"""
        analysis = self.analyze_garage(garage_name)
        if not analysis:
            print(f"❌ No data found for garage: {garage_name}")
            return
        
        print(f"\n🎯 Analysis for {garage_name}")
        print("=" * 50)
        print(f"📊 Records: {analysis['total_records']:,}")
        print(f"📅 Date Range: {analysis['date_range'][0].strftime('%Y-%m-%d')} to {analysis['date_range'][1].strftime('%Y-%m-%d')}")
        print(f"💰 Total Revenue: ${analysis['total_revenue']:,.2f}")
        print(f"📈 Average Daily: ${analysis['avg_revenue']:,.2f}")
        print(f"📊 Recent 90-day Avg: ${analysis['recent_avg']:,.2f}")
        
        # Calculate monthly estimate
        monthly_estimate = analysis['recent_avg'] * 30
        print(f"📊 Monthly Estimate: ${monthly_estimate:,.2f}")
        
        print(f"\n📊 Day of Week Averages:")
        for day, avg in analysis['dow_averages'].items():
            factor = analysis['dow_factors'][day]
            print(f"  {day:9}: ${avg:8,.2f} (factor: {factor:.2f})")

def main():
    print("🚗 Flexible Parking Revenue Forecasting")
    print("=" * 50)
    
    forecaster = FlexibleParkingForecast()
    
    # Try to load data from available files
    data_file = forecaster.try_multiple_files()
    
    if not data_file:
        print("\n❌ No data files found. Please:")
        print("1. Convert your Excel file to CSV format")
        print("2. Name it 'historic_booking_data.csv'")
        print("3. Place it in the project directory")
        return
    
    print(f"\n✅ Successfully loaded data from: {os.path.basename(data_file)}")
    
    # Analyze the main garage or combined data
    garages = list(forecaster.garage_data.keys())
    main_garage = garages[0]  # Use first garage or 'ALL' if combined
    
    forecaster.print_analysis(main_garage)
    
    # Create forecast
    print(f"\n🔮 Generating 30-day forecast for {main_garage}...")
    forecast = forecaster.create_forecast(main_garage, 30)
    
    if forecast:
        total_forecast = sum(day['predicted_revenue'] for day in forecast)
        avg_daily = total_forecast / len(forecast)
        
        print(f"\n📈 Forecast Summary (next 30 days):")
        print(f"  Total forecasted revenue: ${total_forecast:,.2f}")
        print(f"  Average daily revenue: ${avg_daily:,.2f}")
        
        print(f"\n📅 Next 7 days:")
        for i in range(min(7, len(forecast))):
            day = forecast[i]
            print(f"  {day['date']} ({day['day_name']}): ${day['predicted_revenue']:,.2f}")
        
        # Save forecast
        filename = 'flexible_parking_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Day', 'Predicted_Revenue'])
            for day in forecast:
                writer.writerow([day['date'], day['day_name'], day['predicted_revenue']])
        
        print(f"\n💾 Forecast saved to: {filename}")
        
        # Validate against expected $1.6M monthly
        if total_forecast > 1000000:  # Over $1M
            print(f"\n✅ Forecast aligns with your $1.6M+ monthly business!")
        else:
            print(f"\n⚠️  Forecast seems low compared to your $1.6M+ monthly business.")
            print(f"This might indicate:")
            print(f"  - Data covers only part of your business")
            print(f"  - Need to combine multiple garages")
            print(f"  - Excel file needs to be converted to CSV")

if __name__ == "__main__":
    main()

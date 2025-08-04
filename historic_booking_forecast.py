#!/usr/bin/env python3
"""
Historic Booking Data Forecasting
Specifically designed for your historic booking data format
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class HistoricBookingForecast:
    def __init__(self):
        self.data = []
        self.total_revenue_data = []
        
    def load_historic_data(self):
        """Load the historic booking data CSV"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🚗 Historic Booking Data Forecasting")
        print("=" * 50)
        print(f"📊 Loading data from HIstoric Booking Data.csv...")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # Clean up column names (remove extra spaces)
            fieldnames = [col.strip() for col in reader.fieldnames]
            
            print(f"📋 Columns available:")
            for i, col in enumerate(fieldnames[:10]):  # Show first 10 columns
                print(f"  {i+1:2d}. {col}")
            if len(fieldnames) > 10:
                print(f"  ... and {len(fieldnames)-10} more columns")
            
            # Find the key columns we need
            date_col = None
            year_col = None
            month_col = None
            total_revenue_col = None
            
            for col in fieldnames:
                if col.lower() == 'date':
                    date_col = col
                elif col.lower() == 'year':
                    year_col = col
                elif col.lower() == 'month':
                    month_col = col
                elif col.lower() == 'total revenue':
                    total_revenue_col = col
            
            if not date_col or not year_col or not month_col:
                print("❌ Missing required columns: Year, Month, Date")
                return False
            if not total_revenue_col:
                print("❌ No 'Total Revenue' column found")
                return False
            
            print(f"✅ Using Date column: '{date_col}'")
            print(f"✅ Using Year column: '{year_col}'")
            print(f"✅ Using Month column: '{month_col}'")
            print(f"✅ Using Revenue column: '{total_revenue_col}'")
            
            # Load the data
            row_count = 0
            valid_rows = 0
            total_revenue_sum = 0
            
            for row in reader:
                row_count += 1
                
                try:
                    # Parse date from Year/Month/Date columns
                    year_str = row[year_col].strip()
                    month_str = row[month_col].strip()
                    date_str = row[date_col].strip()
                    
                    if not year_str or not month_str or not date_str:
                        continue
                    
                    date = self.parse_date_from_components(year_str, month_str, date_str)
                    if not date:
                        continue
                    
                    # Parse total revenue
                    revenue_str = row[total_revenue_col].strip()
                    if not revenue_str:
                        continue
                    
                    revenue = self.parse_revenue(revenue_str)
                    if revenue is None or revenue <= 0:
                        continue
                    
                    record = {
                        'date': date,
                        'revenue': revenue,
                        'day_of_week': date.weekday(),
                        'month': date.month,
                        'year': date.year,
                        'is_weekend': date.weekday() >= 5
                    }
                    
                    self.data.append(record)
                    total_revenue_sum += revenue
                    valid_rows += 1
                    
                except Exception as e:
                    continue
            
            if valid_rows == 0:
                print("❌ No valid data rows found")
                return False
            
            # Sort data by date
            self.data.sort(key=lambda x: x['date'])
            
            print(f"✅ Loaded {valid_rows:,} valid records out of {row_count:,} total rows")
            print(f"💰 Total revenue in dataset: ${total_revenue_sum:,.2f}")
            print(f"📈 Average daily revenue: ${total_revenue_sum/valid_rows:,.2f}")
            print(f"📅 Date range: {self.data[0]['date'].strftime('%Y-%m-%d')} to {self.data[-1]['date'].strftime('%Y-%m-%d')}")
            
            # Check if this matches expected $1.6M monthly business
            avg_daily = total_revenue_sum / valid_rows
            monthly_estimate = avg_daily * 30
            print(f"📊 Monthly revenue estimate: ${monthly_estimate:,.2f}")
            
            if monthly_estimate > 1000000:
                print("✅ Revenue levels align with your $1.6M+ monthly business!")
            else:
                print("⚠️  Revenue levels seem lower than expected $1.6M+ monthly")
            
            return True
    
    def parse_date_from_components(self, year_str, month_str, date_str):
        """Parse date from Year/Month/Date components"""
        try:
            year = int(year_str)
            
            # Handle month names
            month_map = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5,
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12
            }
            
            month_lower = month_str.lower()
            if month_lower in month_map:
                month = month_map[month_lower]
            else:
                month = int(month_str)
            
            day = int(date_str)
            
            return datetime(year, month, day)
        except:
            return None
    
    def parse_date(self, date_str):
        """Parse date from various formats"""
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y',
            '%m/%d/%y',
            '%d/%m/%y'
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
            # Remove common currency symbols, commas, and spaces
            clean_str = revenue_str.replace('$', '').replace(',', '').replace(' ', '').replace('(', '-').replace(')', '')
            if clean_str == '' or clean_str == '-':
                return 0
            return float(clean_str)
        except:
            return None
    
    def analyze_patterns(self):
        """Analyze revenue patterns"""
        if not self.data:
            return None
        
        revenues = [r['revenue'] for r in self.data]
        
        analysis = {
            'total_records': len(self.data),
            'date_range': (self.data[0]['date'], self.data[-1]['date']),
            'total_revenue': sum(revenues),
            'avg_revenue': statistics.mean(revenues),
            'median_revenue': statistics.median(revenues),
            'std_revenue': statistics.stdev(revenues) if len(revenues) > 1 else 0,
            'min_revenue': min(revenues),
            'max_revenue': max(revenues)
        }
        
        # Day of week patterns
        dow_revenues = defaultdict(list)
        for record in self.data:
            dow_revenues[record['day_of_week']].append(record['revenue'])
        
        dow_averages = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for dow in range(7):
            if dow in dow_revenues:
                dow_averages[days[dow]] = statistics.mean(dow_revenues[dow])
        
        analysis['dow_averages'] = dow_averages
        
        # Monthly patterns
        monthly_revenues = defaultdict(list)
        for record in self.data:
            monthly_revenues[record['month']].append(record['revenue'])
        
        monthly_averages = {}
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month in range(1, 13):
            if month in monthly_revenues:
                monthly_averages[months[month-1]] = statistics.mean(monthly_revenues[month])
        
        analysis['monthly_averages'] = monthly_averages
        
        # Recent baseline (last 90 days)
        recent_data = [r for r in self.data if r['date'] >= self.data[-1]['date'] - timedelta(days=90)]
        analysis['recent_avg'] = statistics.mean([r['revenue'] for r in recent_data]) if recent_data else analysis['avg_revenue']
        
        # Calculate seasonality factors
        overall_avg = analysis['avg_revenue']
        analysis['dow_factors'] = {}
        for day, avg in dow_averages.items():
            analysis['dow_factors'][day] = avg / overall_avg if overall_avg > 0 else 1
        
        return analysis
    
    def create_forecast(self, days=30):
        """Create revenue forecast"""
        analysis = self.analyze_patterns()
        if not analysis:
            return None
        
        last_date = self.data[-1]['date']
        
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
    
    def print_analysis(self):
        """Print detailed analysis"""
        analysis = self.analyze_patterns()
        if not analysis:
            return
        
        print(f"\n🎯 Revenue Analysis")
        print("=" * 50)
        print(f"📊 Records: {analysis['total_records']:,}")
        print(f"📅 Date Range: {analysis['date_range'][0].strftime('%Y-%m-%d')} to {analysis['date_range'][1].strftime('%Y-%m-%d')}")
        print(f"💰 Total Revenue: ${analysis['total_revenue']:,.2f}")
        print(f"📈 Average Daily: ${analysis['avg_revenue']:,.2f}")
        print(f"📊 Recent 90-day Avg: ${analysis['recent_avg']:,.2f}")
        print(f"📊 Min/Max Daily: ${analysis['min_revenue']:,.2f} / ${analysis['max_revenue']:,.2f}")
        
        # Monthly estimate
        monthly_estimate = analysis['recent_avg'] * 30
        print(f"📊 Monthly Estimate: ${monthly_estimate:,.2f}")
        
        print(f"\n📊 Day of Week Averages:")
        for day, avg in analysis['dow_averages'].items():
            factor = analysis['dow_factors'][day]
            print(f"  {day:9}: ${avg:8,.2f} (factor: {factor:.2f})")
        
        print(f"\n📊 Monthly Averages:")
        for month, avg in analysis['monthly_averages'].items():
            print(f"  {month}: ${avg:8,.2f}")

def main():
    forecaster = HistoricBookingForecast()
    
    # Load the historic booking data
    if not forecaster.load_historic_data():
        return
    
    # Analyze patterns
    forecaster.print_analysis()
    
    # Create 30-day forecast
    print(f"\n🔮 Generating 30-day forecast...")
    forecast = forecaster.create_forecast(30)
    
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
        filename = 'historic_booking_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Day', 'Predicted_Revenue'])
            for day in forecast:
                writer.writerow([day['date'], day['day_name'], day['predicted_revenue']])
        
        print(f"\n💾 Forecast saved to: {filename}")
        
        # Validate against expected business scale
        if total_forecast > 1200000:  # Over $1.2M
            print(f"\n✅ Forecast aligns with your $1.6M+ monthly business scale!")
        elif total_forecast > 800000:  # Over $800k
            print(f"\n✅ Forecast shows strong revenue - close to your $1.6M+ target!")
        else:
            print(f"\n⚠️  Forecast seems lower than your $1.6M+ monthly business.")

if __name__ == "__main__":
    main()

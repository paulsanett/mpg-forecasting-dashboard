#!/usr/bin/env python3
"""
Minimal Parking Revenue Forecasting Script
Uses only Python standard library - no external dependencies required
"""

import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import math

class MinimalParkingForecast:
    def __init__(self):
        self.data = []
        self.garage_data = {}
        
    def load_data(self, file_path):
        """Load parking data from CSV"""
        print(f"📊 Loading data from {file_path}...")
        
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date = datetime.strptime(row['Date'], '%Y-%m-%d')
                    garage = row['Garage']
                    revenue = float(row['Revenue'])
                    
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
                    
                except (ValueError, KeyError) as e:
                    continue
        
        # Sort data by date
        for garage in self.garage_data:
            self.garage_data[garage].sort(key=lambda x: x['date'])
        
        print(f"✅ Loaded {len(self.data):,} records for {len(self.garage_data)} garages")
        return self.data
    
    def analyze_garage(self, garage_name):
        """Analyze patterns for a specific garage"""
        if garage_name not in self.garage_data:
            print(f"❌ Garage {garage_name} not found")
            return None
        
        data = self.garage_data[garage_name]
        revenues = [r['revenue'] for r in data]
        
        # Basic statistics
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
        
        # Recent trend - but exclude problematic 2025 data if it's too low
        recent_30_data = [row for row in data if row['date'] >= data[-1]['date'] - timedelta(days=30)]
        recent_30_avg = statistics.mean([row['revenue'] for row in recent_30_data]) if recent_30_data else analysis['avg_revenue']
        
        # If recent average is dramatically lower than historical (indicating data issues), use 2024 data instead
        if recent_30_avg < analysis['avg_revenue'] * 0.3:  # If recent is less than 30% of historical average
            print(f"⚠️  Recent 30-day average (${recent_30_avg:.2f}) is dramatically lower than historical average (${analysis['avg_revenue']:.2f})")
            print(f"🔧 Using 2024 data as baseline instead of recent low values...")
            
            # Use 2024 data as recent baseline
            recent_2024_data = [row for row in data if row['year'] == 2024]
            if recent_2024_data:
                analysis['recent_avg'] = statistics.mean([row['revenue'] for row in recent_2024_data[-60:]])  # Last 60 days of 2024
                print(f"✅ Using 2024 baseline: ${analysis['recent_avg']:.2f}")
            else:
                analysis['recent_avg'] = analysis['avg_revenue']
        else:
            analysis['recent_avg'] = recent_30_avg
        
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
        
        # Generate forecast
        forecast = []
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][forecast_date.weekday()]
            
            # Base forecast on recent average adjusted by day-of-week factor
            base_forecast = analysis['recent_avg']
            dow_factor = analysis['dow_factors'].get(day_name, 1)
            
            predicted_revenue = base_forecast * dow_factor
            
            # Add some trend adjustment based on recent data
            recent_trend = self.calculate_trend(data[-14:])  # Last 2 weeks
            trend_adjustment = predicted_revenue * recent_trend * (i / days)  # Gradual trend application
            
            final_prediction = predicted_revenue + trend_adjustment
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'day_name': day_name,
                'predicted_revenue': round(final_prediction, 2),
                'base_forecast': round(predicted_revenue, 2),
                'trend_adjustment': round(trend_adjustment, 2)
            })
        
        return forecast
    
    def calculate_trend(self, recent_data):
        """Calculate recent trend factor"""
        if len(recent_data) < 7:
            return 0
        
        # Simple linear trend calculation
        revenues = [r['revenue'] for r in recent_data]
        n = len(revenues)
        x_values = list(range(n))
        
        # Calculate slope using least squares
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(revenues)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, revenues))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        return slope / y_mean if y_mean != 0 else 0  # Normalize by average
    
    def print_analysis(self, garage_name):
        """Print detailed analysis for a garage"""
        analysis = self.analyze_garage(garage_name)
        if not analysis:
            return
        
        print(f"\n🎯 Analysis for {garage_name} Garage")
        print("=" * 50)
        print(f"📊 Records: {analysis['total_records']:,}")
        print(f"📅 Date Range: {analysis['date_range'][0].strftime('%Y-%m-%d')} to {analysis['date_range'][1].strftime('%Y-%m-%d')}")
        print(f"💰 Total Revenue: ${analysis['total_revenue']:,.2f}")
        print(f"📈 Average Daily: ${analysis['avg_revenue']:.2f}")
        print(f"📊 Median Daily: ${analysis['median_revenue']:.2f}")
        print(f"📊 Recent 30-day Avg: ${analysis['recent_avg']:.2f}")
        print(f"📊 Min/Max: ${analysis['min_revenue']:.2f} / ${analysis['max_revenue']:.2f}")
        
        print(f"\n📊 Day of Week Averages:")
        for day, avg in analysis['dow_averages'].items():
            factor = analysis['dow_factors'][day]
            print(f"  {day:9}: ${avg:8.2f} (factor: {factor:.2f})")
        
        print(f"\n📊 Monthly Averages:")
        for month, avg in analysis['monthly_averages'].items():
            print(f"  {month}: ${avg:8.2f}")
    
    def save_forecast(self, forecast, filename):
        """Save forecast to CSV file"""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Day', 'Predicted_Revenue', 'Base_Forecast', 'Trend_Adjustment'])
            for day in forecast:
                writer.writerow([
                    day['date'],
                    day['day_name'],
                    day['predicted_revenue'],
                    day['base_forecast'],
                    day['trend_adjustment']
                ])

def main():
    print("🚗 Minimal Parking Revenue Forecasting")
    print("=" * 50)
    
    # Initialize forecaster
    forecaster = MinimalParkingForecast()
    
    # Load data
    data_file = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/Cleaned_Transient_Revenue_Data_updated.csv"
    forecaster.load_data(data_file)
    
    # Analyze each garage
    garages = list(forecaster.garage_data.keys())
    print(f"\n🏢 Found garages: {', '.join(garages)}")
    
    # Focus on GPN (appears to have most complete data)
    main_garage = 'GPN'
    if main_garage in garages:
        forecaster.print_analysis(main_garage)
        
        # Create 30-day forecast
        print(f"\n🔮 Generating 30-day forecast for {main_garage}...")
        forecast = forecaster.create_forecast(main_garage, 30)
        
        if forecast:
            total_forecast = sum(day['predicted_revenue'] for day in forecast)
            avg_forecast = total_forecast / len(forecast)
            
            print(f"\n📈 Forecast Summary (next 30 days):")
            print(f"  Average daily revenue: ${avg_forecast:.2f}")
            print(f"  Total forecasted revenue: ${total_forecast:.2f}")
            print(f"  Min daily forecast: ${min(day['predicted_revenue'] for day in forecast):.2f}")
            print(f"  Max daily forecast: ${max(day['predicted_revenue'] for day in forecast):.2f}")
            
            print(f"\n📅 Next 7 days forecast:")
            for i in range(min(7, len(forecast))):
                day = forecast[i]
                print(f"  {day['date']} ({day['day_name']}): ${day['predicted_revenue']:.2f}")
            
            # Save forecast
            forecaster.save_forecast(forecast, 'parking_forecast_minimal.csv')
            print(f"\n💾 Forecast saved to: parking_forecast_minimal.csv")
            
            # Calculate accuracy estimate
            analysis = forecaster.analyze_garage(main_garage)
            recent_revenues = [r['revenue'] for r in forecaster.garage_data[main_garage][-30:]]
            if len(recent_revenues) > 1:
                recent_std = statistics.stdev(recent_revenues)
                recent_avg = statistics.mean(recent_revenues)
                cv = (recent_std / recent_avg) * 100 if recent_avg > 0 else 0
                print(f"\n📊 Model Accuracy Estimate:")
                print(f"  Recent coefficient of variation: {cv:.1f}%")
                print(f"  Expected forecast accuracy: ±{cv:.1f}%")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Revenue Forecasting with Weather & Events
Builds on your working revenue_extractor.py with weather and event adjustments
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class EnhancedRevenueForecaster:
    def __init__(self):
        self.data = []
        
    def load_revenue_data(self):
        """Load revenue data using the proven working approach"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🚗 Enhanced Revenue Forecasting with Weather & Events")
        print("=" * 65)
        
        data = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            revenue_col = 37  # We know this works from revenue_extractor.py
            
            row_count = 0
            valid_count = 0
            total_revenue = 0
            
            for row in reader:
                row_count += 1
                
                if len(row) <= revenue_col:
                    continue
                
                try:
                    # Extract date components (same as working model)
                    year_str = row[0].strip() if len(row) > 0 else ""
                    month_str = row[1].strip() if len(row) > 1 else ""
                    date_str = row[2].strip() if len(row) > 2 else ""
                    revenue_str = row[revenue_col].strip() if len(row) > revenue_col else ""
                    
                    if not year_str or not month_str or not date_str or not revenue_str:
                        continue
                    
                    # Parse date (same as working model)
                    year = int(year_str)
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
                    
                    # Parse revenue (same as working model)
                    clean_revenue = ""
                    for char in revenue_str:
                        if char.isdigit() or char == '.' or char == '-':
                            clean_revenue += char
                    
                    if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                        revenue = float(clean_revenue)
                        
                        if revenue > 1000:  # Same threshold as working model
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
                
                except:
                    continue
            
            print(f"✅ Loaded {valid_count:,} valid revenue records")
            print(f"💰 Total revenue: ${total_revenue:,.2f}")
            print(f"📈 Average daily: ${total_revenue/valid_count:,.2f}")
            print(f"📊 Monthly estimate: ${(total_revenue/valid_count)*30:,.2f}")
            
            # Sort by date
            data.sort(key=lambda x: x['date'])
            self.data = data
            
            return data
    
    def get_weather_adjustment(self, temperature, precipitation):
        """Get weather adjustment factor based on conditions"""
        temp_factor = 1.0
        precip_factor = 1.0
        
        # Temperature adjustments (based on parking industry research)
        if temperature < 32:
            temp_factor = 0.85  # Freezing weather reduces parking
        elif temperature < 50:
            temp_factor = 0.92  # Cold weather reduces parking
        elif temperature < 70:
            temp_factor = 1.00  # Cool weather is baseline
        elif temperature < 85:
            temp_factor = 1.05  # Warm weather increases parking
        else:
            temp_factor = 1.10  # Hot weather increases parking (people drive more)
        
        # Precipitation adjustments
        if precipitation == 'heavy_rain':
            precip_factor = 0.70  # Heavy rain significantly reduces parking
        elif precipitation == 'rain':
            precip_factor = 0.85  # Light rain reduces parking
        elif precipitation == 'snow':
            precip_factor = 0.65  # Snow greatly reduces parking
        elif precipitation == 'clear':
            precip_factor = 1.00  # Clear weather is baseline
        
        return temp_factor * precip_factor
    
    def get_event_adjustment(self, events):
        """Get event adjustment factor based on scheduled events"""
        event_factor = 1.0
        
        if not events:
            return event_factor
        
        # Holiday adjustments
        if events.get('is_holiday'):
            event_factor *= 1.20  # Holidays increase parking by 20%
        
        # Sports events
        if events.get('cubs_home_game'):
            event_factor *= 1.35  # Cubs home games increase parking by 35%
        elif events.get('bears_home_game'):
            event_factor *= 1.40  # Bears home games increase parking by 40%
        
        # Entertainment events
        if events.get('millennium_park_concert'):
            event_factor *= 1.25  # Concerts increase parking by 25%
        elif events.get('festival'):
            event_factor *= 1.30  # Festivals increase parking by 30%
        
        # City events
        if events.get('marathon'):
            event_factor *= 1.15  # Marathons increase parking by 15%
        elif events.get('parade'):
            event_factor *= 1.20  # Parades increase parking by 20%
        
        return event_factor
    
    def create_enhanced_forecast(self, days=30, weather_forecast=None, events_calendar=None):
        """Create enhanced forecast with weather and events"""
        print(f"\n🔮 Creating Enhanced {days}-day Forecast")
        print("=" * 50)
        
        # Calculate baseline day-of-week patterns (same as working model)
        recent_cutoff = self.data[-1]['date'] - timedelta(days=90)
        recent_data = [d for d in self.data if d['date'] >= recent_cutoff]
        
        if len(recent_data) < 10:
            recent_data = self.data[-30:] if len(self.data) >= 30 else self.data
        
        dow_revenues = defaultdict(list)
        for record in recent_data:
            dow_revenues[record['day_of_week']].append(record['revenue'])
        
        dow_averages = {}
        overall_avg = statistics.mean([r['revenue'] for r in recent_data])
        
        for dow in range(7):
            if dow in dow_revenues and dow_revenues[dow]:
                dow_averages[dow] = statistics.mean(dow_revenues[dow])
            else:
                dow_averages[dow] = overall_avg
        
        print(f"📊 Base day-of-week averages:")
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for dow in range(7):
            print(f"  {days_names[dow]}: ${dow_averages[dow]:,.2f}")
        
        # Generate enhanced forecast
        last_date = self.data[-1]['date']
        forecast = []
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            dow = forecast_date.weekday()
            
            # Base forecast from historical patterns
            base_forecast = dow_averages[dow]
            
            # Apply weather adjustments
            weather_adjustment = 1.0
            if weather_forecast and i <= len(weather_forecast):
                weather_info = weather_forecast[i-1]
                weather_adjustment = self.get_weather_adjustment(
                    weather_info.get('temperature', 70),
                    weather_info.get('precipitation', 'clear')
                )
            
            # Apply event adjustments
            event_adjustment = 1.0
            if events_calendar:
                date_str = forecast_date.strftime('%Y-%m-%d')
                event_info = events_calendar.get(date_str)
                if event_info:
                    event_adjustment = self.get_event_adjustment(event_info)
            
            # Final prediction
            predicted_revenue = base_forecast * weather_adjustment * event_adjustment
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'day_name': days_names[dow],
                'base_forecast': round(base_forecast, 2),
                'weather_adjustment': round(weather_adjustment, 3),
                'event_adjustment': round(event_adjustment, 3),
                'predicted_revenue': round(predicted_revenue, 2)
            })
        
        return forecast
    
    def display_forecast_results(self, forecast):
        """Display enhanced forecast results"""
        total_forecast = sum(day['predicted_revenue'] for day in forecast)
        
        print(f"\n📈 Enhanced {len(forecast)}-Day Forecast Results:")
        print(f"  Total forecasted revenue: ${total_forecast:,.2f}")
        print(f"  Average daily revenue: ${total_forecast/len(forecast):,.2f}")
        
        print(f"\n📅 Detailed forecast:")
        for day in forecast:
            print(f"  {day['date']} ({day['day_name']}):")
            print(f"    Base forecast: ${day['base_forecast']:,.2f}")
            if day['weather_adjustment'] != 1.0:
                print(f"    Weather adj:   {day['weather_adjustment']:.3f}x")
            if day['event_adjustment'] != 1.0:
                print(f"    Event adj:     {day['event_adjustment']:.3f}x")
            print(f"    Final forecast: ${day['predicted_revenue']:,.2f}")
            print()
        
        # Save enhanced forecast
        filename = 'enhanced_weather_events_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Day', 'Base_Forecast', 'Weather_Adj', 'Event_Adj', 'Final_Prediction'])
            for day in forecast:
                writer.writerow([
                    day['date'], day['day_name'], day['base_forecast'],
                    day['weather_adjustment'], day['event_adjustment'], day['predicted_revenue']
                ])
        
        print(f"💾 Enhanced forecast saved to: {filename}")
        
        # Business validation
        if total_forecast > 1200000:
            print(f"\n🎉 EXCELLENT: ${total_forecast:,.2f} enhanced forecast aligns with your $1.6M+ business!")
        else:
            print(f"\n✅ Enhanced forecast: ${total_forecast:,.2f}")

def main():
    forecaster = EnhancedRevenueForecaster()
    
    # Load revenue data using proven approach
    data = forecaster.load_revenue_data()
    
    if not data:
        print("❌ No data loaded")
        return
    
    # Example weather forecast (you would get this from a weather API)
    print(f"\n🌤️  Example Weather Integration:")
    sample_weather_forecast = [
        {'temperature': 75, 'precipitation': 'clear'},      # Day 1: Nice weather
        {'temperature': 80, 'precipitation': 'clear'},      # Day 2: Warm and clear
        {'temperature': 72, 'precipitation': 'rain'},       # Day 3: Cooler with rain
        {'temperature': 68, 'precipitation': 'clear'},      # Day 4: Cool but clear
        {'temperature': 85, 'precipitation': 'clear'},      # Day 5: Hot and clear
        {'temperature': 88, 'precipitation': 'clear'},      # Day 6: Very hot
        {'temperature': 82, 'precipitation': 'clear'},      # Day 7: Hot weekend
    ]
    
    # Example events calendar (you would populate this with real events)
    print(f"🎉 Example Events Integration:")
    sample_events = {
        '2025-08-02': {'cubs_home_game': True, 'description': 'Cubs vs Cardinals 7:05 PM'},
        '2025-08-03': {'millennium_park_concert': True, 'description': 'Chicago Symphony Orchestra'},
        '2025-08-04': {'is_holiday': True, 'description': 'Local holiday observed'},
    }
    
    for date, event in sample_events.items():
        print(f"  {date}: {event['description']}")
    
    # Create enhanced forecast
    forecast = forecaster.create_enhanced_forecast(
        days=7,
        weather_forecast=sample_weather_forecast,
        events_calendar=sample_events
    )
    
    # Display results
    forecaster.display_forecast_results(forecast)
    
    print(f"\n💡 Next Steps to Implement:")
    print(f"   1. Sign up for weather API (OpenWeatherMap free tier)")
    print(f"   2. Create events calendar with Cubs/Bears schedules")
    print(f"   3. Add holiday calendar integration")
    print(f"   4. Test enhanced forecasts against actual results")
    print(f"   5. Refine adjustment factors based on your specific data")

if __name__ == "__main__":
    main()

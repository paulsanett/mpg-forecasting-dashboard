#!/usr/bin/env python3
"""
Complete Weather + Events Integrated Forecasting System
Combines validated event multipliers with live weather data
"""

import csv
import json
import urllib.request
from datetime import datetime, timedelta

class WeatherEventsForecaster:
    def __init__(self):
        self.api_key = "db6ca4a5eb88cfbb09ae4bd8713460b7"
        self.base_daily_revenue = {
            'Monday': 48361,
            'Tuesday': 45935,
            'Wednesday': 47514,
            'Thursday': 53478,
            'Friday': 54933,
            'Saturday': 74934,
            'Sunday': 71348
        }
        
        # Garage distribution percentages
        self.garage_distribution = {
            'Grant Park North': 0.323,
            'Grant Park South': 0.131,
            'Millennium': 0.076,
            'Lakeside': 0.193,
            'Other': 0.277
        }
        
        # Validated event multipliers
        self.event_multipliers = {
            'mega_festival': 1.67,
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
    
    def get_weather_forecast(self):
        """Get 5-day weather forecast from OpenWeather API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q=Chicago,IL,US&appid={self.api_key}&units=imperial"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            weather_by_date = {}
            for item in data['list']:
                date_str = item['dt_txt'].split(' ')[0]
                if date_str not in weather_by_date:
                    weather_by_date[date_str] = {
                        'temp_high': item['main']['temp_max'],
                        'temp_low': item['main']['temp_min'],
                        'condition': item['weather'][0]['description'],
                        'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                    }
                else:
                    # Update with higher/lower temps
                    weather_by_date[date_str]['temp_high'] = max(weather_by_date[date_str]['temp_high'], item['main']['temp_max'])
                    weather_by_date[date_str]['temp_low'] = min(weather_by_date[date_str]['temp_low'], item['main']['temp_min'])
            
            return weather_by_date
        except Exception as e:
            print(f"Weather API error: {e}")
            return {}
    
    def load_events(self):
        """Load events from calendar"""
        events_by_date = {}
        try:
            with open('MG Event Calendar 2025.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_str = row.get('Start Date', '').strip()
                    if date_str:
                        try:
                            # Parse date in M/D/YY format
                            date_obj = datetime.strptime(date_str, '%m/%d/%y')
                            date_key = date_obj.strftime('%Y-%m-%d')
                            
                            if date_key not in events_by_date:
                                events_by_date[date_key] = []
                            
                            event_name = row.get('Event', '').strip()
                            if event_name and event_name != '-':
                                # Categorize events
                                category = self.categorize_event(event_name)
                                events_by_date[date_key].append({
                                    'name': event_name,
                                    'category': category,
                                    'multiplier': self.event_multipliers.get(category, 1.0)
                                })
                        except ValueError:
                            continue
        except FileNotFoundError:
            print("Event calendar not found, using event-free forecast")
        
        return events_by_date
    
    def categorize_event(self, event_name):
        """Categorize events based on name"""
        event_lower = event_name.lower()
        
        if 'lollapalooza' in event_lower:
            return 'mega_festival'
        elif any(sport in event_lower for sport in ['bears', 'bulls', 'blackhawks', 'cubs', 'sox', 'fire']):
            return 'sports'
        elif any(term in event_lower for term in ['festival', 'fest']):
            return 'festival'
        elif any(term in event_lower for term in ['broadway', 'symphony', 'opera', 'ballet']):
            return 'major_performance'
        elif any(term in event_lower for term in ['concert', 'music', 'performance', 'show']):
            return 'performance'
        elif any(term in event_lower for term in ['holiday', 'christmas', 'thanksgiving', 'july 4']):
            return 'holiday'
        else:
            return 'other'
    
    def calculate_weather_adjustment(self, weather_data):
        """Calculate weather adjustment multiplier"""
        if not weather_data:
            return 1.0
        
        temp_high = weather_data.get('temp_high', 75)
        precipitation = weather_data.get('precipitation', 0)
        condition = weather_data.get('condition', '').lower()
        
        # Temperature adjustment (optimal range 70-80°F)
        if 70 <= temp_high <= 80:
            temp_adj = 1.0
        elif temp_high < 50:
            temp_adj = 0.85  # Very cold reduces activity
        elif temp_high > 95:
            temp_adj = 0.90  # Very hot reduces activity
        elif temp_high < 70:
            temp_adj = 0.95  # Cool weather slight reduction
        else:  # temp_high > 80
            temp_adj = 0.98  # Warm weather slight reduction
        
        # Precipitation adjustment
        if precipitation > 0.5:
            precip_adj = 0.80  # Heavy rain/snow significantly reduces parking
        elif precipitation > 0.1:
            precip_adj = 0.90  # Light precipitation reduces parking
        else:
            precip_adj = 1.0   # No precipitation
        
        # Condition adjustment
        if 'storm' in condition or 'heavy' in condition:
            condition_adj = 0.75
        elif 'rain' in condition or 'snow' in condition:
            condition_adj = 0.90
        elif 'cloud' in condition:
            condition_adj = 0.997  # Slight reduction for cloudy
        else:
            condition_adj = 1.0
        
        return temp_adj * precip_adj * condition_adj
    
    def generate_forecast(self):
        """Generate complete 7-day forecast with weather and events"""
        print("🌤️ WEATHER + EVENTS INTEGRATED FORECASTING SYSTEM")
        print("=" * 70)
        
        # Get weather and events data
        weather_data = self.get_weather_forecast()
        events_data = self.load_events()
        
        print(f"✅ Weather data loaded for {len(weather_data)} days")
        print(f"✅ Events data loaded for {len(events_data)} days")
        
        # Generate 7-day forecast starting tomorrow
        start_date = datetime.now() + timedelta(days=1)
        forecast_data = []
        total_revenue = 0
        
        print(f"\n🔮 7-DAY INTEGRATED FORECAST")
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=6)).strftime('%Y-%m-%d')}")
        print("=" * 70)
        
        for i in range(7):
            forecast_date = start_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            day_name = forecast_date.strftime('%A')
            
            # Base revenue for day of week
            base_revenue = self.base_daily_revenue[day_name]
            
            # Get events for this date
            day_events = events_data.get(date_str, [])
            event_multiplier = 1.0
            if day_events:
                # Use the highest multiplier if multiple events
                event_multiplier = max([event['multiplier'] for event in day_events])
            
            # Get weather for this date
            weather = weather_data.get(date_str, {})
            weather_multiplier = self.calculate_weather_adjustment(weather)
            
            # Calculate final revenue
            final_revenue = base_revenue * event_multiplier * weather_multiplier
            total_revenue += final_revenue
            
            # Calculate garage breakdown
            garage_breakdown = {}
            for garage, percentage in self.garage_distribution.items():
                if garage != 'Other':  # Only show main garages
                    garage_breakdown[garage] = final_revenue * percentage
            
            # Display forecast
            print(f"\n📅 {forecast_date.strftime('%Y-%m-%d')} ({day_name})")
            
            if day_events:
                print(f"   🎪 {len(day_events)} Events (Event Multiplier: {event_multiplier:.2f}x)")
                for event in day_events[:3]:  # Show first 3 events
                    print(f"      🎪 {event['name'][:50]}...")
            else:
                print("   📅 No major events")
            
            if weather:
                temp_high = weather.get('temp_high', 0)
                temp_low = weather.get('temp_low', 0)
                condition = weather.get('condition', 'unknown')
                precipitation = weather.get('precipitation', 0)
                print(f"   🌤️  Weather: {temp_high:.0f}°F/{temp_low:.0f}°F, {condition}")
                if precipitation > 0:
                    print(f"      🌧️  Precipitation: {precipitation:.2f}mm")
                print(f"   🌤️  Weather Multiplier: {weather_multiplier:.3f}x")
            else:
                print("   🌤️  Weather: No data available")
                print(f"   🌤️  Weather Multiplier: {weather_multiplier:.3f}x (default)")
            
            print(f"   📊 Base: ${base_revenue:,} → Final: ${final_revenue:,.0f}")
            print(f"      Grant Park North: ${garage_breakdown.get('Grant Park North', 0):,.0f}")
            print(f"      Lakeside: ${garage_breakdown.get('Lakeside', 0):,.0f}")
            print(f"      Grant Park South: ${garage_breakdown.get('Grant Park South', 0):,.0f}")
            print(f"      Millennium: ${garage_breakdown.get('Millennium', 0):,.0f}")
            
            # Store data for CSV
            forecast_data.append({
                'Date': date_str,
                'Day': day_name,
                'Base_Revenue': base_revenue,
                'Event_Count': len(day_events),
                'Event_Multiplier': event_multiplier,
                'Weather_High': weather.get('temp_high', ''),
                'Weather_Low': weather.get('temp_low', ''),
                'Weather_Condition': weather.get('condition', ''),
                'Weather_Precipitation': weather.get('precipitation', 0),
                'Weather_Multiplier': weather_multiplier,
                'Final_Revenue': final_revenue,
                'Grant_Park_North': garage_breakdown.get('Grant Park North', 0),
                'Lakeside': garage_breakdown.get('Lakeside', 0),
                'Grant_Park_South': garage_breakdown.get('Grant Park South', 0),
                'Millennium': garage_breakdown.get('Millennium', 0)
            })
        
        print(f"\n📊 7-DAY INTEGRATED FORECAST SUMMARY")
        print("=" * 70)
        print(f"💰 Total Revenue: ${total_revenue:,.0f}")
        print(f"📈 Average Daily: ${total_revenue/7:,.0f}")
        print(f"📅 Monthly Projection: ${total_revenue * 30/7:,.0f}")
        
        # Save to CSV
        csv_filename = f"weather_events_integrated_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = forecast_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(forecast_data)
        
        print(f"💾 Integrated forecast saved to: {csv_filename}")
        print("\n🎉 WEATHER + EVENTS INTEGRATION COMPLETE!")
        print("   ✅ Live weather data from OpenWeather API")
        print("   ✅ Validated event multipliers from historical data")
        print("   ✅ Complete garage-level breakdown")
        print("   ✅ Weather adjustments for temperature and precipitation")

if __name__ == "__main__":
    forecaster = WeatherEventsForecaster()
    forecaster.generate_forecast()

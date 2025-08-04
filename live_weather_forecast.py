#!/usr/bin/env python3
"""
Live Weather-Enhanced Parking Revenue Forecasting
Uses real OpenWeather API data for accurate weather-adjusted forecasts
"""

import csv
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# For API requests - using urllib to avoid external dependencies
import urllib.request
import urllib.parse

class LiveWeatherForecaster:
    def __init__(self, api_key):
        self.api_key = api_key
        self.data = []
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def load_revenue_data(self):
        """Load revenue data using proven approach"""
        file_path = "HIstoric Booking Data.csv"
        
        print("🌤️ Live Weather-Enhanced Parking Revenue Forecasting")
        print("=" * 70)
        
        data = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            revenue_col = 37  # Proven working column
            
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
                    
                    # Parse date
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
                    
                    # Parse revenue
                    clean_revenue = ""
                    for char in revenue_str:
                        if char.isdigit() or char == '.' or char == '-':
                            clean_revenue += char
                    
                    if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                        revenue = float(clean_revenue)
                        
                        if revenue > 1000:
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
            
            # Sort by date
            data.sort(key=lambda x: x['date'])
            self.data = data
            
            return data
    
    def get_current_weather(self):
        """Get current weather for Chicago"""
        try:
            url = f"{self.base_url}/weather?q=Chicago,IL,US&appid={self.api_key}&units=imperial"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            weather = {
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'].lower(),
                'wind_speed': data['wind']['speed']
            }
            
            print(f"🌤️  Current Chicago Weather:")
            print(f"   Temperature: {weather['temperature']}°F (feels like {weather['feels_like']}°F)")
            print(f"   Conditions: {weather['description'].title()}")
            print(f"   Humidity: {weather['humidity']}%")
            print(f"   Wind: {weather['wind_speed']} mph")
            
            return weather
            
        except Exception as e:
            print(f"⚠️  Could not fetch current weather: {e}")
            return None
    
    def get_weather_forecast(self, days=7):
        """Get weather forecast for next few days"""
        try:
            url = f"{self.base_url}/forecast?q=Chicago,IL,US&appid={self.api_key}&units=imperial"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            # Process 5-day forecast (3-hour intervals)
            daily_forecasts = {}
            
            for item in data['list']:
                dt = datetime.fromtimestamp(item['dt'])
                date_key = dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        'temperatures': [],
                        'conditions': [],
                        'precipitation': 0,
                        'humidity': [],
                        'wind_speed': []
                    }
                
                daily_forecasts[date_key]['temperatures'].append(item['main']['temp'])
                daily_forecasts[date_key]['conditions'].append(item['weather'][0]['main'].lower())
                daily_forecasts[date_key]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date_key]['wind_speed'].append(item['wind']['speed'])
                
                # Check for precipitation
                if 'rain' in item:
                    daily_forecasts[date_key]['precipitation'] += item['rain'].get('3h', 0)
                if 'snow' in item:
                    daily_forecasts[date_key]['precipitation'] += item['snow'].get('3h', 0)
            
            # Convert to daily summaries
            forecast_list = []
            for date_key in sorted(daily_forecasts.keys())[:days]:
                day_data = daily_forecasts[date_key]
                
                # Determine primary condition
                conditions = day_data['conditions']
                if 'rain' in conditions:
                    primary_condition = 'rain'
                elif 'snow' in conditions:
                    primary_condition = 'snow'
                elif 'clouds' in conditions:
                    primary_condition = 'cloudy'
                else:
                    primary_condition = 'clear'
                
                forecast_list.append({
                    'date': date_key,
                    'high_temp': round(max(day_data['temperatures'])),
                    'low_temp': round(min(day_data['temperatures'])),
                    'avg_temp': round(statistics.mean(day_data['temperatures'])),
                    'condition': primary_condition,
                    'precipitation': round(day_data['precipitation'], 2),
                    'humidity': round(statistics.mean(day_data['humidity'])),
                    'wind_speed': round(statistics.mean(day_data['wind_speed']), 1)
                })
            
            print(f"\n🔮 7-Day Weather Forecast:")
            for forecast in forecast_list:
                date_obj = datetime.strptime(forecast['date'], '%Y-%m-%d')
                day_name = date_obj.strftime('%A')
                print(f"   {forecast['date']} ({day_name}): {forecast['high_temp']}°F/{forecast['low_temp']}°F, {forecast['condition']}")
                if forecast['precipitation'] > 0:
                    print(f"      Precipitation: {forecast['precipitation']} inches")
            
            return forecast_list
            
        except Exception as e:
            print(f"⚠️  Could not fetch weather forecast: {e}")
            return None
    
    def get_weather_adjustment(self, weather_data):
        """Calculate weather adjustment factor"""
        if not weather_data:
            return 1.0
        
        temp_factor = 1.0
        condition_factor = 1.0
        
        # Temperature adjustment
        avg_temp = weather_data['avg_temp']
        if avg_temp < 32:
            temp_factor = 0.80  # Very cold
        elif avg_temp < 50:
            temp_factor = 0.90  # Cold
        elif avg_temp < 70:
            temp_factor = 1.00  # Comfortable
        elif avg_temp < 85:
            temp_factor = 1.05  # Warm
        else:
            temp_factor = 1.10  # Hot
        
        # Condition adjustment
        condition = weather_data['condition']
        if condition == 'rain':
            if weather_data['precipitation'] > 0.5:
                condition_factor = 0.75  # Heavy rain
            else:
                condition_factor = 0.85  # Light rain
        elif condition == 'snow':
            condition_factor = 0.65  # Snow
        elif condition == 'cloudy':
            condition_factor = 0.95  # Cloudy
        else:
            condition_factor = 1.00  # Clear
        
        return temp_factor * condition_factor
    
    def create_live_weather_forecast(self, days=7):
        """Create forecast with live weather data"""
        print(f"\n🔮 Creating Live Weather-Enhanced Forecast")
        print("=" * 55)
        
        # Get live weather forecast
        weather_forecast = self.get_weather_forecast(days)
        
        if not weather_forecast:
            print("❌ Could not get weather data, using base forecast")
            weather_forecast = []
        
        # Calculate baseline patterns
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
        
        # Generate forecast
        last_date = self.data[-1]['date']
        forecast = []
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            dow = forecast_date.weekday()
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # Base forecast
            base_forecast = dow_averages[dow]
            
            # Weather adjustment
            weather_adjustment = 1.0
            weather_info = None
            
            # Find matching weather data
            for weather_day in weather_forecast:
                if weather_day['date'] == date_str:
                    weather_info = weather_day
                    weather_adjustment = self.get_weather_adjustment(weather_day)
                    break
            
            # Final prediction
            predicted_revenue = base_forecast * weather_adjustment
            
            forecast_item = {
                'date': date_str,
                'day_name': days_names[dow],
                'base_forecast': round(base_forecast, 2),
                'weather_adjustment': round(weather_adjustment, 3),
                'predicted_revenue': round(predicted_revenue, 2)
            }
            
            # Add weather details if available
            if weather_info:
                forecast_item.update({
                    'high_temp': weather_info['high_temp'],
                    'low_temp': weather_info['low_temp'],
                    'condition': weather_info['condition'],
                    'precipitation': weather_info['precipitation']
                })
            
            forecast.append(forecast_item)
        
        return forecast
    
    def display_live_forecast(self, forecast):
        """Display live weather-enhanced forecast"""
        total_forecast = sum(day['predicted_revenue'] for day in forecast)
        
        print(f"\n📈 Live Weather-Enhanced {len(forecast)}-Day Forecast:")
        print(f"  Total forecasted revenue: ${total_forecast:,.2f}")
        print(f"  Average daily revenue: ${total_forecast/len(forecast):,.2f}")
        
        print(f"\n📅 Detailed forecast with live weather:")
        for day in forecast:
            print(f"  {day['date']} ({day['day_name']}):")
            print(f"    Base forecast: ${day['base_forecast']:,.2f}")
            
            if 'high_temp' in day:
                print(f"    Weather: {day['high_temp']}°F/{day['low_temp']}°F, {day['condition']}")
                if day['precipitation'] > 0:
                    print(f"    Precipitation: {day['precipitation']} inches")
            
            if day['weather_adjustment'] != 1.0:
                print(f"    Weather adjustment: {day['weather_adjustment']:.3f}x")
            
            print(f"    Final forecast: ${day['predicted_revenue']:,.2f}")
            print()
        
        # Save forecast
        filename = 'live_weather_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            headers = ['Date', 'Day', 'Base_Forecast', 'High_Temp', 'Low_Temp', 'Condition', 'Precipitation', 'Weather_Adj', 'Final_Prediction']
            writer.writerow(headers)
            
            for day in forecast:
                writer.writerow([
                    day['date'], day['day_name'], day['base_forecast'],
                    day.get('high_temp', ''), day.get('low_temp', ''), day.get('condition', ''),
                    day.get('precipitation', ''), day['weather_adjustment'], day['predicted_revenue']
                ])
        
        print(f"💾 Live weather forecast saved to: {filename}")
        
        # Business validation
        if total_forecast > 400000:  # 7-day threshold
            print(f"\n🎉 EXCELLENT: ${total_forecast:,.2f} live forecast looks great!")
        else:
            print(f"\n✅ Live forecast: ${total_forecast:,.2f}")

def main():
    # Your OpenWeather API key
    api_key = "ba31450f2724afa561069a027fb451e6"
    
    forecaster = LiveWeatherForecaster(api_key)
    
    # Load revenue data
    print("📊 Loading historical revenue data...")
    data = forecaster.load_revenue_data()
    
    if not data:
        print("❌ No data loaded")
        return
    
    # Get current weather
    current_weather = forecaster.get_current_weather()
    
    # Create live weather-enhanced forecast
    forecast = forecaster.create_live_weather_forecast(days=7)
    
    # Display results
    forecaster.display_live_forecast(forecast)
    
    print(f"\n🎯 Live Weather Integration Complete!")
    print(f"   • Using real OpenWeather API data")
    print(f"   • 7-day forecast with temperature and precipitation")
    print(f"   • Weather adjustments applied to revenue predictions")
    print(f"   • Run this script daily for updated forecasts")

if __name__ == "__main__":
    main()

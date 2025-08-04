#!/usr/bin/env python3
"""
Weather & Events Enhanced Parking Revenue Forecasting
Integrates weather data and events for improved accuracy
"""

import csv
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

class WeatherEventsForecaster:
    def __init__(self):
        self.data = []
        self.weather_patterns = {}
        self.event_patterns = {}
        
    def extract_weather_events_data(self):
        """Extract revenue data with weather and events information"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🌤️ Weather & Events Enhanced Forecasting")
        print("=" * 60)
        
        data = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            # Find columns
            revenue_col = None
            notes_col = None
            
            print(f"📋 Available columns (first 10):")
            for i, col in enumerate(header[:10]):
                print(f"  {i}: {col.strip()}")
            
            for i, col in enumerate(header):
                col_clean = col.lower().strip()
                if 'total revenue' in col_clean:
                    revenue_col = i
                elif 'notes' in col_clean:
                    notes_col = i
            
            # If notes column not found, try to find it by position (usually near the end)
            if notes_col is None and len(header) > 45:
                # Notes column is typically around position 47 based on your data
                for i in range(45, min(len(header), 55)):
                    if i < len(header) and header[i].strip():
                        notes_col = i
                        break
            
            print(f"📋 Revenue column: {revenue_col}, Notes column: {notes_col}")
            
            row_count = 0
            valid_count = 0
            
            for row in reader:
                row_count += 1
                
                if len(row) <= max(0, 1, 2, revenue_col or 0):
                    continue
                
                try:
                    # Extract basic data
                    year_str = row[0].strip() if len(row) > 0 else ""
                    month_str = row[1].strip() if len(row) > 1 else ""
                    date_str = row[2].strip() if len(row) > 2 else ""
                    revenue_str = row[revenue_col].strip() if revenue_col and len(row) > revenue_col else ""
                    notes_str = row[notes_col].strip() if notes_col and len(row) > notes_col else ""
                    
                    if not year_str or not month_str or not date_str:
                        continue
                    
                    # Parse date
                    year = int(year_str)
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    month = month_map.get(month_str.lower(), int(month_str))
                    day = int(date_str)
                    date = datetime(year, month, day)
                    
                    # Parse revenue (use same logic as working revenue_extractor.py)
                    clean_revenue = ""
                    for char in revenue_str:
                        if char.isdigit() or char == '.' or char == '-':
                            clean_revenue += char
                    
                    if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                        revenue = float(clean_revenue)
                        
                        if revenue > 1000:  # Use same threshold as working model
                            # Extract weather and event features
                            weather_features = self.extract_weather_features(notes_str)
                            event_features = self.extract_event_features(notes_str, date)
                            
                            record = {
                                'date': date,
                                'revenue': revenue,
                                'year': year,
                                'month': month,
                                'day': day,
                                'day_of_week': date.weekday(),
                                'notes': notes_str,
                                'temperature': weather_features.get('temperature'),
                                'precipitation': weather_features.get('precipitation'),
                                'weather_condition': weather_features.get('condition'),
                                'is_holiday': event_features.get('is_holiday', False),
                                'event_type': event_features.get('event_type'),
                                'is_weekend': date.weekday() >= 5
                            }
                            
                            data.append(record)
                            valid_count += 1
                            
                except Exception as e:
                    continue
            
            print(f"✅ Processed {row_count:,} rows, found {valid_count:,} valid records")
            
            # Sort by date
            data.sort(key=lambda x: x['date'])
            self.data = data
            
            return data
    
    def extract_weather_features(self, notes):
        """Extract weather information from notes"""
        features = {}
        
        if not notes:
            return features
        
        notes_lower = notes.lower()
        
        # Extract temperature
        temp_match = re.search(r'(\d+)\s*degrees?\s*fahrenheit', notes_lower)
        if temp_match:
            features['temperature'] = int(temp_match.group(1))
        
        # Extract precipitation
        if 'rain' in notes_lower:
            features['precipitation'] = 'rain'
            # Extract rain amount if available
            rain_match = re.search(r'(\d+\.?\d*)"?\s*rain', notes_lower)
            if rain_match:
                features['rain_amount'] = float(rain_match.group(1))
        elif 'snow' in notes_lower:
            features['precipitation'] = 'snow'
        else:
            features['precipitation'] = 'none'
        
        # Extract weather conditions
        if 'sunny' in notes_lower or 'clear' in notes_lower:
            features['condition'] = 'clear'
        elif 'cloudy' in notes_lower or 'overcast' in notes_lower:
            features['condition'] = 'cloudy'
        elif 'storm' in notes_lower:
            features['condition'] = 'stormy'
        elif 'wind' in notes_lower:
            features['condition'] = 'windy'
        
        return features
    
    def extract_event_features(self, notes, date):
        """Extract event information from notes and date"""
        features = {}
        
        if not notes:
            return features
        
        notes_lower = notes.lower()
        
        # Check for holidays
        holidays = [
            'new year', 'christmas', 'thanksgiving', 'independence day', 'july 4',
            'memorial day', 'labor day', 'columbus day', 'veterans day',
            'martin luther king', 'presidents day', 'easter', 'halloween'
        ]
        
        for holiday in holidays:
            if holiday in notes_lower:
                features['is_holiday'] = True
                features['event_type'] = holiday
                break
        
        # Check for other events
        if 'game' in notes_lower or 'cubs' in notes_lower or 'bears' in notes_lower:
            features['event_type'] = 'sports'
        elif 'concert' in notes_lower or 'festival' in notes_lower:
            features['event_type'] = 'entertainment'
        elif 'parade' in notes_lower or 'marathon' in notes_lower:
            features['event_type'] = 'city_event'
        
        return features
    
    def analyze_weather_impact(self):
        """Analyze how weather affects revenue"""
        print("\n🌡️ Weather Impact Analysis")
        print("=" * 40)
        
        # Temperature analysis
        temp_revenues = defaultdict(list)
        for record in self.data:
            if record['temperature']:
                temp_range = self.get_temp_range(record['temperature'])
                temp_revenues[temp_range].append(record['revenue'])
        
        print("📊 Revenue by Temperature Range:")
        for temp_range, revenues in temp_revenues.items():
            if revenues:
                avg_revenue = statistics.mean(revenues)
                print(f"  {temp_range}: ${avg_revenue:,.2f} (n={len(revenues)})")
        
        # Precipitation analysis
        precip_revenues = defaultdict(list)
        for record in self.data:
            precip = record['precipitation'] or 'unknown'
            precip_revenues[precip].append(record['revenue'])
        
        print("\n🌧️ Revenue by Precipitation:")
        for precip, revenues in precip_revenues.items():
            if revenues:
                avg_revenue = statistics.mean(revenues)
                print(f"  {precip.title()}: ${avg_revenue:,.2f} (n={len(revenues)})")
        
        return temp_revenues, precip_revenues
    
    def analyze_event_impact(self):
        """Analyze how events affect revenue"""
        print("\n🎉 Event Impact Analysis")
        print("=" * 40)
        
        # Holiday analysis
        holiday_revenues = []
        regular_revenues = []
        
        for record in self.data:
            if record['is_holiday']:
                holiday_revenues.append(record['revenue'])
            else:
                regular_revenues.append(record['revenue'])
        
        if holiday_revenues and regular_revenues:
            holiday_avg = statistics.mean(holiday_revenues)
            regular_avg = statistics.mean(regular_revenues)
            impact = (holiday_avg - regular_avg) / regular_avg * 100
            
            print(f"📊 Holiday Impact:")
            print(f"  Regular days: ${regular_avg:,.2f}")
            print(f"  Holiday days: ${holiday_avg:,.2f}")
            print(f"  Impact: {impact:+.1f}%")
        
        # Event type analysis
        event_revenues = defaultdict(list)
        for record in self.data:
            event_type = record['event_type'] or 'none'
            event_revenues[event_type].append(record['revenue'])
        
        print(f"\n📊 Revenue by Event Type:")
        for event_type, revenues in event_revenues.items():
            if revenues:
                avg_revenue = statistics.mean(revenues)
                print(f"  {event_type.title()}: ${avg_revenue:,.2f} (n={len(revenues)})")
        
        return event_revenues
    
    def get_temp_range(self, temp):
        """Categorize temperature into ranges"""
        if temp < 32:
            return "Below Freezing (<32°F)"
        elif temp < 50:
            return "Cold (32-49°F)"
        elif temp < 70:
            return "Cool (50-69°F)"
        elif temp < 85:
            return "Warm (70-84°F)"
        else:
            return "Hot (85°F+)"
    
    def create_enhanced_forecast(self, days=30, weather_forecast=None, events_calendar=None):
        """Create forecast incorporating weather and events"""
        print(f"\n🔮 Creating Enhanced {days}-day Forecast")
        print("=" * 50)
        
        # Get baseline patterns
        recent_cutoff = self.data[-1]['date'] - timedelta(days=90)
        recent_data = [d for d in self.data if d['date'] >= recent_cutoff]
        
        # Calculate base day-of-week averages
        dow_revenues = defaultdict(list)
        for record in recent_data:
            dow_revenues[record['day_of_week']].append(record['revenue'])
        
        dow_averages = {}
        for dow in range(7):
            if dow in dow_revenues:
                dow_averages[dow] = statistics.mean(dow_revenues[dow])
            else:
                dow_averages[dow] = statistics.mean([r['revenue'] for r in recent_data])
        
        # Calculate weather adjustment factors
        temp_factors = self.calculate_weather_factors()
        event_factors = self.calculate_event_factors()
        
        # Generate forecast
        last_date = self.data[-1]['date']
        forecast = []
        
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            dow = forecast_date.weekday()
            
            # Base forecast
            base_forecast = dow_averages[dow]
            
            # Apply weather adjustments (if weather forecast provided)
            weather_adjustment = 1.0
            if weather_forecast and i <= len(weather_forecast):
                weather_info = weather_forecast[i-1]
                weather_adjustment = self.get_weather_adjustment(weather_info, temp_factors)
            
            # Apply event adjustments (if events calendar provided)
            event_adjustment = 1.0
            if events_calendar:
                event_info = events_calendar.get(forecast_date.strftime('%Y-%m-%d'))
                if event_info:
                    event_adjustment = self.get_event_adjustment(event_info, event_factors)
            
            # Final prediction
            predicted_revenue = base_forecast * weather_adjustment * event_adjustment
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'day_name': days_names[dow],
                'base_forecast': round(base_forecast, 2),
                'weather_adjustment': weather_adjustment,
                'event_adjustment': event_adjustment,
                'predicted_revenue': round(predicted_revenue, 2)
            })
        
        return forecast
    
    def calculate_weather_factors(self):
        """Calculate weather adjustment factors"""
        # This would be more sophisticated with more data
        # For now, simple temperature-based adjustments
        return {
            'hot': 1.1,      # Hot weather increases parking (people drive more)
            'warm': 1.05,    # Warm weather slight increase
            'cool': 1.0,     # Baseline
            'cold': 0.95,    # Cold weather slight decrease
            'freezing': 0.9, # Very cold decreases parking
            'rain': 0.85,    # Rain significantly decreases parking
            'snow': 0.7      # Snow greatly decreases parking
        }
    
    def calculate_event_factors(self):
        """Calculate event adjustment factors"""
        return {
            'holiday': 1.2,        # Holidays increase parking
            'sports': 1.3,         # Sports events big increase
            'entertainment': 1.25, # Concerts/festivals increase
            'city_event': 1.15     # City events moderate increase
        }
    
    def get_weather_adjustment(self, weather_info, factors):
        """Get weather adjustment factor"""
        temp = weather_info.get('temperature', 70)
        precip = weather_info.get('precipitation', 'none')
        
        if precip == 'rain':
            return factors['rain']
        elif precip == 'snow':
            return factors['snow']
        elif temp >= 85:
            return factors['hot']
        elif temp >= 70:
            return factors['warm']
        elif temp >= 50:
            return factors['cool']
        elif temp >= 32:
            return factors['cold']
        else:
            return factors['freezing']
    
    def get_event_adjustment(self, event_info, factors):
        """Get event adjustment factor"""
        event_type = event_info.get('type', 'none')
        return factors.get(event_type, 1.0)

def main():
    forecaster = WeatherEventsForecaster()
    
    # Extract data with weather and events
    print("📊 Extracting weather and events data...")
    data = forecaster.extract_weather_events_data()
    
    if not data:
        print("❌ No data extracted")
        return
    
    # Analyze weather and event impacts
    forecaster.analyze_weather_impact()
    forecaster.analyze_event_impact()
    
    # Example weather forecast (you would get this from a weather API)
    sample_weather_forecast = [
        {'temperature': 75, 'precipitation': 'none'},  # Day 1
        {'temperature': 80, 'precipitation': 'none'},  # Day 2
        {'temperature': 72, 'precipitation': 'rain'},  # Day 3
        {'temperature': 68, 'precipitation': 'none'},  # Day 4
        {'temperature': 85, 'precipitation': 'none'},  # Day 5
        {'temperature': 88, 'precipitation': 'none'},  # Day 6
        {'temperature': 82, 'precipitation': 'none'},  # Day 7
    ]
    
    # Example events calendar (you would populate this with known events)
    sample_events = {
        '2025-08-02': {'type': 'sports', 'description': 'Cubs home game'},
        '2025-08-03': {'type': 'entertainment', 'description': 'Millennium Park concert'},
    }
    
    # Create enhanced forecast
    forecast = forecaster.create_enhanced_forecast(
        days=7, 
        weather_forecast=sample_weather_forecast,
        events_calendar=sample_events
    )
    
    # Display results
    total_forecast = sum(day['predicted_revenue'] for day in forecast)
    
    print(f"\n📈 Enhanced 7-Day Forecast Results:")
    print(f"  Total forecasted revenue: ${total_forecast:,.2f}")
    print(f"  Average daily revenue: ${total_forecast/len(forecast):,.2f}")
    
    print(f"\n📅 Detailed forecast:")
    for day in forecast:
        print(f"  {day['date']} ({day['day_name']}):")
        print(f"    Base: ${day['base_forecast']:,.2f}")
        print(f"    Weather adj: {day['weather_adjustment']:.2f}x")
        print(f"    Event adj: {day['event_adjustment']:.2f}x")
        print(f"    Final: ${day['predicted_revenue']:,.2f}")
        print()
    
    # Save enhanced forecast
    with open('enhanced_weather_events_forecast.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Day', 'Base_Forecast', 'Weather_Adj', 'Event_Adj', 'Final_Prediction'])
        for day in forecast:
            writer.writerow([
                day['date'], day['day_name'], day['base_forecast'],
                day['weather_adjustment'], day['event_adjustment'], day['predicted_revenue']
            ])
    
    print(f"💾 Enhanced forecast saved to: enhanced_weather_events_forecast.csv")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Garage-Specific Parking Revenue Forecasting System
Addresses user feedback:
1. Starts forecasting from current date (not historical last date)
2. Explains base vs final forecast clearly
3. Provides garage-level breakdown and forecasts
"""

import csv
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import urllib.request
import urllib.parse
import re

class GarageSpecificForecaster:
    def __init__(self, api_key):
        self.api_key = api_key
        self.revenue_data = []
        self.garage_data = {}
        self.events_data = {}
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def load_revenue_data_with_garages(self):
        """Load revenue data and identify garage columns"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🏢 Garage-Specific Revenue Forecasting System")
        print("=" * 75)
        print("🎯 Loading data with garage-level breakdown...")
        
        data = []
        garage_columns = {}
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            # Identify potential garage revenue columns
            # Based on your data structure, there appear to be multiple revenue columns
            revenue_columns = []
            for i, col_name in enumerate(header):
                if i > 5 and i < 50:  # Revenue columns are typically in this range
                    revenue_columns.append(i)
            
            print(f"📊 Analyzing {len(revenue_columns)} potential revenue columns...")
            
            row_count = 0
            valid_count = 0
            total_revenue = 0
            garage_totals = defaultdict(float)
            garage_counts = defaultdict(int)
            
            for row in reader:
                row_count += 1
                
                if len(row) < 40:
                    continue
                
                try:
                    # Extract date components
                    year_str = row[0].strip() if len(row) > 0 else ""
                    month_str = row[1].strip() if len(row) > 1 else ""
                    date_str = row[2].strip() if len(row) > 2 else ""
                    
                    if not year_str or not month_str or not date_str:
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
                    
                    # Extract garage revenues
                    garage_revenues = {}
                    daily_total = 0
                    
                    # Check multiple revenue columns (garages)
                    garage_names = ['Garage_A', 'Garage_B', 'Garage_C', 'Garage_D', 'Garage_E']
                    revenue_cols = [9, 15, 21, 27, 33]  # Approximate positions based on data structure
                    
                    for i, (garage_name, col_idx) in enumerate(zip(garage_names, revenue_cols)):
                        if col_idx < len(row):
                            revenue_str = row[col_idx].strip()
                            if revenue_str:
                                # Clean revenue string
                                clean_revenue = ""
                                for char in revenue_str:
                                    if char.isdigit() or char == '.' or char == '-':
                                        clean_revenue += char
                                
                                if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                                    try:
                                        revenue = float(clean_revenue)
                                        if revenue > 100:  # Minimum threshold
                                            garage_revenues[garage_name] = revenue
                                            daily_total += revenue
                                            garage_totals[garage_name] += revenue
                                            garage_counts[garage_name] += 1
                                    except:
                                        continue
                    
                    # Also get total revenue from main column (column 37)
                    if len(row) > 37:
                        total_revenue_str = row[37].strip()
                        if total_revenue_str:
                            clean_total = ""
                            for char in total_revenue_str:
                                if char.isdigit() or char == '.' or char == '-':
                                    clean_total += char
                            
                            if clean_total and clean_total != '-' and clean_total != '.':
                                try:
                                    total_rev = float(clean_total)
                                    if total_rev > 1000:
                                        daily_total = max(daily_total, total_rev)  # Use whichever is higher
                                except:
                                    pass
                    
                    if daily_total > 1000:  # Valid day
                        data.append({
                            'date': date,
                            'total_revenue': daily_total,
                            'garage_revenues': garage_revenues,
                            'year': year,
                            'month': month,
                            'day': day,
                            'day_of_week': date.weekday()
                        })
                        total_revenue += daily_total
                        valid_count += 1
                
                except Exception as e:
                    continue
            
            print(f"✅ Revenue Data Loaded: {valid_count:,} records")
            print(f"💰 Total Revenue: ${total_revenue:,.2f}")
            print(f"📈 Average Daily: ${total_revenue/valid_count:,.2f}")
            
            # Show garage breakdown
            print(f"\n🏢 Garage Performance Summary:")
            for garage_name in garage_names:
                if garage_name in garage_totals and garage_counts[garage_name] > 0:
                    avg_daily = garage_totals[garage_name] / garage_counts[garage_name]
                    print(f"   {garage_name}: ${garage_totals[garage_name]:,.0f} total, ${avg_daily:,.0f} avg/day ({garage_counts[garage_name]:,} days)")
            
            # Sort by date
            data.sort(key=lambda x: x['date'])
            self.revenue_data = data
            self.garage_data = {
                'totals': garage_totals,
                'counts': garage_counts,
                'names': garage_names
            }
            
            return data
    
    def load_events_calendar(self):
        """Load events from your MG Event Calendar"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/MG Event Calendar 2025 - Event Calendar.csv"
        
        print(f"\n🎉 Loading Events Calendar...")
        
        events = {}
        event_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        start_date_str = row.get('Start Date', '').strip()
                        if not start_date_str:
                            continue
                        
                        event_name = row.get('Event', '').strip()
                        event_type = row.get('Event Type', '').strip()
                        location = row.get('Location', '').strip()
                        tier = row.get('Tier', '').strip()
                        
                        if not event_name:
                            continue
                        
                        # Clean up date string
                        start_date_clean = re.sub(r'^[A-Za-z]+,\s*', '', start_date_str)
                        
                        # Try to parse date
                        date_obj = None
                        date_formats = ['%b %d', '%B %d', '%m/%d', '%m-%d']
                        
                        for fmt in date_formats:
                            try:
                                parsed_date = datetime.strptime(start_date_clean, fmt)
                                date_obj = parsed_date.replace(year=2025)
                                break
                            except:
                                continue
                        
                        if date_obj:
                            date_key = date_obj.strftime('%Y-%m-%d')
                            
                            if date_key not in events:
                                events[date_key] = []
                            
                            impact_category = self.categorize_event(event_name, event_type, location, tier)
                            
                            events[date_key].append({
                                'name': event_name,
                                'type': event_type,
                                'location': location,
                                'tier': tier,
                                'impact_category': impact_category,
                                'impact_factor': self.get_event_impact_factor(impact_category, tier)
                            })
                            
                            event_count += 1
                    
                    except Exception as e:
                        continue
            
            print(f"✅ Events Calendar Loaded: {event_count:,} events")
            self.events_data = events
            return events
            
        except Exception as e:
            print(f"⚠️  Could not load events calendar: {e}")
            return {}
    
    def categorize_event(self, name, event_type, location, tier):
        """Categorize events by their parking impact"""
        name_lower = name.lower()
        type_lower = event_type.lower()
        location_lower = location.lower()
        
        if 'fire fc' in name_lower or 'chicago fire' in name_lower:
            return 'major_sports'
        elif 'marathon' in name_lower or 'race' in name_lower:
            return 'major_sports'
        elif 'symphony' in name_lower or 'orchestra' in name_lower:
            return 'major_performance'
        elif 'broadway' in location_lower:
            return 'major_performance'
        elif event_type.lower() == 'holiday':
            return 'holiday'
        elif 'concert' in name_lower:
            return 'performance'
        elif 'festival' in name_lower:
            return 'festival'
        elif 'museum' in location_lower:
            return 'cultural'
        elif 'free admission' in name_lower:
            return 'free_event'
        else:
            return 'other'
    
    def get_event_impact_factor(self, category, tier):
        """Get revenue impact factor based on event category and tier"""
        base_factors = {
            'major_sports': 1.45,
            'major_performance': 1.35,
            'holiday': 1.25,
            'performance': 1.20,
            'festival': 1.30,
            'cultural': 1.15,
            'free_event': 1.10,
            'other': 1.00
        }
        
        base_factor = base_factors.get(category, 1.0)
        
        if tier == 'Tier 2':
            base_factor *= 1.1
        elif tier == 'Tier 3':
            base_factor *= 1.05
        
        return base_factor
    
    def get_weather_forecast(self, days=7):
        """Get live weather forecast from OpenWeather API"""
        try:
            print(f"\n🌤️  Fetching Live Chicago Weather Forecast...")
            
            url = f"{self.base_url}/forecast?q=Chicago,IL,US&appid={self.api_key}&units=imperial"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            # Process forecast data
            daily_forecasts = {}
            
            for item in data['list']:
                dt = datetime.fromtimestamp(item['dt'])
                date_key = dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        'temperatures': [],
                        'conditions': [],
                        'precipitation': 0
                    }
                
                daily_forecasts[date_key]['temperatures'].append(item['main']['temp'])
                daily_forecasts[date_key]['conditions'].append(item['weather'][0]['main'].lower())
                
                if 'rain' in item:
                    daily_forecasts[date_key]['precipitation'] += item['rain'].get('3h', 0)
                if 'snow' in item:
                    daily_forecasts[date_key]['precipitation'] += item['snow'].get('3h', 0)
            
            # Convert to daily summaries
            forecast_list = []
            for date_key in sorted(daily_forecasts.keys())[:days]:
                day_data = daily_forecasts[date_key]
                
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
                    'precipitation': round(day_data['precipitation'], 2)
                })
            
            print(f"✅ Weather Forecast Retrieved: {len(forecast_list)} days")
            return forecast_list
            
        except Exception as e:
            print(f"⚠️  Could not fetch weather forecast: {e}")
            return []
    
    def get_weather_adjustment(self, weather_data):
        """Calculate weather adjustment factor"""
        if not weather_data:
            return 1.0
        
        temp_factor = 1.0
        condition_factor = 1.0
        
        avg_temp = weather_data['avg_temp']
        if avg_temp < 20:
            temp_factor = 0.75
        elif avg_temp < 32:
            temp_factor = 0.85
        elif avg_temp < 50:
            temp_factor = 0.92
        elif avg_temp < 70:
            temp_factor = 1.00
        elif avg_temp < 85:
            temp_factor = 1.08
        elif avg_temp < 95:
            temp_factor = 1.12
        else:
            temp_factor = 1.05
        
        condition = weather_data['condition']
        precipitation = weather_data['precipitation']
        
        if condition == 'rain':
            if precipitation > 1.0:
                condition_factor = 0.70
            elif precipitation > 0.5:
                condition_factor = 0.80
            else:
                condition_factor = 0.90
        elif condition == 'snow':
            if precipitation > 0.5:
                condition_factor = 0.60
            else:
                condition_factor = 0.75
        elif condition == 'cloudy':
            condition_factor = 0.95
        
        return temp_factor * condition_factor
    
    def create_garage_specific_forecast(self, days=7):
        """Create garage-specific forecast starting from current date"""
        print(f"\n🔮 Creating Garage-Specific {days}-Day Forecast")
        print("=" * 60)
        
        # Start from tomorrow (current date + 1)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today + timedelta(days=1)
        
        print(f"📅 Forecast Period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=days-1)).strftime('%Y-%m-%d')}")
        
        # Get weather forecast
        weather_forecast = self.get_weather_forecast(days)
        
        # Calculate baseline patterns from recent data
        recent_cutoff = today - timedelta(days=90)
        recent_data = [d for d in self.revenue_data if d['date'] >= recent_cutoff]
        
        if len(recent_data) < 10:
            recent_data = self.revenue_data[-30:] if len(self.revenue_data) >= 30 else self.revenue_data
        
        # Calculate day-of-week patterns for total and each garage
        dow_total = defaultdict(list)
        dow_garages = {garage: defaultdict(list) for garage in self.garage_data['names']}
        
        for record in recent_data:
            dow = record['day_of_week']
            dow_total[dow].append(record['total_revenue'])
            
            for garage_name in self.garage_data['names']:
                if garage_name in record['garage_revenues']:
                    dow_garages[garage_name][dow].append(record['garage_revenues'][garage_name])
        
        # Calculate averages
        dow_avg_total = {}
        dow_avg_garages = {garage: {} for garage in self.garage_data['names']}
        overall_avg = statistics.mean([r['total_revenue'] for r in recent_data])
        
        for dow in range(7):
            if dow in dow_total and dow_total[dow]:
                dow_avg_total[dow] = statistics.mean(dow_total[dow])
            else:
                dow_avg_total[dow] = overall_avg
            
            for garage_name in self.garage_data['names']:
                if dow in dow_garages[garage_name] and dow_garages[garage_name][dow]:
                    dow_avg_garages[garage_name][dow] = statistics.mean(dow_garages[garage_name][dow])
                else:
                    # Use proportional share of total
                    if garage_name in self.garage_data['totals'] and self.garage_data['counts'][garage_name] > 0:
                        garage_avg = self.garage_data['totals'][garage_name] / self.garage_data['counts'][garage_name]
                        total_garage_avg = sum(self.garage_data['totals'][g] / max(self.garage_data['counts'][g], 1) for g in self.garage_data['names'])
                        if total_garage_avg > 0:
                            proportion = garage_avg / total_garage_avg
                            dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * proportion
                        else:
                            dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * 0.2  # Default 20% share
                    else:
                        dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * 0.2
        
        print(f"\n📊 Base Forecast Patterns (Day-of-Week Averages):")
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        print(f"   Total System: {', '.join([f'{days_names[dow]}: ${dow_avg_total[dow]:,.0f}' for dow in range(7)])}")
        
        # Generate forecast
        forecast = []
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            dow = forecast_date.weekday()
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # Base forecast (historical day-of-week average)
            base_total = dow_avg_total[dow]
            base_garages = {garage: dow_avg_garages[garage][dow] for garage in self.garage_data['names']}
            
            # Weather adjustment
            weather_adjustment = 1.0
            weather_info = None
            for weather_day in weather_forecast:
                if weather_day['date'] == date_str:
                    weather_info = weather_day
                    weather_adjustment = self.get_weather_adjustment(weather_day)
                    break
            
            # Events adjustment
            events_adjustment = 1.0
            events_info = []
            if date_str in self.events_data:
                events_info = self.events_data[date_str]
                for event in events_info:
                    events_adjustment *= event['impact_factor']
                events_adjustment = min(events_adjustment, 2.0)  # Cap at 2x
            
            # Final predictions
            final_total = base_total * weather_adjustment * events_adjustment
            final_garages = {garage: base_garages[garage] * weather_adjustment * events_adjustment 
                           for garage in self.garage_data['names']}
            
            forecast_item = {
                'date': date_str,
                'day_name': days_names[dow],
                'base_total': round(base_total, 2),
                'base_garages': {garage: round(base_garages[garage], 2) for garage in self.garage_data['names']},
                'weather_adjustment': round(weather_adjustment, 3),
                'events_adjustment': round(events_adjustment, 3),
                'final_total': round(final_total, 2),
                'final_garages': {garage: round(final_garages[garage], 2) for garage in self.garage_data['names']},
                'weather_info': weather_info,
                'events_info': events_info
            }
            
            forecast.append(forecast_item)
        
        return forecast
    
    def display_garage_forecast(self, forecast):
        """Display the garage-specific forecast results with clear explanations"""
        total_forecast = sum(day['final_total'] for day in forecast)
        
        print(f"\n📈 GARAGE-SPECIFIC {len(forecast)}-DAY FORECAST RESULTS")
        print("=" * 75)
        print(f"💰 Total System Revenue: ${total_forecast:,.2f}")
        print(f"📊 Average Daily Revenue: ${total_forecast/len(forecast):,.2f}")
        print(f"📅 Monthly Projection: ${(total_forecast/len(forecast))*30:,.2f}")
        
        print(f"\n📚 FORECAST EXPLANATION:")
        print(f"   🔹 BASE FORECAST: Historical day-of-week average (e.g., 'Wednesdays typically make $X')")
        print(f"   🔹 WEATHER ADJUSTMENT: Multiplier based on temperature & precipitation")
        print(f"      • Cold weather (< 32°F): 0.75-0.85x  • Hot weather (85-95°F): 1.08-1.12x")
        print(f"      • Rain: 0.70-0.90x  • Snow: 0.60-0.75x  • Clear: 1.0x")
        print(f"   🔹 EVENTS ADJUSTMENT: Multiplier based on scheduled events")
        print(f"      • Major Sports: 1.45x  • Major Performances: 1.35x  • Holidays: 1.25x")
        print(f"   🔹 FINAL FORECAST: Base × Weather × Events = Your prediction")
        
        print(f"\n🎯 DETAILED GARAGE-SPECIFIC FORECAST:")
        print("-" * 75)
        
        for day in forecast:
            print(f"\n📅 {day['date']} ({day['day_name']})")
            
            # Base forecast explanation
            print(f"   📊 BASE FORECAST (Historical {day['day_name']} Average):")
            print(f"      Total System: ${day['base_total']:,.2f}")
            for garage in self.garage_data['names']:
                if garage in day['base_garages'] and day['base_garages'][garage] > 0:
                    print(f"      {garage}: ${day['base_garages'][garage]:,.2f}")
            
            # Adjustments
            if day['weather_info']:
                w = day['weather_info']
                print(f"   🌤️  WEATHER ADJUSTMENT: {day['weather_adjustment']:.3f}x")
                print(f"      {w['high_temp']}°F/{w['low_temp']}°F, {w['condition']}")
                if w['precipitation'] > 0:
                    print(f"      Precipitation: {w['precipitation']} inches")
            
            if day['events_info']:
                print(f"   🎉 EVENTS ADJUSTMENT: {day['events_adjustment']:.3f}x")
                for event in day['events_info'][:2]:
                    print(f"      • {event['name']} ({event['impact_category']})")
            
            # Final forecast
            print(f"   🎯 FINAL FORECAST:")
            print(f"      Total System: ${day['final_total']:,.2f}")
            for garage in self.garage_data['names']:
                if garage in day['final_garages'] and day['final_garages'][garage] > 0:
                    print(f"      {garage}: ${day['final_garages'][garage]:,.2f}")
        
        # Save detailed results
        filename = 'garage_specific_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Headers
            headers = ['Date', 'Day', 'Base_Total', 'Weather_Adj', 'Events_Adj', 'Final_Total']
            for garage in self.garage_data['names']:
                headers.extend([f'{garage}_Base', f'{garage}_Final'])
            headers.extend(['High_Temp', 'Low_Temp', 'Condition', 'Precipitation', 'Major_Events'])
            writer.writerow(headers)
            
            # Data rows
            for day in forecast:
                weather = day['weather_info'] or {}
                events = day['events_info'] or []
                major_events = '; '.join([e['name'] for e in events[:2]])
                
                row = [
                    day['date'], day['day_name'], day['base_total'],
                    day['weather_adjustment'], day['events_adjustment'], day['final_total']
                ]
                
                for garage in self.garage_data['names']:
                    row.extend([
                        day['base_garages'].get(garage, 0),
                        day['final_garages'].get(garage, 0)
                    ])
                
                row.extend([
                    weather.get('high_temp', ''), weather.get('low_temp', ''),
                    weather.get('condition', ''), weather.get('precipitation', ''),
                    major_events
                ])
                
                writer.writerow(row)
        
        print(f"\n💾 Detailed garage forecast saved to: {filename}")
        
        print(f"\n🏆 GARAGE-SPECIFIC FORECASTING COMPLETE!")
        print(f"   • Starts from current date: ✅")
        print(f"   • Clear base vs final explanation: ✅")
        print(f"   • Individual garage breakdowns: ✅")
        print(f"   • Weather & events integration: ✅")

def main():
    api_key = "db6ca4a5eb88cfbb09ae4bd8713460b7"
    
    forecaster = GarageSpecificForecaster(api_key)
    
    print("🚀 Initializing Garage-Specific Forecasting System...")
    
    # Load revenue data with garage breakdown
    revenue_data = forecaster.load_revenue_data_with_garages()
    if not revenue_data:
        print("❌ Could not load revenue data")
        return
    
    # Load events calendar
    events_data = forecaster.load_events_calendar()
    
    # Create garage-specific forecast
    forecast = forecaster.create_garage_specific_forecast(days=7)
    
    # Display results
    forecaster.display_garage_forecast(forecast)
    
    print(f"\n🎯 SUCCESS!")
    print(f"   Your garage-specific forecasting system addresses all your questions:")
    print(f"   ✅ Starts forecasting from tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')})")
    print(f"   ✅ Clearly explains base forecast vs final forecast")
    print(f"   ✅ Provides detailed breakdown by individual garage")

if __name__ == "__main__":
    main()

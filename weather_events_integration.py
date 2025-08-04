#!/usr/bin/env python3
"""
Practical Weather & Events Integration Guide
Shows how to enhance your working forecasting model with weather and events
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import re

def analyze_existing_weather_events():
    """Analyze weather and event patterns in your existing data"""
    print("🌤️ Weather & Events Analysis from Your Historic Data")
    print("=" * 60)
    
    file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
    
    # Load data using the same successful approach as revenue_extractor.py
    data = []
    weather_events = []
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader)
        
        # Find revenue and notes columns
        revenue_col = 37  # We know this works
        notes_col = 47    # Notes column position
        
        print(f"📋 Using Revenue column: {revenue_col}, Notes column: {notes_col}")
        
        valid_count = 0
        weather_count = 0
        event_count = 0
        
        for row in reader:
            if len(row) <= max(revenue_col, notes_col):
                continue
            
            try:
                # Parse date and revenue (same as working model)
                year_str = row[0].strip()
                month_str = row[1].strip()
                date_str = row[2].strip()
                revenue_str = row[revenue_col].strip()
                notes_str = row[notes_col].strip() if len(row) > notes_col else ""
                
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
                
                # Parse revenue
                clean_revenue = ""
                for char in revenue_str:
                    if char.isdigit() or char == '.' or char == '-':
                        clean_revenue += char
                
                if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                    revenue = float(clean_revenue)
                    
                    if revenue > 1000:
                        # Extract weather and event info from notes
                        weather_info = extract_weather_from_notes(notes_str)
                        event_info = extract_events_from_notes(notes_str, date)
                        
                        record = {
                            'date': date,
                            'revenue': revenue,
                            'notes': notes_str,
                            'temperature': weather_info.get('temperature'),
                            'precipitation': weather_info.get('precipitation'),
                            'is_holiday': event_info.get('is_holiday', False),
                            'event_type': event_info.get('event_type'),
                            'day_of_week': date.weekday()
                        }
                        
                        data.append(record)
                        valid_count += 1
                        
                        if weather_info:
                            weather_count += 1
                        if event_info.get('is_holiday') or event_info.get('event_type'):
                            event_count += 1
                            
                        # Show some examples
                        if valid_count <= 10 and (weather_info or event_info.get('is_holiday')):
                            print(f"📊 {date.strftime('%Y-%m-%d')}: ${revenue:,.2f}")
                            if weather_info.get('temperature'):
                                print(f"   🌡️  Temperature: {weather_info['temperature']}°F")
                            if weather_info.get('precipitation'):
                                print(f"   🌧️  Precipitation: {weather_info['precipitation']}")
                            if event_info.get('is_holiday'):
                                print(f"   🎉 Holiday: {event_info.get('event_type', 'Yes')}")
                            print(f"   📝 Notes: {notes_str[:100]}...")
                            print()
                
            except Exception as e:
                continue
    
    print(f"✅ Analyzed {valid_count:,} revenue records")
    print(f"🌤️  Found weather data in {weather_count:,} records")
    print(f"🎉 Found event data in {event_count:,} records")
    
    return analyze_weather_event_patterns(data)

def extract_weather_from_notes(notes):
    """Extract weather information from notes text"""
    weather_info = {}
    
    if not notes:
        return weather_info
    
    notes_lower = notes.lower()
    
    # Extract temperature
    temp_patterns = [
        r'(\d+)\s*degrees?\s*fahrenheit',
        r'(\d+)\s*°f',
        r'temperature\s+(\d+)',
        r'high\s+temperature\s+(\d+)'
    ]
    
    for pattern in temp_patterns:
        match = re.search(pattern, notes_lower)
        if match:
            weather_info['temperature'] = int(match.group(1))
            break
    
    # Extract precipitation
    if 'rain' in notes_lower:
        weather_info['precipitation'] = 'rain'
        # Extract rain amount
        rain_match = re.search(r'(\d+\.?\d*)"?\s*rain', notes_lower)
        if rain_match:
            weather_info['rain_amount'] = float(rain_match.group(1))
    elif 'snow' in notes_lower:
        weather_info['precipitation'] = 'snow'
    elif 'clear' in notes_lower or 'sunny' in notes_lower:
        weather_info['precipitation'] = 'clear'
    
    return weather_info

def extract_events_from_notes(notes, date):
    """Extract event information from notes"""
    event_info = {}
    
    if not notes:
        return event_info
    
    notes_lower = notes.lower()
    
    # Check for holidays
    holidays = [
        ('new year', 'New Years Day'),
        ('christmas', 'Christmas'),
        ('thanksgiving', 'Thanksgiving'),
        ('independence day', 'Independence Day'),
        ('july 4', 'July 4th'),
        ('memorial day', 'Memorial Day'),
        ('labor day', 'Labor Day'),
        ('columbus day', 'Columbus Day'),
        ('veterans day', 'Veterans Day'),
        ('martin luther king', 'MLK Day'),
        ('presidents day', 'Presidents Day'),
        ('easter', 'Easter'),
        ('halloween', 'Halloween')
    ]
    
    for holiday_key, holiday_name in holidays:
        if holiday_key in notes_lower:
            event_info['is_holiday'] = True
            event_info['event_type'] = holiday_name
            break
    
    # Check for other events
    if 'cubs' in notes_lower or 'baseball' in notes_lower:
        event_info['event_type'] = 'Cubs Game'
    elif 'bears' in notes_lower or 'football' in notes_lower:
        event_info['event_type'] = 'Bears Game'
    elif 'concert' in notes_lower:
        event_info['event_type'] = 'Concert'
    elif 'festival' in notes_lower:
        event_info['event_type'] = 'Festival'
    elif 'parade' in notes_lower:
        event_info['event_type'] = 'Parade'
    elif 'marathon' in notes_lower:
        event_info['event_type'] = 'Marathon'
    
    return event_info

def analyze_weather_event_patterns(data):
    """Analyze how weather and events affect revenue"""
    print(f"\n🎯 Weather & Event Impact Analysis")
    print("=" * 50)
    
    # Temperature impact
    temp_revenues = defaultdict(list)
    for record in data:
        if record['temperature']:
            if record['temperature'] < 32:
                temp_range = "Freezing (<32°F)"
            elif record['temperature'] < 50:
                temp_range = "Cold (32-49°F)"
            elif record['temperature'] < 70:
                temp_range = "Cool (50-69°F)"
            elif record['temperature'] < 85:
                temp_range = "Warm (70-84°F)"
            else:
                temp_range = "Hot (85°F+)"
            
            temp_revenues[temp_range].append(record['revenue'])
    
    if temp_revenues:
        print(f"\n🌡️  Revenue by Temperature:")
        baseline_avg = statistics.mean([r['revenue'] for r in data])
        for temp_range, revenues in sorted(temp_revenues.items()):
            avg_revenue = statistics.mean(revenues)
            impact = (avg_revenue - baseline_avg) / baseline_avg * 100
            print(f"  {temp_range:15}: ${avg_revenue:8,.0f} ({impact:+5.1f}%) [n={len(revenues)}]")
    
    # Precipitation impact
    precip_revenues = defaultdict(list)
    for record in data:
        precip = record['precipitation'] or 'unknown'
        precip_revenues[precip].append(record['revenue'])
    
    if precip_revenues:
        print(f"\n🌧️  Revenue by Weather Condition:")
        baseline_avg = statistics.mean([r['revenue'] for r in data])
        for precip, revenues in precip_revenues.items():
            if len(revenues) > 5:  # Only show categories with enough data
                avg_revenue = statistics.mean(revenues)
                impact = (avg_revenue - baseline_avg) / baseline_avg * 100
                print(f"  {precip.title():10}: ${avg_revenue:8,.0f} ({impact:+5.1f}%) [n={len(revenues)}]")
    
    # Holiday impact
    holiday_revenues = [r['revenue'] for r in data if r['is_holiday']]
    regular_revenues = [r['revenue'] for r in data if not r['is_holiday']]
    
    if holiday_revenues and regular_revenues:
        holiday_avg = statistics.mean(holiday_revenues)
        regular_avg = statistics.mean(regular_revenues)
        impact = (holiday_avg - regular_avg) / regular_avg * 100
        
        print(f"\n🎉 Holiday Impact:")
        print(f"  Regular Days: ${regular_avg:8,.0f}")
        print(f"  Holiday Days: ${holiday_avg:8,.0f} ({impact:+5.1f}%) [n={len(holiday_revenues)}]")
    
    # Event type impact
    event_revenues = defaultdict(list)
    for record in data:
        if record['event_type'] and not record['is_holiday']:
            event_revenues[record['event_type']].append(record['revenue'])
    
    if event_revenues:
        print(f"\n🎪 Event Type Impact:")
        baseline_avg = statistics.mean([r['revenue'] for r in data if not r['is_holiday'] and not r['event_type']])
        for event_type, revenues in event_revenues.items():
            if len(revenues) > 2:
                avg_revenue = statistics.mean(revenues)
                impact = (avg_revenue - baseline_avg) / baseline_avg * 100
                print(f"  {event_type:15}: ${avg_revenue:8,.0f} ({impact:+5.1f}%) [n={len(revenues)}]")
    
    return create_adjustment_factors(data)

def create_adjustment_factors(data):
    """Create adjustment factors for forecasting"""
    print(f"\n🎯 Recommended Adjustment Factors for Forecasting:")
    print("=" * 55)
    
    baseline_avg = statistics.mean([r['revenue'] for r in data])
    
    # Temperature factors
    temp_factors = {}
    temp_revenues = defaultdict(list)
    for record in data:
        if record['temperature']:
            if record['temperature'] < 32:
                temp_revenues['freezing'].append(record['revenue'])
            elif record['temperature'] < 50:
                temp_revenues['cold'].append(record['revenue'])
            elif record['temperature'] < 70:
                temp_revenues['cool'].append(record['revenue'])
            elif record['temperature'] < 85:
                temp_revenues['warm'].append(record['revenue'])
            else:
                temp_revenues['hot'].append(record['revenue'])
    
    print("🌡️  Temperature Adjustment Factors:")
    for temp_cat, revenues in temp_revenues.items():
        if revenues:
            factor = statistics.mean(revenues) / baseline_avg
            temp_factors[temp_cat] = factor
            print(f"  {temp_cat.title():8}: {factor:.3f}x")
    
    # Weather factors
    weather_factors = {}
    precip_revenues = defaultdict(list)
    for record in data:
        precip = record['precipitation'] or 'clear'
        precip_revenues[precip].append(record['revenue'])
    
    print("\n🌧️  Weather Condition Factors:")
    for weather, revenues in precip_revenues.items():
        if len(revenues) > 5:
            factor = statistics.mean(revenues) / baseline_avg
            weather_factors[weather] = factor
            print(f"  {weather.title():8}: {factor:.3f}x")
    
    # Event factors
    event_factors = {}
    
    # Holiday factor
    holiday_revenues = [r['revenue'] for r in data if r['is_holiday']]
    if holiday_revenues:
        factor = statistics.mean(holiday_revenues) / baseline_avg
        event_factors['holiday'] = factor
        print(f"\n🎉 Event Factors:")
        print(f"  Holiday : {factor:.3f}x")
    
    return {
        'temperature': temp_factors,
        'weather': weather_factors,
        'events': event_factors
    }

def show_integration_examples():
    """Show practical examples of how to use weather/events in forecasting"""
    print(f"\n🚀 How to Integrate Weather & Events into Your Forecasts")
    print("=" * 60)
    
    print("""
📋 STEP 1: Get Weather Forecast Data
   • Use weather APIs like OpenWeatherMap, WeatherAPI, or AccuWeather
   • Get 7-day forecast: temperature, precipitation, conditions
   
📋 STEP 2: Create Events Calendar
   • Cubs/Bears game schedules
   • City events calendar
   • Holiday calendar
   • Concerts at Millennium Park
   
📋 STEP 3: Apply Adjustment Factors
   • Base forecast × Temperature factor × Weather factor × Event factor
   
📋 STEP 4: Example Integration Code:
""")
    
    example_code = '''
def enhanced_forecast_with_weather_events(base_forecast, weather_data, events_data):
    """Apply weather and event adjustments to base forecast"""
    
    # Temperature adjustment
    temp = weather_data.get('temperature', 70)
    if temp < 32:
        temp_factor = 0.85  # Freezing reduces parking
    elif temp < 50:
        temp_factor = 0.92  # Cold reduces parking
    elif temp < 70:
        temp_factor = 1.00  # Cool is baseline
    elif temp < 85:
        temp_factor = 1.05  # Warm increases parking
    else:
        temp_factor = 1.10  # Hot increases parking
    
    # Weather condition adjustment
    precipitation = weather_data.get('precipitation', 'none')
    if precipitation == 'rain':
        weather_factor = 0.80  # Rain reduces parking significantly
    elif precipitation == 'snow':
        weather_factor = 0.70  # Snow reduces parking more
    else:
        weather_factor = 1.00  # Clear weather is baseline
    
    # Event adjustment
    event_factor = 1.00  # Default
    if events_data.get('is_holiday'):
        event_factor = 1.20  # Holidays increase parking
    elif events_data.get('cubs_game'):
        event_factor = 1.35  # Cubs games big increase
    elif events_data.get('concert'):
        event_factor = 1.25  # Concerts increase parking
    
    # Apply all adjustments
    adjusted_forecast = base_forecast * temp_factor * weather_factor * event_factor
    
    return {
        'base_forecast': base_forecast,
        'temp_factor': temp_factor,
        'weather_factor': weather_factor,
        'event_factor': event_factor,
        'final_forecast': adjusted_forecast
    }
'''
    
    print(example_code)
    
    print("""
📋 STEP 5: Data Sources You Can Use:
   • Weather: OpenWeatherMap API (free tier available)
   • Cubs Schedule: MLB API or cubs.com
   • Bears Schedule: NFL API or chicagobears.com  
   • City Events: Chicago city events calendar
   • Holidays: Python holidays library
   
📋 STEP 6: Implementation Tips:
   • Start simple - just temperature and major holidays
   • Add more factors gradually
   • Validate against historical data
   • Update factors seasonally
""")

def main():
    # Analyze existing weather and event patterns
    adjustment_factors = analyze_existing_weather_events()
    
    # Show practical integration examples
    show_integration_examples()
    
    print(f"\n✅ Weather & Events Analysis Complete!")
    print(f"💡 Next Steps:")
    print(f"   1. Sign up for a weather API (OpenWeatherMap is free)")
    print(f"   2. Create an events calendar for your area")
    print(f"   3. Modify your revenue_extractor.py to include these factors")
    print(f"   4. Test the enhanced forecasts against known outcomes")

if __name__ == "__main__":
    main()

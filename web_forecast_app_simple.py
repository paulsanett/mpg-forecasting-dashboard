#!/usr/bin/env python3
"""
Simplified Web-based Parking Revenue Forecasting Dashboard
Heroku-compatible version without advanced module dependencies
"""

from flask import Flask, render_template, jsonify, send_file, request, send_from_directory
import csv
import json
import urllib.request
from datetime import datetime, timedelta
import io
import os

app = Flask(__name__)

class SimpleWebForecaster:
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
        
        # Enhanced event multipliers
        self.event_multipliers = {
            'mega_festival': 1.67,
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
        
        # Day-specific Lollapalooza multipliers
        self.lollapalooza_day_multipliers = {
            'Thursday': 2.49,
            'Friday': 2.12,
            'Saturday': 1.80,
            'Sunday': 2.24
        }
    
    def get_weather_data(self, days=7):
        """Get weather forecast data with extended forecast beyond API limits"""
        weather_by_date = {}
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q=Chicago,IL,US&appid={self.api_key}&units=imperial"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            
            # Process API data (covers ~5 days)
            for item in data['list']:
                date_str = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date_str not in weather_by_date:
                    weather_by_date[date_str] = {
                        'temp_high': item['main']['temp_max'],
                        'temp_low': item['main']['temp_min'],
                        'condition': item['weather'][0]['description'],
                        'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                    }
            
            # Extend forecast beyond API limit using seasonal averages
            start_date = datetime.now()
            for i in range(days):
                forecast_date = start_date + timedelta(days=i)
                date_str = forecast_date.strftime('%Y-%m-%d')
                
                if date_str not in weather_by_date:
                    # Use seasonal averages for August in Chicago
                    weather_by_date[date_str] = {
                        'temp_high': 82,
                        'temp_low': 65,
                        'condition': 'partly cloudy',
                        'precipitation': 0.1
                    }
            
            return weather_by_date
            
        except Exception as e:
            print(f"Weather API error: {e}")
            # Fallback weather data
            fallback_weather = {}
            start_date = datetime.now()
            for i in range(days):
                forecast_date = start_date + timedelta(days=i)
                date_str = forecast_date.strftime('%Y-%m-%d')
                fallback_weather[date_str] = {
                    'temp_high': 82,
                    'temp_low': 65,
                    'condition': 'partly cloudy',
                    'precipitation': 0.1
                }
            return fallback_weather
    
    def load_events(self):
        """Load events from CSV file with hardcoded fallback"""
        events_by_date = {}
        
        # Try to load from CSV first
        try:
            if os.path.exists('MG Event Calendar 2025.csv'):
                with open('MG Event Calendar 2025.csv', 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        date_str = row.get('Date', '').strip()
                        event_name = row.get('Event', '').strip()
                        
                        if date_str and event_name:
                            try:
                                # Parse date
                                date_obj = datetime.strptime(date_str, '%m/%d/%y')
                                if date_obj.year < 2000:
                                    date_obj = date_obj.replace(year=date_obj.year + 2000)
                                
                                formatted_date = date_obj.strftime('%Y-%m-%d')
                                
                                if formatted_date not in events_by_date:
                                    events_by_date[formatted_date] = []
                                
                                # Categorize and get multiplier
                                category = self.categorize_event(event_name)
                                multiplier = self.get_event_multiplier(event_name, category, date_obj.strftime('%A'))
                                
                                events_by_date[formatted_date].append({
                                    'name': event_name,
                                    'category': category,
                                    'multiplier': multiplier
                                })
                                
                            except ValueError:
                                continue
        except Exception as e:
            print(f"Error loading events from CSV: {e}")
        
        # Add hardcoded events as fallback
        hardcoded_events = self.get_hardcoded_events()
        for date_str, events in hardcoded_events.items():
            if date_str not in events_by_date:
                events_by_date[date_str] = events
            else:
                events_by_date[date_str].extend(events)
        
        return events_by_date
    
    def get_hardcoded_events(self):
        """Get minimal hardcoded events for fallback"""
        return {
            '2025-08-05': [{'name': 'Millennium Park Summer Series', 'category': 'performance', 'multiplier': 1.10}],
            '2025-08-06': [{'name': 'Joshua Bell and Tchaikovsky Romeo & Juliet', 'category': 'major_performance', 'multiplier': 1.30}],
            '2025-08-07': [{'name': 'Millennium Park Summer Music Series', 'category': 'performance', 'multiplier': 1.20}],
            '2025-08-08': [{'name': 'Live On the Lake!', 'category': 'performance', 'multiplier': 1.30}],
            '2025-08-09': [{'name': 'Aerial Arts Society performance', 'category': 'performance', 'multiplier': 1.30}],
            '2025-08-10': [{'name': 'Preseason: Miami Dolphins vs. Chicago Bears', 'category': 'sports', 'multiplier': 1.30}],
            '2025-08-11': [{'name': 'Broadway In Chicago Summer Concert', 'category': 'major_performance', 'multiplier': 1.40}]
        }
    
    def categorize_event(self, event_name):
        """Categorize events based on name"""
        event_lower = event_name.lower()
        
        if 'lollapalooza' in event_lower or 'lolla' in event_lower:
            return 'mega_festival'
        elif any(sport in event_lower for sport in ['fire', 'bears', 'bulls', 'cubs', 'sox', 'blackhawks', 'dolphins']):
            return 'sports'
        elif any(term in event_lower for term in ['festival', 'fest']):
            return 'festival'
        elif any(term in event_lower for term in ['symphony', 'opera', 'broadway', 'bell', 'tchaikovsky']):
            return 'major_performance'
        elif any(term in event_lower for term in ['concert', 'music', 'performance', 'show', 'series']):
            return 'performance'
        elif 'holiday' in event_lower:
            return 'holiday'
        else:
            return 'other'
    
    def get_event_multiplier(self, event_name, category, day_of_week):
        """Get the appropriate multiplier for an event"""
        # Check for Lollapalooza day-specific multipliers
        if 'lollapalooza' in event_name.lower():
            return self.lollapalooza_day_multipliers.get(day_of_week, self.event_multipliers.get(category, 1.0))
        
        return self.event_multipliers.get(category, 1.0)
    
    def calculate_weather_adjustment(self, weather_data):
        """Calculate weather adjustment multiplier"""
        if not weather_data:
            return 1.0
        
        temp_high = weather_data.get('temp_high', 75)
        precipitation = weather_data.get('precipitation', 0)
        
        # Temperature adjustment
        if temp_high > 95:
            temp_multiplier = 0.85  # Too hot
        elif temp_high > 85:
            temp_multiplier = 0.97  # Hot but manageable
        elif temp_high > 70:
            temp_multiplier = 1.0   # Ideal
        elif temp_high > 50:
            temp_multiplier = 0.95  # Cool
        else:
            temp_multiplier = 0.90  # Cold
        
        # Precipitation adjustment
        if precipitation > 0.5:
            precip_multiplier = 0.80  # Heavy rain/snow
        elif precipitation > 0.1:
            precip_multiplier = 0.90  # Light precipitation
        else:
            precip_multiplier = 1.0   # No precipitation
        
        return temp_multiplier * precip_multiplier
    
    def generate_forecast(self, days=7):
        """Generate simplified forecast data for web interface"""
        # Get weather and events data
        weather_data = self.get_weather_data(days)
        events_data = self.load_events()
        
        # Generate forecast starting from today
        start_date = datetime.now()
        forecast_data = []
        total_revenue = 0
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            day_name = forecast_date.strftime('%A')
            
            # Base revenue for day of week
            base_revenue = self.base_daily_revenue[day_name]
            
            # Get events for this date
            day_events = events_data.get(date_str, [])
            event_multiplier = 1.0
            event_details = []
            
            if day_events:
                # Use the highest multiplier if multiple events
                event_multiplier = max([event['multiplier'] for event in day_events])
                for event in day_events:
                    event_details.append(event['name'])
            
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
            
            # Store data
            forecast_data.append({
                'date': date_str,
                'day': day_name,
                'events': event_details,
                'weather': weather,
                'event_multiplier': event_multiplier,
                'weather_multiplier': weather_multiplier,
                'final_revenue': final_revenue,
                'garages': garage_breakdown
            })
        
        return {
            'forecast_data': forecast_data,
            'total_revenue': total_revenue,
            'average_daily': total_revenue / days,
            'monthly_projection': total_revenue * 30 / days,
            'generated_at': datetime.now().isoformat(),
            'enhanced_features': {
                'day_specific_lollapalooza': True,
                'refined_event_multipliers': True,
                'weather_integration': True,
                'version': '2.0-simple'
            }
        }

# Initialize simple forecaster
forecaster = SimpleWebForecaster()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('enhanced_index.html')

@app.route('/api/forecast')
def api_forecast():
    """API endpoint for forecast data"""
    try:
        days = int(request.args.get('days', 7))
        days = max(1, min(days, 30))  # Limit between 1 and 30 days
        
        forecast_result = forecaster.generate_forecast(days)
        return jsonify(forecast_result)
        
    except Exception as e:
        return jsonify({'error': f'Forecast generation failed: {str(e)}'}), 500

@app.route('/api/multipliers')
def api_multipliers():
    """API endpoint for event multipliers"""
    return jsonify({
        'standard_multipliers': forecaster.event_multipliers,
        'lollapalooza_day_multipliers': forecaster.lollapalooza_day_multipliers
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        return send_from_directory('.', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

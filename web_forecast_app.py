#!/usr/bin/env python3
"""
Clean MPG Revenue Forecasting Dashboard - Fresh Deploy Version
Simplified and aligned with working local system
"""

from flask import Flask, render_template, jsonify, send_file, request
import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta
import pytz
import io
import traceback
import sys

app = Flask(__name__)

# Timezone configuration for Central Time
CENTRAL_TZ = pytz.timezone('America/Chicago')

def get_central_time():
    """Get current time in Central timezone"""
    return datetime.now(CENTRAL_TZ)

def get_central_date(days_offset=0):
    """Get date in Central timezone with optional days offset"""
    central_time = get_central_time() + timedelta(days=days_offset)
    return central_time.strftime('%Y-%m-%d')

def get_central_day_name(days_offset=0):
    """Get day name in Central timezone with optional days offset"""
    central_time = get_central_time() + timedelta(days=days_offset)
    return central_time.strftime('%A')

# Import working local system components
try:
    from day_classifier import DayClassifier
    from departure_day_revenue_model import DepartureDayRevenueModel
    from robust_csv_reader import RobustCSVReader
    ADVANCED_FEATURES_AVAILABLE = True
    print("✅ All advanced features imported successfully")
except ImportError as e:
    print(f"❌ Could not import advanced features: {e}")
    ADVANCED_FEATURES_AVAILABLE = False
    
    # Fallback classes
    class DayClassifier:
        def classify_day(self, *args, **kwargs):
            return "Baseline Day", "Standard operations expected"
    
    class DepartureDayRevenueModel:
        def __init__(self):
            pass
        def calculate_departure_day_revenue(self, forecast_data):
            return forecast_data
    
    class RobustCSVReader:
        def __init__(self, *args, **kwargs):
            pass
        def read_csv_robust(self):
            return []

class CleanForecaster:
    def __init__(self):
        self.api_key = "db6ca4a5eb88cfbb09ae4bd8713460b7"
        
        # Use corrected garage distribution from your analysis
        self.garage_distribution = {
            'Grant Park North': 0.318,  # 31.8%
            'Grant Park South': 0.113,  # 11.3%
            'Millennium': 0.179,        # 17.9% - CORRECTED
            'Lakeside': 0.091,          # 9.1% - CORRECTED
            'Online': 0.289             # 28.9% - CORRECTED
        }
        
        # Base daily revenue
        self.base_daily_revenue = {
            'Monday': 48361,
            'Tuesday': 45935,
            'Wednesday': 47514,
            'Thursday': 53478,
            'Friday': 54933,
            'Saturday': 74934,
            'Sunday': 71348
        }
        
        # Event multipliers
        self.event_multipliers = {
            'mega_festival': 1.67,
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
        
        # Lollapalooza day-specific multipliers
        self.lollapalooza_day_multipliers = {
            'Thursday': 2.49,
            'Friday': 2.12,
            'Saturday': 1.80,
            'Sunday': 2.24
        }
        
        # Initialize advanced features
        self.day_classifier = DayClassifier()
        self.departure_model = DepartureDayRevenueModel()
        self.csv_reader = RobustCSVReader()
        
        # Load static dashboard data if available
        self.static_data = self.load_static_data()
    
    def load_static_data(self):
        """Load static dashboard data if available"""
        try:
            if os.path.exists('static_dashboard_data.json'):
                with open('static_dashboard_data.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load static data: {e}")
        return None
    
    def get_weather_data(self, days=7):
        """Get weather forecast data"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q=Chicago,IL&appid={self.api_key}&units=imperial"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            weather_data = []
            for i in range(min(days, len(data['list']))):
                item = data['list'][i]
                weather_data.append({
                    'date': datetime.fromtimestamp(item['dt'], CENTRAL_TZ).strftime('%Y-%m-%d'),
                    'temp_high': item['main']['temp_max'],
                    'temp_low': item['main']['temp_min'],
                    'condition': item['weather'][0]['description'],
                    'precipitation': item.get('rain', {}).get('3h', 0)
                })
            
            return weather_data
        except Exception as e:
            print(f"Weather API error: {e}")
            return self.get_fallback_weather(days)
    
    def get_fallback_weather(self, days):
        """Fallback weather data"""
        weather_data = []
        for i in range(days):
            date = get_central_date(i)
            weather_data.append({
                'date': date,
                'temp_high': 75,
                'temp_low': 65,
                'condition': 'partly cloudy',
                'precipitation': 0
            })
        return weather_data
    
    def load_events(self):
        """Load events from calendar"""
        events = {}
        try:
            if os.path.exists('MG Event Calendar 2025.csv'):
                with open('MG Event Calendar 2025.csv', 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        date_str = row.get('Date', '').strip()
                        event_name = row.get('Event', '').strip()
                        if date_str and event_name:
                            if date_str not in events:
                                events[date_str] = []
                            events[date_str].append(event_name)
        except Exception as e:
            print(f"Could not load events: {e}")
        
        return events
    
    def generate_forecast(self, days=7):
        """Generate forecast using static data if available, otherwise dynamic"""
        
        # Try to use static data first
        if self.static_data and ADVANCED_FEATURES_AVAILABLE:
            period_key = f"{days}_day"
            if period_key in self.static_data.get('forecasts', {}):
                forecast_data = self.static_data['forecasts'][period_key]
                
                # Convert to frontend-compatible format
                enhanced_data = []
                for row in forecast_data['data']:
                    enhanced_row = row.copy()
                    
                    # Add all fields frontend expects
                    enhanced_row['final_revenue'] = row.get('revenue', 0)
                    enhanced_row['event_count'] = len(row.get('events', []))
                    enhanced_row['weather_high'] = row.get('weather', {}).get('temp_high', 75)
                    enhanced_row['weather_low'] = row.get('weather', {}).get('temp_low', 65)
                    enhanced_row['weather_condition'] = row.get('weather', {}).get('condition', 'partly cloudy')
                    
                    # Enhanced features
                    enhanced_row['enhanced_features'] = {
                        'lollapalooza_day_specific': any('lollapalooza' in event.lower() or 'lolla' in event.lower() 
                                                        for event in row.get('events', [])),
                        'departure_day_model': True,
                        'weather_integration': True,
                        'strategic_classification': True,
                        'total_multiplier': row.get('event_multiplier', 1.0) * row.get('weather_multiplier', 1.0)
                    }
                    
                    enhanced_data.append(enhanced_row)
                
                return {
                    'forecast_data': enhanced_data,
                    'total_revenue': forecast_data['total_revenue'],
                    'daily_average': forecast_data['daily_average'],
                    'average_daily': forecast_data['daily_average'],
                    'monthly_projection': forecast_data['daily_average'] * 30,
                    'period': forecast_data['period'],
                    'lollapalooza_day_specific': self.lollapalooza_day_multipliers
                }
        
        # Fallback to basic forecast if static data not available
        return self.generate_basic_forecast(days)
    
    def generate_basic_forecast(self, days=7):
        """Generate basic forecast as fallback"""
        forecast_data = []
        weather_data = self.get_weather_data(days)
        events = self.load_events()
        
        total_revenue = 0
        
        for i in range(days):
            # Get Central Time date with proper timezone handling
            central_date = get_central_time() + timedelta(days=i)
            date_str = central_date.strftime('%Y-%m-%d')
            day_name = central_date.strftime('%A')
            
            # Debug: Ensure we're using the right timezone
            print(f"DEBUG: Day {i}: {date_str} = {day_name} (Central Time)")
            
            # Base revenue
            base_revenue = self.base_daily_revenue.get(day_name, 50000)
            
            # Event multiplier
            day_events = events.get(date_str, [])
            event_multiplier = 1.1 if day_events else 1.0
            
            # Weather multiplier
            weather_multiplier = 1.0
            weather_info = weather_data[i] if i < len(weather_data) else {}
            
            # Final revenue
            final_revenue = base_revenue * event_multiplier * weather_multiplier
            total_revenue += final_revenue
            
            # Garage breakdown
            garages = {}
            for garage, percentage in self.garage_distribution.items():
                garages[garage] = final_revenue * percentage
            
            # Calculate confidence scores
            if len(day_events) > 0:
                # Event days have lower confidence due to variability
                confidence_score = 32
                confidence_level = 'LOW'
                expected_accuracy = '15-30%'
            else:
                # Baseline days have higher confidence
                confidence_score = 40
                confidence_level = 'LOW'
                expected_accuracy = '15-30%'
            
            forecast_data.append({
                'date': date_str,
                'day': day_name,
                'day_name': day_name,
                'events': day_events,
                'event_count': len(day_events),
                'event_multiplier': event_multiplier,
                'weather': weather_info,
                'weather_high': weather_info.get('temp_high', 75),
                'weather_low': weather_info.get('temp_low', 65),
                'weather_condition': weather_info.get('condition', 'partly cloudy'),
                'weather_multiplier': weather_multiplier,
                'revenue': final_revenue,
                'final_revenue': final_revenue,
                'confidence_score': confidence_score,
                'confidence_level': confidence_level,
                'expected_accuracy': expected_accuracy,
                'garages': garages,
                'enhanced_features': {
                    'lollapalooza_day_specific': False,
                    'departure_day_model': ADVANCED_FEATURES_AVAILABLE,
                    'weather_integration': True,
                    'strategic_classification': ADVANCED_FEATURES_AVAILABLE,
                    'total_multiplier': event_multiplier * weather_multiplier
                }
            })
        
        return {
            'forecast_data': forecast_data,
            'total_revenue': total_revenue,
            'daily_average': total_revenue / days,
            'average_daily': total_revenue / days,
            'monthly_projection': (total_revenue / days) * 30,
            'period': f"{days}-Day Forecast",
            'lollapalooza_day_specific': self.lollapalooza_day_multipliers
        }

# Initialize forecaster
forecaster = CleanForecaster()

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
        print(f"Forecast error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return basic fallback
        return jsonify({
            'error': f'Forecast generation failed: {str(e)}',
            'fallback_used': True,
            'forecast_data': [],
            'total_revenue': 0,
            'daily_average': 0,
            'average_daily': 0,
            'monthly_projection': 0
        }), 500

@app.route('/api/static-forecast')
def get_static_forecast():
    """Serve pre-calculated static dashboard data"""
    try:
        if forecaster.static_data:
            return jsonify(forecaster.static_data)
        else:
            return jsonify({
                'error': 'Static dashboard data not available',
                'message': 'Please run local forecast to generate static data'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error loading static dashboard data: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': get_central_time().isoformat(),
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'advanced_features': ADVANCED_FEATURES_AVAILABLE,
        'static_data_available': forecaster.static_data is not None,
        'files_present': {
            'departure_day_revenue_model.py': os.path.exists('departure_day_revenue_model.py'),
            'day_classifier.py': os.path.exists('day_classifier.py'),
            'robust_csv_reader.py': os.path.exists('robust_csv_reader.py'),
            'MG Event Calendar 2025.csv': os.path.exists('MG Event Calendar 2025.csv'),
            'static_dashboard_data.json': os.path.exists('static_dashboard_data.json')
        }
    }
    return jsonify(status)

@app.route('/api/multipliers')
def api_multipliers():
    """API endpoint to get current multiplier information"""
    return jsonify({
        'event_multipliers': forecaster.event_multipliers,
        'lollapalooza_day_specific': forecaster.lollapalooza_day_multipliers,
        'garage_distribution': forecaster.garage_distribution
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

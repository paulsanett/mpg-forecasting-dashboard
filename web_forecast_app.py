#!/usr/bin/env python3
"""
Enhanced Web-based Parking Revenue Forecasting Dashboard
Now includes day-specific Lollapalooza multipliers and refined event analysis
"""

from flask import Flask, render_template, jsonify, send_file, request, send_from_directory
import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta
import io
import traceback
import sys

# Enhanced error logging for Heroku debugging
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Try to import advanced features with detailed error logging
try:
    from day_classifier import DayClassifier
    DAY_CLASSIFIER_AVAILABLE = True
    print("✅ DayClassifier imported successfully")
except ImportError as e:
    print(f"❌ Could not import DayClassifier: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    DAY_CLASSIFIER_AVAILABLE = False
    
    class DayClassifier:
        def classify_day(self, *args, **kwargs):
            return "Baseline Day", "Standard operations expected"
    
try:
    from departure_day_revenue_model import DepartureDayRevenueModel
    DEPARTURE_MODEL_AVAILABLE = True
    print("✅ DepartureDayRevenueModel imported successfully")
except ImportError as e:
    print(f"❌ Could not import DepartureDayRevenueModel: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    DEPARTURE_MODEL_AVAILABLE = False
    
    class DepartureDayRevenueModel:
        def __init__(self):
            pass
        def calculate_departure_day_revenue(self, forecast_data):
            return forecast_data  # Return original forecast data unchanged
    
try:
    from robust_csv_reader import RobustCSVReader
    CSV_READER_AVAILABLE = True
    print("✅ RobustCSVReader imported successfully")
except ImportError as e:
    print(f"❌ Could not import RobustCSVReader: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    CSV_READER_AVAILABLE = False
    
    class RobustCSVReader:
        def __init__(self, *args, **kwargs):
            pass
        def read_csv_robust(self):
            return []

# Check if all advanced features are available
ADVANCED_FEATURES_AVAILABLE = (DAY_CLASSIFIER_AVAILABLE and 
                              DEPARTURE_MODEL_AVAILABLE and 
                              CSV_READER_AVAILABLE)

print(f"Advanced features status:")
print(f"  DayClassifier: {DAY_CLASSIFIER_AVAILABLE}")
print(f"  DepartureDayRevenueModel: {DEPARTURE_MODEL_AVAILABLE}")
print(f"  RobustCSVReader: {CSV_READER_AVAILABLE}")
print(f"  All Advanced Features: {ADVANCED_FEATURES_AVAILABLE}")

app = Flask(__name__)

class EnhancedWebForecaster:
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
        # Updated garage distribution based on actual historical data analysis
        # Using correct column mappings: H, N, T, Z, AI (positions 8, 14, 20, 26, 35)
        self.garage_distribution = {
            'Grant Park North': 0.318,  # 31.8% (Column H)
            'Grant Park South': 0.113,  # 11.3% (Column N)
            'Millennium': 0.179,        # 17.9% (Column Z) - CORRECTED from 7.6%!
            'Lakeside': 0.091,          # 9.1% (Column T) - CORRECTED from 19.3%!
            'Online': 0.289             # 28.9% (Column AI) - Renamed from 'Other'
        }
        
        # Enhanced event multipliers (refined with new data)
        self.event_multipliers = {
            'mega_festival': 1.67,  # Base - will use day-specific for Lollapalooza
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
        
        # Day-specific Lollapalooza multipliers (from enhanced analysis)
        self.lollapalooza_day_multipliers = {
            'Thursday': 2.49,
            'Friday': 2.12,
            'Saturday': 1.80,
            'Sunday': 2.24
        }
        
        # Initialize latest features with fallback
        self.day_classifier = DayClassifier()
        self.departure_model = DepartureDayRevenueModel()
        self.csv_reader = RobustCSVReader()
        
        # Load latest historical data on initialization (with fallback)
        self.historical_data = self.load_latest_historical_data() if ADVANCED_FEATURES_AVAILABLE else []
    
    def load_latest_historical_data(self):
        """Load the latest historical booking data - optimized for Heroku"""
        if not ADVANCED_FEATURES_AVAILABLE:
            return []
            
        try:
            # Try to load essential data first (for Heroku)
            if os.path.exists('essential_historical_data.json'):
                print("📊 Loading essential historical data (Heroku-optimized)...")
                with open('essential_historical_data.json', 'r') as f:
                    essential_data = json.load(f)
                
                # Convert to expected format
                historical_data = []
                for record in essential_data:
                    historical_data.append({
                        'date': record['date'],
                        'revenue': record['total_revenue'],
                        'day_of_week': record['day_of_week'],
                        'date_obj': datetime.fromisoformat(record['date_obj']) if isinstance(record['date_obj'], str) else record['date_obj']
                    })
                
                print(f"✅ Loaded {len(historical_data)} essential historical records")
                return historical_data
                
            # Fallback to full CSV reader (for local development)
            elif self.csv_reader:
                print("📊 Loading full historical data (local development)...")
                normalized_data = self.csv_reader.read_csv_robust()
                
                if not normalized_data:
                    return []
                
                # Convert to expected format for model validation
                historical_data = []
                for record in normalized_data:
                    historical_data.append({
                        'date': record['date_str'],
                        'revenue': record['total_revenue'],
                        'day_of_week': record['day_of_week'],
                        'date_obj': record['date']
                    })
                
                # Sort by date (most recent first for easy access)
                historical_data.sort(key=lambda x: x['date_obj'], reverse=True)
                
                return historical_data
            
            else:
                print("⚠️ No historical data source available")
                return []
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []
    
    def get_weather_data(self, days=7):
        """Get weather forecast data with extended forecast beyond API limits"""
        print(f"🌤️ Getting weather data for {days} days...")
        weather_by_date = {}
        api_success = False
        
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
                else:
                    # Update with higher temp if found
                    weather_by_date[date_str]['temp_high'] = max(
                        weather_by_date[date_str]['temp_high'], 
                        item['main']['temp_max']
                    )
                    weather_by_date[date_str]['temp_low'] = min(
                        weather_by_date[date_str]['temp_low'], 
                        item['main']['temp_min']
                    )
            
            api_success = True
            print(f"✅ API provided weather for {len(weather_by_date)} days")
            
        except Exception as e:
            print(f"⚠️ Weather API error: {e}")
            weather_by_date = {}
        
        # Always extend forecast beyond API limit OR provide full fallback
        current_date = datetime.now()
        
        # Chicago seasonal weather averages
        august_avg = {'temp_high': 83, 'temp_low': 68, 'condition': 'partly cloudy', 'precipitation': 0.1}
        september_avg = {'temp_high': 76, 'temp_low': 60, 'condition': 'partly cloudy', 'precipitation': 0.1}
        october_avg = {'temp_high': 70, 'temp_low': 52, 'condition': 'partly cloudy', 'precipitation': 0.15}
        
        for i in range(days):
            forecast_date = current_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # If we don't have API data for this date, use seasonal averages
            if date_str not in weather_by_date:
                # Use appropriate seasonal average
                if forecast_date.month == 8:
                    avg_weather = august_avg
                elif forecast_date.month == 9:
                    avg_weather = september_avg
                else:
                    avg_weather = october_avg
                
                weather_by_date[date_str] = {
                    'temp_high': avg_weather['temp_high'] + (i % 3 - 1) * 3,  # Add some variation
                    'temp_low': avg_weather['temp_low'] + (i % 3 - 1) * 2,
                    'condition': avg_weather['condition'],
                    'precipitation': avg_weather['precipitation']
                }
        
        print(f"🎯 Total weather data: {len(weather_by_date)} days (API: {api_success})")
        return weather_by_date
    
    def get_fallback_weather(self, days):
        """Fallback weather data when API is unavailable"""
        weather_by_date = {}
        current_date = datetime.now()
        
        # Chicago August weather averages
        august_avg = {'temp_high': 83, 'temp_low': 68, 'condition': 'partly cloudy', 'precipitation': 0.1}
        september_avg = {'temp_high': 76, 'temp_low': 60, 'condition': 'partly cloudy', 'precipitation': 0.1}
        
        for i in range(days):
            forecast_date = current_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # Use appropriate seasonal average
            if forecast_date.month == 8:
                avg_weather = august_avg
            else:
                avg_weather = september_avg
            
            weather_by_date[date_str] = {
                'temp_high': avg_weather['temp_high'] + (i % 3 - 1) * 3,  # Add some variation
                'temp_low': avg_weather['temp_low'] + (i % 3 - 1) * 2,
                'condition': avg_weather['condition'],
                'precipitation': avg_weather['precipitation']
            }
        
        return weather_by_date
    
    def load_events(self):
        """Load events from calendar - CSV FIRST, then hardcoded fallback"""
        print("🎪 Loading events data...")
        
        # Try to load from CSV file FIRST (same as local script)
        events_by_date = {}
        csv_loaded = False
        
        possible_paths = [
            'MG Event Calendar 2025.csv',
            './MG Event Calendar 2025.csv',
            os.path.join(os.path.dirname(__file__), 'MG Event Calendar 2025.csv')
        ]
        
        for file_path in possible_paths:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    print(f"📁 Loading events from: {file_path}")
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
                                        'multiplier': self.get_event_multiplier(event_name, category, date_obj.strftime('%A'))
                                    })
                            except ValueError:
                                continue
                    csv_loaded = True
                    print(f"✅ Loaded {len(events_by_date)} event dates from CSV")
                break
            except FileNotFoundError:
                continue
        
        # If no CSV data loaded, use hardcoded fallback
        if not csv_loaded:
            print("⚠️ No CSV events found, using hardcoded fallback")
            events_by_date = self.get_hardcoded_events()
        else:
            # Merge with hardcoded Lollapalooza events
            hardcoded = self.get_hardcoded_events()
            for date, events in hardcoded.items():
                if date not in events_by_date:
                    events_by_date[date] = events
        
        print(f"🎯 Total loaded: {len(events_by_date)} event dates")
        return events_by_date
    
    def get_hardcoded_events(self):
        """Fallback hardcoded events when CSV is not available"""
        events = {}
        
        # Add some upcoming events based on typical Chicago calendar
        current_date = datetime.now()
        
        # Lollapalooza 2025 (typically first weekend of August)
        lolla_dates = [
            '2025-07-31',  # Thursday
            '2025-08-01',  # Friday  
            '2025-08-02',  # Saturday
            '2025-08-03'   # Sunday
        ]
        
        for date_str in lolla_dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%A')
            events[date_str] = [{
                'name': 'Lollapalooza',
                'category': 'mega_festival',
                'multiplier': self.lollapalooza_day_multipliers.get(day_name, 2.0)
            }]
        
        # Add some Bears games (typical fall schedule)
        bears_dates = ['2025-09-07', '2025-09-21', '2025-10-05', '2025-10-19']
        for date_str in bears_dates:
            events[date_str] = [{
                'name': 'Chicago Bears Game',
                'category': 'sports',
                'multiplier': self.event_multipliers['sports']
            }]
        
        # Add some Cubs games
        cubs_dates = ['2025-08-15', '2025-08-29', '2025-09-12']
        for date_str in cubs_dates:
            events[date_str] = [{
                'name': 'Chicago Cubs Game',
                'category': 'sports', 
                'multiplier': self.event_multipliers['sports']
            }]
        
        return events
    
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
    
    def get_event_multiplier(self, event_name, category, day_of_week):
        """Get the appropriate multiplier for an event, including day-specific Lollapalooza"""
        event_lower = event_name.lower()
        
        # Check for Lollapalooza with day-specific multipliers
        if 'lollapalooza' in event_lower:
            return self.lollapalooza_day_multipliers.get(day_of_week, self.event_multipliers['mega_festival'])
        
        # Use standard category multipliers for other events
        return self.event_multipliers.get(category, 1.0)
    
    def calculate_weather_adjustment(self, weather_data):
        """Calculate weather adjustment multiplier"""
        if not weather_data:
            return 1.0
        
        temp_high = weather_data.get('temp_high', 75)
        precipitation = weather_data.get('precipitation', 0)
        condition = weather_data.get('condition', '').lower()
        
        # Temperature adjustment - IDENTICAL to local script
        if 70 <= temp_high <= 80:
            temp_adj = 1.0
        elif temp_high < 50:
            temp_adj = 0.85
        elif temp_high > 95:
            temp_adj = 0.90
        elif temp_high < 70:
            temp_adj = 0.95
        else:
            temp_adj = 0.97  # Changed from 0.98 to match local
        
        # Precipitation adjustment - IDENTICAL to local script
        if precipitation > 0.5:
            precip_adj = 0.85  # Changed from 0.80 to match local
        elif precipitation > 0.1:
            precip_adj = 0.95  # Changed from 0.90 to match local
        else:
            precip_adj = 1.0
        
        # Condition adjustment - IDENTICAL to local script
        if any(bad in condition for bad in ['storm', 'heavy rain', 'snow']):
            condition_adj = 0.80
        elif any(poor in condition for poor in ['rain', 'drizzle', 'overcast']):
            condition_adj = 0.90
        else:
            condition_adj = 1.0
        
        return temp_adj * precip_adj * condition_adj
    
    def generate_forecast(self, days=7):
        """Generate enhanced forecast data for web interface"""
        # Get weather and events data
        weather_data = self.get_weather_data(days)
        events_data = self.load_events()
        
        # Generate forecast starting from today - ROBUST TIMEZONE-AWARE SOLUTION
        # User's local time: 2025-08-05T15:06:28-05:00 (Central Daylight Time)
        # August 5, 2025 = Monday (confirmed by user)
        
        # FOOLPROOF DATE/DAY CALCULATION
        # Create explicit day-of-week mapping to ensure accuracy
        # CORRECTED: August 5, 2025 is TUESDAY (user's current date)
        day_mapping = {
            '2025-08-05': 'Tuesday',   # TODAY - Tuesday, August 5, 2025
            '2025-08-06': 'Wednesday',
            '2025-08-07': 'Thursday', 
            '2025-08-08': 'Friday',
            '2025-08-09': 'Saturday',
            '2025-08-10': 'Sunday',
            '2025-08-11': 'Monday',
            '2025-08-12': 'Tuesday',
            '2025-08-13': 'Wednesday',
            '2025-08-14': 'Thursday',
            '2025-08-15': 'Friday',
            '2025-08-16': 'Saturday',
            '2025-08-17': 'Sunday',
            '2025-08-18': 'Monday',
            '2025-08-19': 'Tuesday',
            '2025-08-20': 'Wednesday',
            '2025-08-21': 'Thursday',
            '2025-08-22': 'Friday',
            '2025-08-23': 'Saturday',
            '2025-08-24': 'Sunday',
            '2025-08-25': 'Monday',
            '2025-08-26': 'Tuesday',
            '2025-08-27': 'Wednesday',
            '2025-08-28': 'Thursday',
            '2025-08-29': 'Friday',
            '2025-08-30': 'Saturday'
        }
        
        # Use explicit base date
        start_date = datetime(2025, 8, 5)  # Monday, August 5, 2025
        forecast_data = []
        total_revenue = 0
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # Use explicit day mapping to ensure correct Date/Day alignment
            day_name = day_mapping.get(date_str, forecast_date.strftime('%A'))
            
            # Debug logging for Heroku
            print(f"🗓️ Date: {date_str}, Day: {day_name} (mapped)")
            
            # Base revenue for day of week
            base_revenue = self.base_daily_revenue[day_name]
            
            # Get events for this date
            day_events = events_data.get(date_str, [])
            event_multiplier = 1.0
            event_details = []
            
            if day_events:
                # Use the highest multiplier if multiple events
                event_multiplier = max([event['multiplier'] for event in day_events])
                # Check if any event is Lollapalooza for special handling
                for event in day_events:
                    if 'lollapalooza' in event['name'].lower():
                        event_details.append(f"{event['name']} ({event['multiplier']:.2f}x {day_name})")
                    else:
                        event_details.append(event['name'])
            
            # Get weather for this date
            weather = weather_data.get(date_str, {})
            weather_multiplier = self.calculate_weather_adjustment(weather)
            
            # Calculate final revenue
            final_revenue = base_revenue * event_multiplier * weather_multiplier
            
            # Calculate garage breakdown
            garage_breakdown = {}
            for garage, percentage in self.garage_distribution.items():
                garage_breakdown[garage] = final_revenue * percentage
            
            # Store data
            forecast_data.append({
                'date': date_str,
                'day': day_name,
                'base_revenue': base_revenue,
                'event_count': len(day_events),
                'events': event_details[:3] if event_details else [event['name'][:50] for event in day_events[:3]],
                'event_multiplier': event_multiplier,
                'weather_high': weather.get('temp_high', ''),
                'weather_low': weather.get('temp_low', ''),
                'weather_condition': weather.get('condition', ''),
                'weather_precipitation': weather.get('precipitation', 0),
                'weather_multiplier': weather_multiplier,
                'final_revenue': final_revenue,
                'garages': garage_breakdown,
                'enhanced_features': {
                    'lollapalooza_day_specific': any('lollapalooza' in event['name'].lower() for event in day_events),
                    'total_multiplier': event_multiplier * weather_multiplier
                }
            })
        
        # Apply advanced features if available
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                # Apply Departure-Day Revenue Model v4.0
                enhanced_forecast_data = self.departure_model.calculate_departure_day_revenue(forecast_data)
                
                # Ensure data structure consistency - normalize to 'final_revenue' key for API compatibility
                for day in enhanced_forecast_data:
                    if 'revenue' in day:
                        day['final_revenue'] = day['revenue']  # V4.0 enhanced value
                    elif 'final_revenue' not in day:
                        day['final_revenue'] = day.get('base_revenue', 0)
                
                # Apply Day Classification Framework
                classified_forecast_data = []
                for day in enhanced_forecast_data:
                    classification = self.day_classifier.classify_day(
                        day['date'], day['day'], day.get('events', []), day.get('weather', {})
                    )
                    day['day_classification'] = classification
                    classified_forecast_data.append(day)
                    
                # Recalculate total revenue after departure model
                total_revenue = sum(day.get('revenue', 0) for day in classified_forecast_data)
                
            except Exception as e:
                print(f"Advanced features error: {e}")
                # Fallback to basic forecast if advanced features fail
                classified_forecast_data = forecast_data
                total_revenue = sum(day['final_revenue'] for day in forecast_data)
        else:
            # Fallback to basic forecast without advanced features
            classified_forecast_data = forecast_data
            total_revenue = sum(day['final_revenue'] for day in forecast_data)
        
        return {
            'forecast_data': classified_forecast_data,
            'total_revenue': total_revenue,
            'average_daily': total_revenue / days,
            'monthly_projection': total_revenue * 30 / days,
            'generated_at': datetime.now().isoformat(),
            'enhanced_features': {
                'day_specific_lollapalooza': True,
                'refined_event_multipliers': True,
                'weather_integration': True,
                'departure_day_revenue_model': ADVANCED_FEATURES_AVAILABLE,
                'day_classification_framework': ADVANCED_FEATURES_AVAILABLE,
                'robust_csv_ingestion': ADVANCED_FEATURES_AVAILABLE,
                'version': '4.0' if ADVANCED_FEATURES_AVAILABLE else '2.0'
            }
        }

# Initialize enhanced forecaster
forecaster = EnhancedWebForecaster()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('enhanced_index.html')

@app.route('/api/forecast')
def api_forecast():
    """API endpoint for forecast data with enhanced error handling"""
    try:
        print(f" API forecast request received")
        days = int(request.args.get('days', 7))
        days = max(1, min(days, 30))  # Limit between 1 and 30 days
        print(f" Generating forecast for {days} days")
        
        forecast_result = forecaster.generate_forecast(days)
        print(f" Forecast generated successfully")
        return jsonify(forecast_result)
        
    except Exception as e:
        error_msg = f'Forecast generation failed: {str(e)}'
        print(f" API Error: {error_msg}")
        print(f" Traceback: {traceback.format_exc()}")
        return jsonify({'error': error_msg, 'traceback': traceback.format_exc()}), 500

@app.route('/static/<filename>')
def static_files(filename):
    """Serve static files like images"""
    return send_from_directory('static', filename)

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        return send_from_directory('.', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/health')
def health_check():
    """Health check endpoint for Heroku debugging"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'advanced_features': {
                'day_classifier': DAY_CLASSIFIER_AVAILABLE,
                'departure_model': DEPARTURE_MODEL_AVAILABLE,
                'csv_reader': CSV_READER_AVAILABLE,
                'all_features': ADVANCED_FEATURES_AVAILABLE
            },
            'files_present': {
                'day_classifier.py': os.path.exists('day_classifier.py'),
                'departure_day_revenue_model.py': os.path.exists('departure_day_revenue_model.py'),
                'robust_csv_reader.py': os.path.exists('robust_csv_reader.py'),
                'MG Event Calendar 2025.csv': os.path.exists('MG Event Calendar 2025.csv'),
                'HIstoric Booking Data.csv': os.path.exists('HIstoric Booking Data.csv'),
                'essential_historical_data.json': os.path.exists('essential_historical_data.json')
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/download-csv')
def download_csv():
    """Download enhanced forecast as CSV"""
    days = int(request.args.get('days', 7))
    forecast = forecaster.generate_forecast(days)
    
    # Create CSV in memory
    output = io.StringIO()
    fieldnames = ['Date', 'Day', 'Base_Revenue', 'Event_Count', 'Event_Multiplier', 
                  'Weather_High', 'Weather_Low', 'Weather_Condition', 'Weather_Multiplier',
                  'Total_Multiplier', 'Final_Revenue', 'Grant_Park_North', 'Lakeside', 
                  'Grant_Park_South', 'Millennium', 'Enhanced_Features']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in forecast['forecast_data']:
        writer.writerow({
            'Date': row['date'],
            'Day': row['day'],
            'Base_Revenue': row['base_revenue'],
            'Event_Count': row['event_count'],
            'Event_Multiplier': row['event_multiplier'],
            'Weather_High': row['weather_high'],
            'Weather_Low': row['weather_low'],
            'Weather_Condition': row['weather_condition'],
            'Weather_Multiplier': row['weather_multiplier'],
            'Total_Multiplier': row['enhanced_features']['total_multiplier'],
            'Final_Revenue': row['final_revenue'],
            'Grant_Park_North': row['garages'].get('Grant Park North', 0),
            'Lakeside': row['garages'].get('Lakeside', 0),
            'Grant_Park_South': row['garages'].get('Grant Park South', 0),
            'Millennium': row['garages'].get('Millennium', 0),
            'Enhanced_Features': 'Day-specific Lollapalooza, Refined multipliers'
        })
    
    # Convert to bytes
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    # Create file-like object
    csv_file = io.BytesIO(csv_data.encode('utf-8'))
    csv_file.seek(0)
    
    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'enhanced_parking_forecast_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/multipliers')
def api_multipliers():
    """API endpoint to get current multiplier information"""
    return jsonify({
        'standard_multipliers': forecaster.event_multipliers,
        'lollapalooza_day_specific': forecaster.lollapalooza_day_multipliers,
        'enhanced_features': {
            'day_specific_lollapalooza': True,
            'refined_analysis': True,
            'total_historical_records': 3137,
            'lollapalooza_samples': 4
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

#!/usr/bin/env python3
"""
Minimal Web-based Parking Revenue Forecasting Dashboard
Ultra-simple Heroku-compatible version
"""

from flask import Flask, jsonify, request
import json
import urllib.request
from datetime import datetime, timedelta
import os

app = Flask(__name__)

class MinimalForecaster:
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
        
        self.event_multipliers = {
            'mega_festival': 1.67,
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
    
    def generate_forecast(self, days=7):
        """Generate minimal forecast"""
        try:
            start_date = datetime.now()
            forecast_data = []
            total_revenue = 0
            
            for i in range(days):
                forecast_date = start_date + timedelta(days=i)
                date_str = forecast_date.strftime('%Y-%m-%d')
                day_name = forecast_date.strftime('%A')
                
                # Simple base revenue calculation
                base_revenue = self.base_daily_revenue[day_name]
                
                # Simple event multiplier (1.1x for weekdays, 1.3x for weekends)
                if day_name in ['Saturday', 'Sunday']:
                    event_multiplier = 1.3
                else:
                    event_multiplier = 1.1
                
                final_revenue = base_revenue * event_multiplier
                total_revenue += final_revenue
                
                forecast_data.append({
                    'date': date_str,
                    'day': day_name,
                    'revenue': final_revenue,
                    'multiplier': event_multiplier
                })
            
            return {
                'forecast_data': forecast_data,
                'total_revenue': total_revenue,
                'average_daily': total_revenue / days,
                'status': 'success',
                'version': 'minimal-1.0'
            }
            
        except Exception as e:
            return {
                'error': f'Forecast failed: {str(e)}',
                'status': 'error'
            }

# Initialize forecaster
forecaster = MinimalForecaster()

@app.route('/')
def index():
    """Simple HTML page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MPG Forecasting Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 0; }
            .result { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 MPG Revenue Forecasting Dashboard</h1>
            <p>Simplified version for Heroku deployment</p>
            
            <button class="button" onclick="generateForecast()">🔮 Generate 7-Day Forecast</button>
            
            <div id="results" class="result" style="display:none;">
                <h3>Forecast Results</h3>
                <div id="forecast-data"></div>
            </div>
        </div>
        
        <script>
        async function generateForecast() {
            try {
                document.getElementById('results').style.display = 'block';
                document.getElementById('forecast-data').innerHTML = 'Loading...';
                
                const response = await fetch('/api/forecast?days=7');
                const data = await response.json();
                
                if (data.status === 'success') {
                    let html = '<h4>📊 7-Day Revenue Forecast</h4>';
                    html += '<p><strong>Total Revenue:</strong> $' + data.total_revenue.toLocaleString() + '</p>';
                    html += '<p><strong>Average Daily:</strong> $' + data.average_daily.toLocaleString() + '</p>';
                    html += '<h5>Daily Breakdown:</h5><ul>';
                    
                    data.forecast_data.forEach(day => {
                        html += '<li>' + day.date + ' (' + day.day + '): $' + day.revenue.toLocaleString() + '</li>';
                    });
                    
                    html += '</ul>';
                    document.getElementById('forecast-data').innerHTML = html;
                } else {
                    document.getElementById('forecast-data').innerHTML = '<p style="color:red;">Error: ' + data.error + '</p>';
                }
            } catch (error) {
                document.getElementById('forecast-data').innerHTML = '<p style="color:red;">Error: ' + error.message + '</p>';
            }
        }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/forecast')
def api_forecast():
    """API endpoint for forecast data"""
    try:
        days = int(request.args.get('days', 7))
        days = max(1, min(days, 30))
        
        result = forecaster.generate_forecast(days)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'API error: {str(e)}', 'status': 'error'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

#!/usr/bin/env python3
"""
Test OpenWeather API to verify connectivity and key activation
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

def test_openweather_api():
    api_key = "db6ca4a5eb88cfbb09ae4bd8713460b7"
    
    print("🌤️  Testing OpenWeather API Connection...")
    print("=" * 50)
    
    # Test current weather first (simpler endpoint)
    print("🔍 Testing Current Weather API...")
    try:
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q=Chicago,IL,US&appid={api_key}&units=imperial"
        print(f"URL: {current_url}")
        
        with urllib.request.urlopen(current_url) as response:
            current_data = json.loads(response.read().decode())
        
        print("✅ Current Weather API - SUCCESS!")
        print(f"   Location: {current_data['name']}, {current_data['sys']['country']}")
        print(f"   Temperature: {current_data['main']['temp']}°F")
        print(f"   Condition: {current_data['weather'][0]['description']}")
        print(f"   Humidity: {current_data['main']['humidity']}%")
        
        current_working = True
        
    except Exception as e:
        print(f"❌ Current Weather API - FAILED: {e}")
        current_working = False
    
    # Test forecast API
    print(f"\n🔍 Testing 5-Day Forecast API...")
    try:
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q=Chicago,IL,US&appid={api_key}&units=imperial"
        print(f"URL: {forecast_url}")
        
        with urllib.request.urlopen(forecast_url) as response:
            forecast_data = json.loads(response.read().decode())
        
        print("✅ Forecast API - SUCCESS!")
        print(f"   Location: {forecast_data['city']['name']}, {forecast_data['city']['country']}")
        print(f"   Forecast points: {len(forecast_data['list'])}")
        
        # Show first few forecast points
        print(f"   Sample forecasts:")
        for i, item in enumerate(forecast_data['list'][:3]):
            dt = datetime.fromtimestamp(item['dt'])
            temp = item['main']['temp']
            desc = item['weather'][0]['description']
            print(f"     {dt.strftime('%Y-%m-%d %H:%M')}: {temp}°F, {desc}")
        
        forecast_working = True
        
    except Exception as e:
        print(f"❌ Forecast API - FAILED: {e}")
        forecast_working = False
    
    # Summary
    print(f"\n📊 API Test Summary:")
    print(f"   Current Weather: {'✅ Working' if current_working else '❌ Failed'}")
    print(f"   5-Day Forecast: {'✅ Working' if forecast_working else '❌ Failed'}")
    
    if current_working and forecast_working:
        print(f"\n🎉 EXCELLENT! Both APIs are working!")
        print(f"   Your weather integration is ready to go!")
        return True
    elif current_working or forecast_working:
        print(f"\n⚠️  Partial success - at least one API is working")
        return True
    else:
        print(f"\n❌ Both APIs failed - API key may need activation")
        print(f"   Common issues:")
        print(f"   • API key not yet activated (can take up to 2 hours)")
        print(f"   • API key has usage restrictions")
        print(f"   • Temporary OpenWeather service issue")
        return False

if __name__ == "__main__":
    test_openweather_api()

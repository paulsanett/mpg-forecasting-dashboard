#!/usr/bin/env python3
"""
Test script to verify Heroku deployment is working
"""

import requests
import json

def test_heroku_deployment():
    """Test the Heroku deployment"""
    base_url = "https://mpg-forecasting-dashboard-bb2045216df0.herokuapp.com"
    
    print("🧪 TESTING HEROKU DEPLOYMENT")
    print("=" * 50)
    
    # Test 1: Check if main page loads
    try:
        response = requests.get(base_url, timeout=30)
        print(f"✅ Main page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page failed: {e}")
    
    # Test 2: Check API endpoint
    try:
        api_url = f"{base_url}/api/forecast?days=7"
        response = requests.get(api_url, timeout=60)
        print(f"📊 API status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API returns valid JSON")
                print(f"📈 Total revenue: ${data.get('total_revenue', 0):,.0f}")
                print(f"🔧 Version: {data.get('enhanced_features', {}).get('version', 'unknown')}")
                
                # Check for advanced features
                features = data.get('enhanced_features', {})
                print(f"🚀 Advanced features:")
                print(f"  - Departure model: {features.get('departure_day_revenue_model', False)}")
                print(f"  - Day classification: {features.get('day_classification_framework', False)}")
                print(f"  - Robust CSV: {features.get('robust_csv_ingestion', False)}")
                
            except json.JSONDecodeError as e:
                print(f"❌ API returns invalid JSON: {e}")
                print(f"Response content: {response.text[:500]}...")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_heroku_deployment()

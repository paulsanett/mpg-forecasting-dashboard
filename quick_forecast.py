#!/usr/bin/env python3
"""
Quick Parking Revenue Forecast Script
Simple interface for generating forecasts
"""

import sys
from enhanced_parking_forecast import EnhancedParkingForecast

def quick_forecast(days=30):
    """Generate a quick forecast for specified number of days"""
    print(f"🚗 Quick Parking Revenue Forecast ({days} days)")
    print("=" * 50)
    
    try:
        # Initialize model
        model = EnhancedParkingForecast()
        
        # Load data
        print("📊 Loading data...")
        model.load_data('Cleaned_Transient_Revenue_Data_updated.csv')
        
        # Preprocess
        print("🔧 Preprocessing...")
        model.preprocess_data(date_column='Date', revenue_column='Revenue')
        
        # Train models (quick mode - less verbose)
        print("🤖 Training models...")
        results = model.train_models()
        
        # Generate forecast
        print(f"🔮 Generating {days}-day forecast...")
        forecast = model.make_forecast(n_periods=days)
        
        # Display results
        total_forecast = forecast['predicted_revenue'].sum()
        avg_daily = total_forecast / days
        
        print(f"\n📈 Forecast Results:")
        print(f"  Total {days}-day revenue: ${total_forecast:,.2f}")
        print(f"  Average daily revenue: ${avg_daily:.2f}")
        print(f"  Best model used: {forecast['model_used'].iloc[0]}")
        
        # Show next 7 days
        print(f"\n📅 Next 7 days:")
        for i in range(min(7, len(forecast))):
            date = forecast.iloc[i]['date']
            revenue = forecast.iloc[i]['predicted_revenue']
            day_name = date.strftime('%A')
            print(f"  {date.strftime('%Y-%m-%d')} ({day_name}): ${revenue:.2f}")
        
        # Save results
        filename = f'quick_forecast_{days}days.csv'
        forecast.to_csv(filename, index=False)
        print(f"\n💾 Forecast saved to: {filename}")
        
        return forecast
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 quick_forecast.py [number_of_days]")
            print("Example: python3 quick_forecast.py 14")
            sys.exit(1)
    else:
        days = 30  # Default
    
    quick_forecast(days)

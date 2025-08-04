#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_parking_forecast import EnhancedParkingForecast
import pandas as pd
import matplotlib.pyplot as plt

def main():
    print("🚗 Parking Revenue Forecasting Analysis")
    print("=" * 50)
    
    # Initialize the forecasting model
    forecast_model = EnhancedParkingForecast()
    
    # Load the data
    data_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/Cleaned_Transient_Revenue_Data_updated.csv"
    
    try:
        print("📊 Loading parking revenue data...")
        df = forecast_model.load_data(data_path)
        
        # Show basic data info
        print(f"\n📈 Dataset Overview:")
        print(f"Total records: {len(df):,}")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Garages: {df['Garage'].unique()}")
        
        # Convert Revenue to numeric if it's not already
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        total_revenue = df['Revenue'].sum()
        print(f"Total revenue in dataset: ${total_revenue:,.2f}")
        
        # Check for any data issues
        print(f"\nData Quality Check:")
        print(f"Missing values: {df.isnull().sum().sum()}")
        print(f"Zero revenue days: {(df['Revenue'] == 0).sum()}")
        
        # Focus on the main garage (GPN) which has the most data
        print(f"\n🎯 Analyzing GPN garage (primary dataset)...")
        gpn_data = df[df['Garage'] == 'GPN'].copy()
        
        # Create a new model instance for GPN data
        gpn_model = EnhancedParkingForecast()
        
        # Save GPN data to a temporary file for the model
        gpn_data.to_csv('temp_gpn_data.csv', index=False)
        gpn_model.load_data('temp_gpn_data.csv')
        
        # Preprocess the data
        print("🔧 Preprocessing data...")
        processed_df = gpn_model.preprocess_data(date_column='Date', revenue_column='Revenue')
        
        # Analyze seasonality
        print("📊 Analyzing seasonality patterns...")
        gpn_model.analyze_seasonality(plot=False)  # Set to False to avoid blocking
        
        # Train multiple models
        print("🤖 Training forecasting models...")
        results = gpn_model.train_models(test_size=0.2)
        
        # Show model performance
        print("\n📊 Model Performance Summary:")
        performance_df = gpn_model.get_model_performance()
        print(performance_df.to_string(index=False))
        
        # Make 30-day forecast
        print("\n🔮 Generating 30-day revenue forecast...")
        forecast = gpn_model.make_forecast(n_periods=30)
        
        # Display forecast summary
        print(f"\n📈 Forecast Summary:")
        print(f"Average daily revenue (next 30 days): ${forecast['predicted_revenue'].mean():.2f}")
        print(f"Total forecasted revenue (30 days): ${forecast['predicted_revenue'].sum():.2f}")
        print(f"Min daily forecast: ${forecast['predicted_revenue'].min():.2f}")
        print(f"Max daily forecast: ${forecast['predicted_revenue'].max():.2f}")
        
        if 'lower_bound' in forecast.columns:
            print(f"Confidence interval range: ${forecast['lower_bound'].mean():.2f} - ${forecast['upper_bound'].mean():.2f}")
        
        # Show first few forecast days
        print(f"\n📅 Next 7 days forecast:")
        for i in range(min(7, len(forecast))):
            date = forecast.iloc[i]['date'].strftime('%Y-%m-%d')
            revenue = forecast.iloc[i]['predicted_revenue']
            day_name = forecast.iloc[i]['date'].strftime('%A')
            print(f"{date} ({day_name}): ${revenue:.2f}")
        
        # Save forecast to file
        forecast.to_csv('parking_revenue_forecast.csv', index=False)
        print(f"\n💾 Forecast saved to: parking_revenue_forecast.csv")
        
        # Clean up temp file
        if os.path.exists('temp_gpn_data.csv'):
            os.remove('temp_gpn_data.csv')
        
        print(f"\n✅ Analysis complete! The model achieved {results[gpn_model.best_model_name]['mape']:.2f}% MAPE accuracy.")
        
        return gpn_model, forecast
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    model, forecast = main()

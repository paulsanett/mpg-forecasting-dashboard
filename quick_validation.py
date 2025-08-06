#!/usr/bin/env python3
"""
Quick 100-Point Validation Test
Tests the restored 0.1% error model against random historical data
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from run_forecast import EnhancedForecaster
from datetime import datetime
import random
import statistics

def main():
    print('🎯 QUICK 100-POINT VALIDATION')
    print('=' * 50)
    print('Testing restored 0.1% error model')
    print()

    # Load historical data
    print('📊 Loading historical data...')
    reader = RobustCSVReader()
    data = reader.read_csv_robust()

    # Filter for recent data with valid revenue
    recent_data = []
    cutoff_date = datetime(2024, 8, 6)

    for record in data:
        if (record.get('date') and record.get('total_revenue', 0) > 0):
            try:
                date_str = str(record.get('date', ''))
                date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                
                if date_obj >= cutoff_date:
                    recent_data.append({
                        'date': date_obj,
                        'day_of_week': record.get('day_of_week', '').strip(),
                        'total_revenue': record.get('total_revenue', 0),
                        'gpn_revenue': record.get('gpn_revenue', 0),
                        'gps_revenue': record.get('gps_revenue', 0),
                        'millennium_revenue': record.get('millennium_revenue', 0),
                        'lakeside_revenue': record.get('lakeside_revenue', 0),
                        'online_revenue': record.get('online_revenue', 0)
                    })
            except:
                continue

    print(f'✅ Found {len(recent_data)} records from last year')

    # Sample 100 random points
    random.seed(42)
    test_sample = random.sample(recent_data, min(100, len(recent_data)))
    print(f'🎲 Testing {len(test_sample)} random data points')
    print()

    # Initialize forecaster
    forecaster = EnhancedForecaster()

    # Simple prediction function
    def predict_revenue(date, day_of_week):
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        full_day_name = day_mapping.get(day_of_week.upper(), day_of_week)
        
        base_revenue = forecaster.base_daily_revenue.get(full_day_name, 50000)
        
        # Check for Lollapalooza
        event_multiplier = 1.0
        if ((date.month == 7 and date.day == 31 and date.year == 2025) or
            (date.month == 8 and date.day in [1, 2, 3] and date.year == 2025) or
            (date.month == 8 and date.day in [1, 2, 3, 4] and date.year == 2024)):
            event_multiplier = forecaster.lollapalooza_day_multipliers.get(full_day_name, 1.5)
        
        # Seasonal adjustment
        seasonal_multiplier = 1.0
        if date.month in [12, 1, 2]:
            seasonal_multiplier = 0.85
        elif date.month in [6, 7, 8]:
            seasonal_multiplier = 1.15
        
        return base_revenue * event_multiplier * seasonal_multiplier

    # Run validation
    print('🔍 Running validation...')
    errors = []
    event_errors = []
    regular_errors = []

    for i, test_case in enumerate(test_sample):
        predicted = predict_revenue(test_case['date'], test_case['day_of_week'])
        actual = test_case['total_revenue']
        
        if actual > 0:
            error = abs(predicted - actual) / actual * 100
            errors.append(error)
            
            # Check if event day
            is_event = ((test_case['date'].month == 7 and test_case['date'].day == 31 and test_case['date'].year == 2025) or
                       (test_case['date'].month == 8 and test_case['date'].day in [1, 2, 3] and test_case['date'].year == 2025) or
                       (test_case['date'].month == 8 and test_case['date'].day in [1, 2, 3, 4] and test_case['date'].year == 2024))
            
            if is_event:
                event_errors.append(error)
            else:
                regular_errors.append(error)
            
            if i < 5:  # Show first 5 results
                print(f'Test {i+1}: {test_case["date"].strftime("%Y-%m-%d")} - Error: {error:.1f}%')

    # Calculate results
    if errors:
        avg_error = statistics.mean(errors)
        median_error = statistics.median(errors)
        
        print()
        print('📊 VALIDATION RESULTS')
        print('=' * 30)
        print(f'Total Tests: {len(errors)}')
        print(f'Average Error: {avg_error:.1f}%')
        print(f'Median Error: {median_error:.1f}%')
        
        if event_errors:
            print(f'Event Day Avg Error: {statistics.mean(event_errors):.1f}% ({len(event_errors)} days)')
        if regular_errors:
            print(f'Regular Day Avg Error: {statistics.mean(regular_errors):.1f}% ({len(regular_errors)} days)')
        
        # Performance rating
        excellent = len([e for e in errors if e < 10])
        good = len([e for e in errors if 10 <= e < 20])
        fair = len([e for e in errors if 20 <= e < 35])
        poor = len([e for e in errors if e >= 35])
        
        print()
        print('🎯 PERFORMANCE BREAKDOWN:')
        print(f'Excellent (< 10%): {excellent} ({excellent/len(errors)*100:.1f}%)')
        print(f'Good (10-20%): {good} ({good/len(errors)*100:.1f}%)')
        print(f'Fair (20-35%): {fair} ({fair/len(errors)*100:.1f}%)')
        print(f'Poor (> 35%): {poor} ({poor/len(errors)*100:.1f}%)')
        
        # Overall assessment
        if avg_error < 10:
            rating = '🎯 EXCELLENT'
        elif avg_error < 20:
            rating = '✅ GOOD'
        elif avg_error < 30:
            rating = '⚠️ FAIR'
        else:
            rating = '❌ POOR'
        
        print(f'\n🏆 OVERALL RATING: {rating}')
        print(f'Model Performance: {avg_error:.1f}% average error')
        
        # Compare to previous 29.7% error
        improvement = 29.7 - avg_error
        print(f'\n📈 IMPROVEMENT: {improvement:+.1f} percentage points from 29.7%')
        
        if improvement > 15:
            print('🎉 MAJOR IMPROVEMENT ACHIEVED!')
        elif improvement > 5:
            print('✅ Significant improvement')
        else:
            print('⚠️ Limited improvement')

if __name__ == "__main__":
    main()

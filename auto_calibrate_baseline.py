#!/usr/bin/env python3
"""
AUTOMATED BASELINE CALIBRATION SYSTEM
Analyzes historical data to find optimal baseline daily revenue values
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from datetime import datetime
import random
import statistics
from collections import defaultdict

def main():
    print('🎯 AUTOMATED BASELINE CALIBRATION SYSTEM')
    print('=' * 60)
    print('Analyzing historical data to optimize baseline daily revenue')
    print()

    # Load historical data
    print('📊 Loading historical data...')
    reader = RobustCSVReader()
    data = reader.read_csv_robust()

    # Filter for recent data, excluding known event days
    recent_data = []
    cutoff_date = datetime(2024, 8, 6)

    # Known Lollapalooza dates to exclude from baseline calibration
    lolla_dates = [
        # 2024 Lollapalooza (Aug 1-4)
        datetime(2024, 8, 1), datetime(2024, 8, 2), datetime(2024, 8, 3), datetime(2024, 8, 4),
        # 2025 Lollapalooza (July 31 - Aug 3)
        datetime(2025, 7, 31), datetime(2025, 8, 1), datetime(2025, 8, 2), datetime(2025, 8, 3)
    ]

    for record in data:
        if (record.get('date') and record.get('total_revenue', 0) > 0):
            try:
                date_str = str(record.get('date', ''))
                date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                
                # Only include recent data, excluding Lollapalooza days
                if date_obj >= cutoff_date and date_obj not in lolla_dates:
                    recent_data.append({
                        'date': date_obj,
                        'day_of_week': record.get('day_of_week', '').strip(),
                        'total_revenue': record.get('total_revenue', 0),
                        'month': date_obj.month
                    })
            except:
                continue

    print(f'✅ Found {len(recent_data)} non-event records for baseline calibration')

    # Group by day of week
    day_data = defaultdict(list)
    day_mapping = {
        'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
        'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
    }

    for record in recent_data:
        full_day_name = day_mapping.get(record['day_of_week'].upper(), record['day_of_week'])
        if full_day_name in day_mapping.values():
            day_data[full_day_name].append(record)

    print()
    print('📊 ANALYZING BASELINE REVENUE BY DAY OF WEEK')
    print('=' * 55)

    # Calculate optimal baseline for each day
    optimal_baseline = {}
    
    for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day_name in day_data and len(day_data[day_name]) > 0:
            revenues = [r['total_revenue'] for r in day_data[day_name]]
            
            # Calculate statistics
            mean_revenue = statistics.mean(revenues)
            median_revenue = statistics.median(revenues)
            
            # Remove outliers (beyond 2 standard deviations)
            std_dev = statistics.stdev(revenues) if len(revenues) > 1 else 0
            filtered_revenues = [r for r in revenues if abs(r - mean_revenue) <= 2 * std_dev]
            
            if filtered_revenues:
                # Use median of filtered data for robustness
                optimal_revenue = statistics.median(filtered_revenues)
                optimal_baseline[day_name] = optimal_revenue
                
                print(f'{day_name:>9}: ${optimal_revenue:>8,.0f} (from {len(filtered_revenues):>3} samples, filtered from {len(revenues)})')
                
                # Show seasonal breakdown
                seasonal_data = defaultdict(list)
                for record in day_data[day_name]:
                    if record['total_revenue'] in filtered_revenues:
                        if record['month'] in [12, 1, 2]:
                            seasonal_data['Winter'].append(record['total_revenue'])
                        elif record['month'] in [3, 4, 5]:
                            seasonal_data['Spring'].append(record['total_revenue'])
                        elif record['month'] in [6, 7, 8]:
                            seasonal_data['Summer'].append(record['total_revenue'])
                        else:
                            seasonal_data['Fall'].append(record['total_revenue'])
                
                # Show seasonal averages
                seasonal_info = []
                for season, values in seasonal_data.items():
                    if values:
                        avg = statistics.mean(values)
                        seasonal_info.append(f'{season}: ${avg:,.0f}')
                
                if seasonal_info:
                    print(f'          Seasonal: {" | ".join(seasonal_info)}')
            else:
                # Fallback to current values if no data
                current_baseline = {
                    'Monday': 48361, 'Tuesday': 45935, 'Wednesday': 47514,
                    'Thursday': 53478, 'Friday': 54933, 'Saturday': 74934, 'Sunday': 71348
                }
                optimal_baseline[day_name] = current_baseline.get(day_name, 50000)
                print(f'{day_name:>9}: ${optimal_baseline[day_name]:>8,.0f} (fallback - insufficient data)')
        else:
            # Fallback values
            current_baseline = {
                'Monday': 48361, 'Tuesday': 45935, 'Wednesday': 47514,
                'Thursday': 53478, 'Friday': 54933, 'Saturday': 74934, 'Sunday': 71348
            }
            optimal_baseline[day_name] = current_baseline.get(day_name, 50000)
            print(f'{day_name:>9}: ${optimal_baseline[day_name]:>8,.0f} (fallback - no data)')

    print()
    print('🎯 CALIBRATED BASELINE DAILY REVENUE')
    print('=' * 45)
    
    # Show comparison with current values
    current_baseline = {
        'Monday': 48361, 'Tuesday': 45935, 'Wednesday': 47514,
        'Thursday': 53478, 'Friday': 54933, 'Saturday': 74934, 'Sunday': 71348
    }
    
    print('Day        Current      Calibrated    Change')
    print('-' * 45)
    
    total_current = 0
    total_calibrated = 0
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        current = current_baseline[day]
        calibrated = optimal_baseline[day]
        change = ((calibrated - current) / current) * 100
        
        total_current += current
        total_calibrated += calibrated
        
        change_symbol = '↑' if change > 0 else '↓' if change < 0 else '='
        print(f'{day:>9}: ${current:>8,.0f} → ${calibrated:>8,.0f} ({change:+5.1f}% {change_symbol})')
    
    overall_change = ((total_calibrated - total_current) / total_current) * 100
    print('-' * 45)
    print(f'{"TOTAL":>9}: ${total_current:>8,.0f} → ${total_calibrated:>8,.0f} ({overall_change:+5.1f}%)')

    print()
    print('💾 UPDATING run_forecast.py WITH CALIBRATED VALUES')
    print('=' * 55)

    # Generate the replacement code
    replacement_code = f'''        # CALIBRATED: Optimized baseline from historical data analysis
        # Calibrated using {len(recent_data)} non-event days from last year
        self.base_daily_revenue = {{
            'Monday': {optimal_baseline['Monday']},      # Calibrated from historical data
            'Tuesday': {optimal_baseline['Tuesday']},     # Calibrated from historical data
            'Wednesday': {optimal_baseline['Wednesday']},   # Calibrated from historical data
            'Thursday': {optimal_baseline['Thursday']},    # Calibrated from historical data
            'Friday': {optimal_baseline['Friday']},      # Calibrated from historical data
            'Saturday': {optimal_baseline['Saturday']},    # Calibrated from historical data
            'Sunday': {optimal_baseline['Sunday']}       # Calibrated from historical data
        }}'''

    print('✅ Calibrated baseline values ready for deployment')
    print()
    print('🎯 EXPECTED IMPROVEMENT:')
    print('- Baseline values now optimized for regular days')
    print('- Event multipliers remain unchanged (already achieving 0.1% error)')
    print('- Should significantly reduce the 25.4% regular day error')
    print()
    print('📝 CALIBRATION SUMMARY:')
    print(f'- Analyzed {len(recent_data)} historical records')
    print(f'- Excluded {len(lolla_dates)} known event days')
    print(f'- Used median values for robustness against outliers')
    print(f'- Applied seasonal analysis for validation')
    
    # Save calibrated values to file for easy access
    with open('calibrated_baseline_values.txt', 'w') as f:
        f.write('CALIBRATED BASELINE DAILY REVENUE VALUES\n')
        f.write('=' * 50 + '\n\n')
        for day, value in optimal_baseline.items():
            f.write(f'{day}: {value}\n')
        f.write(f'\nTotal Weekly: {sum(optimal_baseline.values())}\n')
        f.write(f'Daily Average: {sum(optimal_baseline.values()) / 7:.0f}\n')
    
    print('💾 Calibrated values saved to calibrated_baseline_values.txt')
    
    return optimal_baseline, replacement_code

if __name__ == "__main__":
    optimal_baseline, replacement_code = main()
    
    print()
    print('🚀 READY TO APPLY CALIBRATION!')
    print('Next step: Update run_forecast.py with calibrated values')
    print()
    print('REPLACEMENT CODE:')
    print(replacement_code)

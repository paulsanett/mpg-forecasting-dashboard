#!/usr/bin/env python3
"""
Base Revenue Calibrator for MPG Forecasting System
Analyzes historical data to calibrate base daily revenue by:
- Day of week patterns
- Seasonal adjustments (monthly)
- Year-over-year changes
- Event vs non-event day patterns
"""

import csv
from datetime import datetime
import statistics
import json
from collections import defaultdict
from robust_csv_reader import RobustCSVReader

class BaseRevenueCalibrator:
    def __init__(self):
        self.historical_data = []
        self.csv_reader = RobustCSVReader()
        
        # Current base revenue (from existing system)
        self.current_base_revenue = {
            'Monday': 65326,
            'Tuesday': 58826,
            'Wednesday': 62597,
            'Thursday': 70064,
            'Friday': 77143,
            'Saturday': 113978,
            'Sunday': 103029
        }
        
        # Calibrated base revenue (to be calculated)
        self.calibrated_base_revenue = {}
        
        # Analysis results
        self.analysis_results = {}
    
    def load_historical_data(self):
        """Load and normalize historical booking data"""
        print("📊 Loading historical data for base revenue calibration...")
        
        # Load historical data using robust CSV reader
        self.csv_reader.filename = 'HIstoric Booking Data.csv'
        normalized_data = self.csv_reader.read_csv_robust()
        
        # Convert to analysis format
        for record in normalized_data:
            if record.get('total_revenue', 0) > 1000 and record.get('date'):
                date_obj = record['date']
                # Handle both datetime objects and strings
                if isinstance(date_obj, datetime):
                    date_str = date_obj.strftime('%Y-%m-%d')
                    year = str(date_obj.year)
                    month = date_obj.month
                else:
                    date_str = str(date_obj)
                    year = date_str[:4]
                    month = int(date_str[5:7])
                
                self.historical_data.append({
                    'date': date_str,
                    'year': year,
                    'month': month,
                    'day_of_week': record['day_of_week'],
                    'total_revenue': record['total_revenue'],
                    'garages': {
                        'Grant Park North': record.get('gpn_revenue', 0),
                        'Grant Park South': record.get('gps_revenue', 0),
                        'Millennium': record.get('millennium_revenue', 0),
                        'Lakeside': record.get('lakeside_revenue', 0),
                        'Online': record.get('online_revenue', 0)
                    }
                })
        
        print(f"✅ Loaded {len(self.historical_data)} historical records")
        return self.historical_data
    
    def analyze_day_of_week_patterns(self):
        """Analyze revenue patterns by day of week"""
        print("📈 Analyzing day-of-week revenue patterns...")
        
        # Group by day of week
        day_revenues = defaultdict(list)
        
        for record in self.historical_data:
            # Convert abbreviated day names to full names
            day_mapping = {
                'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
                'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
            }
            full_day = day_mapping.get(record['day_of_week'], record['day_of_week'])
            day_revenues[full_day].append(record['total_revenue'])
        
        # Calculate statistics for each day
        day_stats = {}
        for day, revenues in day_revenues.items():
            if revenues:
                day_stats[day] = {
                    'count': len(revenues),
                    'mean': statistics.mean(revenues),
                    'median': statistics.median(revenues),
                    'std_dev': statistics.stdev(revenues) if len(revenues) > 1 else 0,
                    'min': min(revenues),
                    'max': max(revenues)
                }
        
        self.analysis_results['day_of_week'] = day_stats
        
        # Display results
        print("\n📊 Day-of-Week Revenue Analysis:")
        print("=" * 80)
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in day_stats:
                stats = day_stats[day]
                current = self.current_base_revenue[day]
                actual_mean = stats['mean']
                error = ((current - actual_mean) / actual_mean) * 100
                
                print(f"{day:>9}: Current ${current:>7,.0f} | Actual ${actual_mean:>7,.0f} | Error: {error:>6.1f}% | Count: {stats['count']}")
        
        return day_stats
    
    def analyze_seasonal_patterns(self):
        """Analyze revenue patterns by month and season"""
        print("\n📅 Analyzing seasonal revenue patterns...")
        
        # Group by year and month
        monthly_revenues = defaultdict(lambda: defaultdict(list))
        
        for record in self.historical_data:
            year = record['year']
            month = record['month']
            monthly_revenues[year][month].append(record['total_revenue'])
        
        # Calculate monthly averages by year
        monthly_stats = {}
        for year, months in monthly_revenues.items():
            monthly_stats[year] = {}
            for month, revenues in months.items():
                if revenues:
                    monthly_stats[year][month] = {
                        'count': len(revenues),
                        'mean': statistics.mean(revenues),
                        'median': statistics.median(revenues)
                    }
        
        self.analysis_results['seasonal'] = monthly_stats
        
        # Display seasonal patterns
        print("\n📊 Monthly Revenue Patterns (Recent Years):")
        print("=" * 80)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for year in ['2023', '2024', '2025']:
            if year in monthly_stats:
                print(f"\n{year}:")
                for month in range(1, 13):
                    if month in monthly_stats[year]:
                        stats = monthly_stats[year][month]
                        print(f"  {month_names[month-1]:>3}: ${stats['mean']:>7,.0f} (n={stats['count']:>3})")
        
        return monthly_stats
    
    def analyze_year_over_year_changes(self):
        """Analyze year-over-year revenue changes"""
        print("\n📈 Analyzing year-over-year changes...")
        
        # Calculate annual averages
        yearly_revenues = defaultdict(list)
        
        for record in self.historical_data:
            yearly_revenues[record['year']].append(record['total_revenue'])
        
        yearly_stats = {}
        for year, revenues in yearly_revenues.items():
            if revenues:
                yearly_stats[year] = {
                    'count': len(revenues),
                    'mean': statistics.mean(revenues),
                    'total': sum(revenues)
                }
        
        self.analysis_results['yearly'] = yearly_stats
        
        # Display year-over-year changes
        print("\n📊 Year-over-Year Revenue Analysis:")
        print("=" * 50)
        years = sorted(yearly_stats.keys())
        for i, year in enumerate(years):
            stats = yearly_stats[year]
            if i > 0:
                prev_year = years[i-1]
                prev_mean = yearly_stats[prev_year]['mean']
                change = ((stats['mean'] - prev_mean) / prev_mean) * 100
                print(f"{year}: ${stats['mean']:>7,.0f} ({change:>+5.1f}% vs {prev_year}) | Days: {stats['count']}")
            else:
                print(f"{year}: ${stats['mean']:>7,.0f} (baseline) | Days: {stats['count']}")
        
        return yearly_stats
    
    def calculate_calibrated_base_revenue(self):
        """Calculate calibrated base revenue using historical analysis"""
        print("\n🎯 Calculating calibrated base revenue...")
        
        # Use recent data (2024-2025) for calibration, with 2023 as reference
        recent_data = [r for r in self.historical_data if r['year'] in ['2023', '2024', '2025']]
        
        # Group by day of week for recent data
        day_revenues = defaultdict(list)
        
        for record in recent_data:
            # Convert abbreviated day names to full names
            day_mapping = {
                'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
                'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
            }
            full_day = day_mapping.get(record['day_of_week'], record['day_of_week'])
            day_revenues[full_day].append(record['total_revenue'])
        
        # Calculate calibrated base revenue
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in day_revenues and day_revenues[day]:
                revenues = day_revenues[day]
                
                # Use median for robustness against outliers
                calibrated_value = statistics.median(revenues)
                
                # Apply conservative adjustment (blend with current)
                current_value = self.current_base_revenue[day]
                blended_value = (calibrated_value * 0.7) + (current_value * 0.3)
                
                self.calibrated_base_revenue[day] = int(blended_value)
            else:
                # Keep current value if no data
                self.calibrated_base_revenue[day] = self.current_base_revenue[day]
        
        # Display calibration results
        print("\n🎯 Base Revenue Calibration Results:")
        print("=" * 80)
        print(f"{'Day':>9} | {'Current':>10} | {'Calibrated':>12} | {'Change':>8} | {'% Change':>9}")
        print("-" * 80)
        
        total_current = 0
        total_calibrated = 0
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            current = self.current_base_revenue[day]
            calibrated = self.calibrated_base_revenue[day]
            change = calibrated - current
            pct_change = (change / current) * 100
            
            total_current += current
            total_calibrated += calibrated
            
            print(f"{day:>9} | ${current:>9,.0f} | ${calibrated:>11,.0f} | {change:>+7,.0f} | {pct_change:>+7.1f}%")
        
        total_change = total_calibrated - total_current
        total_pct_change = (total_change / total_current) * 100
        
        print("-" * 80)
        print(f"{'TOTAL':>9} | ${total_current:>9,.0f} | ${total_calibrated:>11,.0f} | {total_change:>+7,.0f} | {total_pct_change:>+7.1f}%")
        
        return self.calibrated_base_revenue
    
    def generate_seasonal_multipliers(self):
        """Generate seasonal adjustment multipliers by month"""
        print("\n🌍 Generating seasonal adjustment multipliers...")
        
        # Calculate monthly multipliers based on deviation from annual average
        seasonal_multipliers = {}
        
        if 'seasonal' in self.analysis_results:
            # Use 2024 data as primary reference
            if '2024' in self.analysis_results['seasonal']:
                monthly_data = self.analysis_results['seasonal']['2024']
                
                # Calculate annual average for 2024
                monthly_means = [stats['mean'] for stats in monthly_data.values()]
                annual_average = statistics.mean(monthly_means) if monthly_means else 70000
                
                # Generate multipliers for each month
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                print("\n📊 Seasonal Adjustment Multipliers (2024 baseline):")
                print("=" * 50)
                
                for month in range(1, 13):
                    if month in monthly_data:
                        monthly_avg = monthly_data[month]['mean']
                        multiplier = monthly_avg / annual_average
                        seasonal_multipliers[month] = multiplier
                        
                        print(f"{month_names[month-1]:>3}: {multiplier:>5.3f}x (${monthly_avg:>7,.0f})")
                    else:
                        seasonal_multipliers[month] = 1.0
                        print(f"{month_names[month-1]:>3}: {1.0:>5.3f}x (no data)")
        
        self.analysis_results['seasonal_multipliers'] = seasonal_multipliers
        return seasonal_multipliers
    
    def save_calibration_results(self):
        """Save calibration results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Reports/Base_Revenue_Calibration_{timestamp}.json"
        
        calibration_data = {
            'timestamp': timestamp,
            'current_base_revenue': self.current_base_revenue,
            'calibrated_base_revenue': self.calibrated_base_revenue,
            'analysis_results': self.analysis_results,
            'summary': {
                'total_records_analyzed': len(self.historical_data),
                'years_covered': list(set(r['year'] for r in self.historical_data)),
                'calibration_method': 'median_blend_70_30'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2, default=str)
        
        print(f"\n💾 Calibration results saved: {filename}")
        return filename
    
    def run_full_calibration(self):
        """Run complete base revenue calibration analysis"""
        print("🎯 STARTING BASE REVENUE CALIBRATION")
        print("=" * 80)
        
        # Load data
        self.load_historical_data()
        
        # Run analyses
        self.analyze_day_of_week_patterns()
        self.analyze_seasonal_patterns()
        self.analyze_year_over_year_changes()
        
        # Calculate calibrated values
        self.calculate_calibrated_base_revenue()
        self.generate_seasonal_multipliers()
        
        # Save results
        self.save_calibration_results()
        
        print("\n✅ BASE REVENUE CALIBRATION COMPLETE")
        print("=" * 80)
        
        return {
            'calibrated_base_revenue': self.calibrated_base_revenue,
            'seasonal_multipliers': self.analysis_results.get('seasonal_multipliers', {}),
            'analysis_results': self.analysis_results
        }

if __name__ == "__main__":
    calibrator = BaseRevenueCalibrator()
    results = calibrator.run_full_calibration()

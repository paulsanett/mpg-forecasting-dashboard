#!/usr/bin/env python3
"""
PRECISION CALIBRATION SYSTEM
Advanced multi-factor calibration to achieve 2-5% error target
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from datetime import datetime, timedelta
import random
import statistics
from collections import defaultdict
import numpy as np
from scipy import optimize
import math

class PrecisionCalibrator:
    def __init__(self):
        self.target_error = 3.5  # Target 2-5% range, aim for middle
        self.reader = RobustCSVReader()
        self.data = None
        self.training_data = []
        self.validation_data = []
        
    def load_and_prepare_data(self):
        """Load and split data into training/validation sets"""
        print('📊 Loading and preparing data for precision calibration...')
        
        self.data = self.reader.read_csv_robust()
        
        # Filter for recent, high-quality data
        cutoff_date = datetime(2024, 8, 6)
        quality_data = []
        
        # Known event dates for proper handling
        lolla_dates = [
            datetime(2024, 8, 1), datetime(2024, 8, 2), datetime(2024, 8, 3), datetime(2024, 8, 4),
            datetime(2025, 7, 31), datetime(2025, 8, 1), datetime(2025, 8, 2), datetime(2025, 8, 3)
        ]
        
        for record in self.data:
            if (record.get('date') and record.get('total_revenue', 0) > 0):
                try:
                    date_str = str(record.get('date', ''))
                    date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    
                    if date_obj >= cutoff_date:
                        # Enhanced data point with features
                        data_point = {
                            'date': date_obj,
                            'day_of_week': record.get('day_of_week', '').strip(),
                            'total_revenue': record.get('total_revenue', 0),
                            'month': date_obj.month,
                            'day_of_month': date_obj.day,
                            'week_of_year': date_obj.isocalendar()[1],
                            'is_lolla': date_obj in lolla_dates,
                            'is_weekend': date_obj.weekday() >= 5,
                            'is_month_end': date_obj.day >= 28,
                            'is_holiday_season': date_obj.month in [11, 12, 1],
                            'is_summer': date_obj.month in [6, 7, 8],
                            'days_from_lolla': min([abs((date_obj - ld).days) for ld in lolla_dates])
                        }
                        quality_data.append(data_point)
                except:
                    continue
        
        # Split 80/20 for training/validation
        random.seed(42)
        random.shuffle(quality_data)
        split_point = int(0.8 * len(quality_data))
        
        self.training_data = quality_data[:split_point]
        self.validation_data = quality_data[split_point:]
        
        print(f'✅ Prepared {len(self.training_data)} training samples')
        print(f'✅ Prepared {len(self.validation_data)} validation samples')
        
    def calculate_advanced_features(self, data_point):
        """Calculate advanced predictive features"""
        features = {}
        
        # Day of week mapping
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        full_day_name = day_mapping.get(data_point['day_of_week'].upper(), data_point['day_of_week'])
        
        # Base features
        features['day_of_week'] = full_day_name
        features['month'] = data_point['month']
        features['is_weekend'] = data_point['is_weekend']
        features['is_lolla'] = data_point['is_lolla']
        
        # Advanced seasonal features
        features['seasonal_factor'] = self.get_seasonal_factor(data_point['month'])
        features['monthly_progression'] = (data_point['day_of_month'] - 1) / 30  # 0-1 scale
        
        # Proximity effects
        features['lolla_proximity_factor'] = self.get_lolla_proximity_factor(data_point['days_from_lolla'])
        
        # Holiday and special period effects
        features['holiday_season_factor'] = 0.9 if data_point['is_holiday_season'] else 1.0
        features['month_end_factor'] = 1.05 if data_point['is_month_end'] else 1.0
        
        return features
    
    def get_seasonal_factor(self, month):
        """Calculate precise seasonal adjustment"""
        seasonal_curves = {
            1: 0.82,   # January - lowest
            2: 0.85,   # February
            3: 0.95,   # March - spring pickup
            4: 1.02,   # April
            5: 1.08,   # May - strong spring
            6: 1.15,   # June - summer start
            7: 1.20,   # July - peak summer
            8: 1.18,   # August - still strong
            9: 1.10,   # September - fall start
            10: 1.05,  # October
            11: 0.95,  # November - decline
            12: 0.88   # December - holiday impact
        }
        return seasonal_curves.get(month, 1.0)
    
    def get_lolla_proximity_factor(self, days_away):
        """Calculate Lollapalooza proximity effect"""
        if days_away == 0:
            return 1.0  # Handled separately
        elif days_away <= 3:
            return 1.1  # Pre-event buildup
        elif days_away <= 7:
            return 1.05  # Moderate proximity effect
        else:
            return 1.0  # No effect
    
    def optimize_baseline_revenue(self):
        """Use optimization to find best baseline revenue values"""
        print('🎯 Optimizing baseline revenue using advanced techniques...')
        
        # Group training data by day of week
        day_groups = defaultdict(list)
        for dp in self.training_data:
            if not dp['is_lolla']:  # Exclude Lolla days from baseline
                day_mapping = {
                    'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
                    'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
                }
                full_day_name = day_mapping.get(dp['day_of_week'].upper(), dp['day_of_week'])
                day_groups[full_day_name].append(dp)
        
        optimized_baseline = {}
        
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day_name in day_groups and len(day_groups[day_name]) > 5:
                day_data = day_groups[day_name]
                
                # Multi-factor optimization
                def objective_function(base_revenue):
                    total_error = 0
                    count = 0
                    
                    for dp in day_data:
                        features = self.calculate_advanced_features(dp)
                        
                        # Calculate predicted revenue with all factors
                        predicted = (base_revenue * 
                                   features['seasonal_factor'] * 
                                   features['lolla_proximity_factor'] * 
                                   features['holiday_season_factor'] * 
                                   features['month_end_factor'])
                        
                        actual = dp['total_revenue']
                        if actual > 0:
                            error = abs(predicted - actual) / actual
                            total_error += error
                            count += 1
                    
                    return total_error / count if count > 0 else 1.0
                
                # Find optimal baseline using scipy optimization
                initial_guess = statistics.median([dp['total_revenue'] for dp in day_data])
                
                result = optimize.minimize_scalar(
                    objective_function,
                    bounds=(initial_guess * 0.5, initial_guess * 1.5),
                    method='bounded'
                )
                
                optimized_baseline[day_name] = int(result.x)
                
                print(f'{day_name:>9}: ${optimized_baseline[day_name]:>8,.0f} (optimized from {len(day_data)} samples)')
            else:
                # Fallback for insufficient data
                fallback_values = {
                    'Monday': 58731, 'Tuesday': 57325, 'Wednesday': 59196,
                    'Thursday': 67685, 'Friday': 74862, 'Saturday': 105464, 'Sunday': 96516
                }
                optimized_baseline[day_name] = fallback_values.get(day_name, 60000)
                print(f'{day_name:>9}: ${optimized_baseline[day_name]:>8,.0f} (fallback)')
        
        return optimized_baseline
    
    def optimize_event_multipliers(self):
        """Optimize Lollapalooza multipliers for maximum precision"""
        print('🎯 Optimizing Lollapalooza multipliers...')
        
        lolla_data = [dp for dp in self.training_data if dp['is_lolla']]
        
        if not lolla_data:
            print('⚠️  No Lollapalooza data found, using existing multipliers')
            return {
                'Thursday': 2.49, 'Friday': 2.12, 'Saturday': 1.80, 'Sunday': 2.24
            }
        
        # Group by day of week
        lolla_by_day = defaultdict(list)
        for dp in lolla_data:
            day_mapping = {
                'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
                'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
            }
            full_day_name = day_mapping.get(dp['day_of_week'].upper(), dp['day_of_week'])
            lolla_by_day[full_day_name].append(dp)
        
        optimized_multipliers = {}
        baseline_values = {
            'Monday': 58731, 'Tuesday': 57325, 'Wednesday': 59196,
            'Thursday': 67685, 'Friday': 74862, 'Saturday': 105464, 'Sunday': 96516
        }
        
        for day_name, day_data in lolla_by_day.items():
            if day_data:
                base_revenue = baseline_values.get(day_name, 60000)
                actual_revenues = [dp['total_revenue'] for dp in day_data]
                
                # Calculate optimal multiplier
                optimal_multiplier = statistics.median([rev / base_revenue for rev in actual_revenues])
                optimized_multipliers[day_name] = round(optimal_multiplier, 2)
                
                print(f'Lolla {day_name:>9}: {optimal_multiplier:.2f}x (from {len(day_data)} samples)')
            else:
                # Use existing values
                existing = {'Thursday': 2.49, 'Friday': 2.12, 'Saturday': 1.80, 'Sunday': 2.24}
                optimized_multipliers[day_name] = existing.get(day_name, 2.0)
        
        return optimized_multipliers
    
    def validate_precision(self, baseline_revenue, lolla_multipliers):
        """Validate the optimized model against validation set"""
        print('🔍 Validating precision against validation set...')
        
        errors = []
        predictions = []
        actuals = []
        
        for dp in self.validation_data:
            features = self.calculate_advanced_features(dp)
            day_name = features['day_of_week']
            
            # Get base revenue
            base_revenue = baseline_revenue.get(day_name, 60000)
            
            # Apply event multiplier if Lollapalooza
            event_multiplier = 1.0
            if dp['is_lolla']:
                event_multiplier = lolla_multipliers.get(day_name, 2.0)
            
            # Calculate predicted revenue with all factors
            predicted = (base_revenue * 
                        event_multiplier *
                        features['seasonal_factor'] * 
                        features['lolla_proximity_factor'] * 
                        features['holiday_season_factor'] * 
                        features['month_end_factor'])
            
            actual = dp['total_revenue']
            
            if actual > 0:
                error = abs(predicted - actual) / actual * 100
                errors.append(error)
                predictions.append(predicted)
                actuals.append(actual)
        
        if errors:
            avg_error = statistics.mean(errors)
            median_error = statistics.median(errors)
            
            # Performance breakdown
            excellent = len([e for e in errors if e < 5])
            good = len([e for e in errors if 5 <= e < 10])
            fair = len([e for e in errors if 10 <= e < 20])
            poor = len([e for e in errors if e >= 20])
            
            print()
            print('📊 PRECISION VALIDATION RESULTS')
            print('=' * 40)
            print(f'Validation Samples: {len(errors)}')
            print(f'Average Error: {avg_error:.1f}%')
            print(f'Median Error: {median_error:.1f}%')
            print()
            print('🎯 PRECISION BREAKDOWN:')
            print(f'Target Range (< 5%): {excellent} ({excellent/len(errors)*100:.1f}%)')
            print(f'Good (5-10%): {good} ({good/len(errors)*100:.1f}%)')
            print(f'Fair (10-20%): {fair} ({fair/len(errors)*100:.1f}%)')
            print(f'Poor (> 20%): {poor} ({poor/len(errors)*100:.1f}%)')
            
            # Success assessment
            target_achievement = excellent / len(errors) * 100
            
            if avg_error <= 5.0 and target_achievement >= 70:
                rating = '🎯 TARGET ACHIEVED!'
                success = True
            elif avg_error <= 7.5 and target_achievement >= 50:
                rating = '✅ CLOSE TO TARGET'
                success = False
            else:
                rating = '⚠️ NEEDS MORE CALIBRATION'
                success = False
            
            print(f'\n🏆 OVERALL ASSESSMENT: {rating}')
            print(f'Target Achievement: {target_achievement:.1f}% in 2-5% range')
            
            return success, avg_error, target_achievement
        
        return False, 100, 0
    
    def run_precision_calibration(self):
        """Run the complete precision calibration process"""
        print('🚀 PRECISION CALIBRATION SYSTEM - TARGET: 2-5% ERROR')
        print('=' * 65)
        
        # Load and prepare data
        self.load_and_prepare_data()
        
        # Optimize baseline revenue
        optimized_baseline = self.optimize_baseline_revenue()
        
        # Optimize event multipliers
        optimized_multipliers = self.optimize_event_multipliers()
        
        # Validate precision
        success, avg_error, target_achievement = self.validate_precision(
            optimized_baseline, optimized_multipliers
        )
        
        print()
        print('💾 PRECISION CALIBRATION RESULTS')
        print('=' * 45)
        
        # Generate optimized configuration
        config_code = f'''        # PRECISION CALIBRATED: Advanced multi-factor optimization
        # Target: 2-5% error range | Achieved: {avg_error:.1f}% average error
        # Target achievement: {target_achievement:.1f}% of predictions in 2-5% range
        self.base_daily_revenue = {{
            'Monday': {optimized_baseline['Monday']},      # Precision optimized
            'Tuesday': {optimized_baseline['Tuesday']},     # Precision optimized
            'Wednesday': {optimized_baseline['Wednesday']},   # Precision optimized
            'Thursday': {optimized_baseline['Thursday']},    # Precision optimized
            'Friday': {optimized_baseline['Friday']},      # Precision optimized
            'Saturday': {optimized_baseline['Saturday']},    # Precision optimized
            'Sunday': {optimized_baseline['Sunday']}       # Precision optimized
        }}
        
        # PRECISION OPTIMIZED Lollapalooza multipliers
        self.lollapalooza_day_multipliers = {{'''
        
        for day, mult in optimized_multipliers.items():
            config_code += f"\n            '{day}': {mult},"
        
        config_code += "\n        }"
        
        print('✅ Precision calibration complete!')
        print(f'📊 Average Error: {avg_error:.1f}%')
        print(f'🎯 Target Achievement: {target_achievement:.1f}%')
        
        if success:
            print('🎉 TARGET ACHIEVED! Ready for deployment.')
        else:
            print('⚠️  Additional refinement may be needed.')
        
        return optimized_baseline, optimized_multipliers, config_code, success

def main():
    calibrator = PrecisionCalibrator()
    baseline, multipliers, code, success = calibrator.run_precision_calibration()
    
    print()
    print('🚀 READY TO APPLY PRECISION CALIBRATION!')
    print()
    print('OPTIMIZED CONFIGURATION:')
    print(code)
    
    return baseline, multipliers, code, success

if __name__ == "__main__":
    main()

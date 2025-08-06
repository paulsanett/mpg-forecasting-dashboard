#!/usr/bin/env python3
"""
HYBRID PRECISION FORECASTING SYSTEM
Combines multiple approaches to achieve 2-5% error target:
1. Individual day-specific models for each day of week
2. Event-specific models for Lollapalooza
3. Seasonal adjustment layers
4. Outlier detection and correction
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

class HybridPrecisionSystem:
    def __init__(self):
        self.target_error = 3.5  # Target 2-5% range
        self.reader = RobustCSVReader()
        self.data = None
        self.day_specific_models = {}
        self.event_models = {}
        
    def load_and_analyze_patterns(self):
        """Deep analysis of revenue patterns by day, season, and events"""
        print('🔍 Deep pattern analysis for hybrid precision system...')
        
        self.data = self.reader.read_csv_robust()
        
        # Filter for recent, high-quality data
        cutoff_date = datetime(2024, 8, 6)
        pattern_data = []
        
        # Known event dates
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
                        data_point = {
                            'date': date_obj,
                            'day_of_week': record.get('day_of_week', '').strip(),
                            'total_revenue': record.get('total_revenue', 0),
                            'month': date_obj.month,
                            'is_lolla': date_obj in lolla_dates,
                            'season': self.get_season(date_obj.month),
                            'week_of_month': (date_obj.day - 1) // 7 + 1
                        }
                        pattern_data.append(data_point)
                except:
                    continue
        
        print(f'✅ Analyzing {len(pattern_data)} data points for patterns')
        return pattern_data
    
    def get_season(self, month):
        """Get season for month"""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def build_day_specific_models(self, pattern_data):
        """Build highly specific models for each day of week"""
        print('🎯 Building day-specific precision models...')
        
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        # Group data by day of week (excluding Lolla days for baseline)
        day_groups = defaultdict(list)
        for dp in pattern_data:
            if not dp['is_lolla']:  # Build baseline models without events
                full_day_name = day_mapping.get(dp['day_of_week'].upper(), dp['day_of_week'])
                day_groups[full_day_name].append(dp)
        
        day_models = {}
        
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day_name in day_groups and len(day_groups[day_name]) >= 10:
                day_data = day_groups[day_name]
                
                # Advanced day-specific analysis
                model = self.create_advanced_day_model(day_name, day_data)
                day_models[day_name] = model
                
                print(f'{day_name:>9}: {len(day_data)} samples → {model["accuracy"]:.1f}% accuracy')
            else:
                # Fallback model
                day_models[day_name] = {
                    'base_revenue': 60000,
                    'seasonal_adjustments': {'Winter': 0.85, 'Spring': 1.0, 'Summer': 1.15, 'Fall': 1.0},
                    'accuracy': 20.0
                }
                print(f'{day_name:>9}: Fallback model (insufficient data)')
        
        return day_models
    
    def create_advanced_day_model(self, day_name, day_data):
        """Create advanced model for specific day of week"""
        
        # Group by season for seasonal patterns
        seasonal_data = defaultdict(list)
        for dp in day_data:
            seasonal_data[dp['season']].append(dp['total_revenue'])
        
        # Calculate seasonal adjustments
        overall_median = statistics.median([dp['total_revenue'] for dp in day_data])
        seasonal_adjustments = {}
        
        for season in ['Winter', 'Spring', 'Summer', 'Fall']:
            if season in seasonal_data and len(seasonal_data[season]) >= 3:
                season_median = statistics.median(seasonal_data[season])
                seasonal_adjustments[season] = season_median / overall_median
            else:
                # Default seasonal adjustments
                defaults = {'Winter': 0.85, 'Spring': 1.0, 'Summer': 1.15, 'Fall': 1.0}
                seasonal_adjustments[season] = defaults[season]
        
        # Remove outliers for base calculation
        revenues = [dp['total_revenue'] for dp in day_data]
        q1 = np.percentile(revenues, 25)
        q3 = np.percentile(revenues, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered_revenues = [r for r in revenues if lower_bound <= r <= upper_bound]
        
        # Use median of filtered data for stability
        base_revenue = statistics.median(filtered_revenues) if filtered_revenues else overall_median
        
        # Calculate model accuracy on training data
        errors = []
        for dp in day_data:
            predicted = base_revenue * seasonal_adjustments[dp['season']]
            actual = dp['total_revenue']
            error = abs(predicted - actual) / actual * 100
            errors.append(error)
        
        accuracy = statistics.median(errors) if errors else 20.0
        
        return {
            'base_revenue': int(base_revenue),
            'seasonal_adjustments': seasonal_adjustments,
            'accuracy': accuracy,
            'sample_count': len(day_data),
            'filtered_count': len(filtered_revenues)
        }
    
    def build_event_models(self, pattern_data):
        """Build precise models for Lollapalooza events"""
        print('🎯 Building event-specific precision models...')
        
        # Get Lollapalooza data
        lolla_data = [dp for dp in pattern_data if dp['is_lolla']]
        
        if not lolla_data:
            print('⚠️  No Lollapalooza data found')
            return {
                'Thursday': 2.49, 'Friday': 2.12, 'Saturday': 1.80, 'Sunday': 2.24
            }
        
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        # Group by day of week
        lolla_by_day = defaultdict(list)
        for dp in lolla_data:
            full_day_name = day_mapping.get(dp['day_of_week'].upper(), dp['day_of_week'])
            lolla_by_day[full_day_name].append(dp)
        
        event_models = {}
        
        for day_name, day_data in lolla_by_day.items():
            if day_data:
                # Calculate precise multiplier for this day
                base_revenue = self.day_specific_models[day_name]['base_revenue']
                
                # Account for seasonal adjustment
                multipliers = []
                for dp in day_data:
                    seasonal_adj = self.day_specific_models[day_name]['seasonal_adjustments'][dp['season']]
                    expected_base = base_revenue * seasonal_adj
                    multiplier = dp['total_revenue'] / expected_base
                    multipliers.append(multiplier)
                
                # Use median for robustness
                optimal_multiplier = statistics.median(multipliers)
                event_models[day_name] = round(optimal_multiplier, 2)
                
                print(f'Lolla {day_name:>9}: {optimal_multiplier:.2f}x (from {len(day_data)} samples)')
            else:
                # Use existing validated multipliers
                existing = {'Thursday': 2.49, 'Friday': 2.12, 'Saturday': 1.80, 'Sunday': 2.24}
                event_models[day_name] = existing.get(day_name, 2.0)
        
        return event_models
    
    def validate_hybrid_system(self, pattern_data):
        """Validate the complete hybrid system"""
        print('🔍 Validating hybrid precision system...')
        
        # Split data for validation
        random.seed(42)
        random.shuffle(pattern_data)
        split_point = int(0.8 * len(pattern_data))
        validation_data = pattern_data[split_point:]
        
        errors = []
        event_errors = []
        regular_errors = []
        
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        for dp in validation_data:
            full_day_name = day_mapping.get(dp['day_of_week'].upper(), dp['day_of_week'])
            
            # Get day-specific model
            day_model = self.day_specific_models[full_day_name]
            base_revenue = day_model['base_revenue']
            seasonal_adj = day_model['seasonal_adjustments'][dp['season']]
            
            # Apply event multiplier if needed
            event_multiplier = 1.0
            if dp['is_lolla']:
                event_multiplier = self.event_models.get(full_day_name, 2.0)
            
            # Calculate prediction
            predicted = base_revenue * seasonal_adj * event_multiplier
            actual = dp['total_revenue']
            
            if actual > 0:
                error = abs(predicted - actual) / actual * 100
                errors.append(error)
                
                if dp['is_lolla']:
                    event_errors.append(error)
                else:
                    regular_errors.append(error)
        
        if errors:
            avg_error = statistics.mean(errors)
            median_error = statistics.median(errors)
            
            # Performance breakdown
            target_range = len([e for e in errors if e < 5])
            good = len([e for e in errors if 5 <= e < 10])
            fair = len([e for e in errors if 10 <= e < 20])
            poor = len([e for e in errors if e >= 20])
            
            print()
            print('📊 HYBRID SYSTEM VALIDATION RESULTS')
            print('=' * 45)
            print(f'Validation Samples: {len(errors)}')
            print(f'Average Error: {avg_error:.1f}%')
            print(f'Median Error: {median_error:.1f}%')
            
            if event_errors:
                print(f'Event Day Avg Error: {statistics.mean(event_errors):.1f}% ({len(event_errors)} days)')
            if regular_errors:
                print(f'Regular Day Avg Error: {statistics.mean(regular_errors):.1f}% ({len(regular_errors)} days)')
            
            print()
            print('🎯 PRECISION BREAKDOWN:')
            print(f'Target Range (< 5%): {target_range} ({target_range/len(errors)*100:.1f}%)')
            print(f'Good (5-10%): {good} ({good/len(errors)*100:.1f}%)')
            print(f'Fair (10-20%): {fair} ({fair/len(errors)*100:.1f}%)')
            print(f'Poor (> 20%): {poor} ({poor/len(errors)*100:.1f}%)')
            
            # Success assessment
            target_achievement = target_range / len(errors) * 100
            
            if avg_error <= 5.0 and target_achievement >= 60:
                rating = '🎯 TARGET ACHIEVED!'
                success = True
            elif avg_error <= 7.5 and target_achievement >= 40:
                rating = '✅ VERY CLOSE TO TARGET'
                success = False
            else:
                rating = '⚠️ NEEDS REFINEMENT'
                success = False
            
            print(f'\n🏆 OVERALL ASSESSMENT: {rating}')
            print(f'Target Achievement: {target_achievement:.1f}% in 2-5% range')
            
            return success, avg_error, target_achievement
        
        return False, 100, 0
    
    def run_hybrid_calibration(self):
        """Run the complete hybrid calibration process"""
        print('🚀 HYBRID PRECISION FORECASTING SYSTEM')
        print('=' * 60)
        print('Multi-model approach targeting 2-5% error range')
        print()
        
        # Load and analyze patterns
        pattern_data = self.load_and_analyze_patterns()
        
        if len(pattern_data) < 50:
            print('❌ Insufficient data for hybrid calibration')
            return None, None, None, False
        
        # Build day-specific models
        self.day_specific_models = self.build_day_specific_models(pattern_data)
        
        # Build event models
        self.event_models = self.build_event_models(pattern_data)
        
        # Validate complete system
        success, avg_error, target_achievement = self.validate_hybrid_system(pattern_data)
        
        print()
        print('💾 HYBRID SYSTEM RESULTS')
        print('=' * 35)
        
        # Generate optimized configuration
        config_code = f'''        # HYBRID PRECISION SYSTEM: Multi-model approach
        # Average error: {avg_error:.1f}% | Target achievement: {target_achievement:.1f}%
        # Uses day-specific models with seasonal adjustments
        self.base_daily_revenue = {{'''
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            base = self.day_specific_models[day]['base_revenue']
            accuracy = self.day_specific_models[day]['accuracy']
            config_code += f"\n            '{day}': {base},      # {accuracy:.1f}% accuracy"
        
        config_code += "\n        }\n        \n        # HYBRID EVENT MULTIPLIERS\n        self.lollapalooza_day_multipliers = {"
        
        for day, mult in self.event_models.items():
            config_code += f"\n            '{day}': {mult},"
        
        config_code += "\n        }"
        
        print(f'📊 Average Error: {avg_error:.1f}%')
        print(f'🎯 Target Achievement: {target_achievement:.1f}%')
        
        if success:
            print('🎉 TARGET ACHIEVED!')
        elif avg_error <= 10:
            print('✅ Significant improvement achieved')
        else:
            print('⚠️ Additional refinement needed')
        
        return self.day_specific_models, self.event_models, config_code, success

def main():
    calibrator = HybridPrecisionSystem()
    day_models, event_models, code, success = calibrator.run_hybrid_calibration()
    
    if day_models:
        print()
        print('🚀 HYBRID CALIBRATION COMPLETE!')
        print()
        print('OPTIMIZED CONFIGURATION:')
        print(code)
        
        return day_models, event_models, code, success
    else:
        print('❌ Hybrid calibration failed')
        return None, None, None, False

if __name__ == "__main__":
    main()

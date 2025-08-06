#!/usr/bin/env python3
"""
ENHANCED MODEL VALIDATOR
========================

Validates the Enhanced Comprehensive Forecasting System (v5.0 + Holiday Handler)
against historical data to measure accuracy improvements and identify remaining outliers.

Target: Achieve 2-5% accuracy range consistently

Author: Cascade AI
Date: 2025-08-06
"""

import random
import json
import csv
import statistics
from datetime import datetime, timedelta
from comprehensive_forecasting_engine import ComprehensiveForecastingEngine
from holiday_special_date_handler import HolidaySpecialDateHandler
from robust_csv_reader import RobustCSVReader

class EnhancedModelValidator:
    """Validates enhanced comprehensive forecasting model accuracy"""
    
    def __init__(self):
        self.comprehensive_engine = ComprehensiveForecastingEngine()
        self.holiday_handler = HolidaySpecialDateHandler()
        self.csv_reader = RobustCSVReader()
        self.validation_results = []
        
        print("🎯 ENHANCED MODEL VALIDATOR")
        print("=" * 60)
        print("Testing: Comprehensive Model v5.0 + Holiday Handler")
        print("Target: 2-5% accuracy range")
        print("=" * 60)
        
    def load_historical_events(self, target_date):
        """Load historical events for a specific date"""
        year = target_date[:4]
        event_calendars = {
            '2023': 'MG Event Calendar 2023.csv',
            '2024': 'MG Event Calendar 2024.csv',
            '2025': 'MG Event Calendar 2025.csv'
        }
        
        events = []
        calendar_file = event_calendars.get(year)
        if calendar_file:
            try:
                with open(calendar_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        event_name = row.get('Event Name', '').strip()
                        start_date = row.get('Start Date', '').strip()
                        tier = row.get('Tier', 'Tier 3').strip()
                        
                        if event_name and start_date:
                            try:
                                event_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                                if event_date == target_date:
                                    events.append({
                                        'name': event_name,
                                        'tier': tier
                                    })
                            except ValueError:
                                continue
            except FileNotFoundError:
                pass
        
        return events
    
    def extract_weather_from_notes(self, notes):
        """Extract weather information from historical notes"""
        if not notes:
            return None
        
        notes_lower = notes.lower()
        
        # Temperature extraction
        temp = None
        if '°' in notes:
            import re
            temp_match = re.search(r'(\d+)°', notes)
            if temp_match:
                temp = int(temp_match.group(1))
        
        # Weather description
        weather_conditions = {
            'rain': ['rain', 'rainy', 'shower', 'drizzle', 'storm'],
            'snow': ['snow', 'snowy', 'blizzard', 'ice'],
            'sunny': ['sunny', 'clear', 'nice', 'beautiful'],
            'cloudy': ['cloudy', 'overcast', 'partly cloudy'],
            'hot': ['hot', 'heat', 'warm'],
            'cold': ['cold', 'freezing', 'chilly']
        }
        
        description = "partly cloudy"  # default
        for condition, keywords in weather_conditions.items():
            if any(keyword in notes_lower for keyword in keywords):
                description = condition
                break
        
        return {
            'temperature': temp,
            'description': description
        } if temp or description != "partly cloudy" else None
    
    def run_enhanced_validation(self, num_tests=50, focus_on_outliers=True):
        """Run enhanced validation tests with focus on previous outliers"""
        print(f"🔬 Running {num_tests} enhanced validation tests...")
        
        # Build the comprehensive model first
        print("🔧 Building comprehensive model...")
        self.comprehensive_engine.build_comprehensive_model()
        
        # Get historical data for validation
        self.csv_reader.filename = 'HIstoric Booking Data.csv'
        historical_data = self.csv_reader.read_csv_robust()
        
        # Filter valid records
        valid_records = []
        for record in historical_data:
            if (record.get('total_revenue', 0) > 1000 and 
                record.get('date') and 
                record.get('day_of_week')):
                
                date_obj = record['date']
                if isinstance(date_obj, datetime):
                    year = date_obj.year
                    date_str = date_obj.strftime('%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')
                else:
                    year = int(str(date_obj)[:4])
                    date_str = str(date_obj)
                    day_of_week = record.get('day_of_week', 'Unknown')
                
                # Skip COVID years
                if year not in [2020, 2021]:
                    valid_records.append({
                        'date': date_str,
                        'year': year,
                        'day_of_week': day_of_week,
                        'actual_revenue': float(record.get('total_revenue', 0)),
                        'notes': record.get('notes', '')
                    })
        
        # If focusing on outliers, include known problematic dates
        outlier_dates = [
            '2023-07-01',  # 142% error Saturday
            '2024-01-01',  # 56% error New Year's Monday
            '2017-05-27',  # 42.9% error Memorial Day weekend
            '2025-03-07',  # 37% error Friday
            '2024-12-05',  # 33.9% error Thursday
            '2024-02-03',  # 29.9% error Saturday
            '2022-09-10',  # 20.9% error Saturday
        ]
        
        if focus_on_outliers:
            # Include outlier dates if they exist in our data
            outlier_records = [r for r in valid_records if r['date'] in outlier_dates]
            regular_records = [r for r in valid_records if r['date'] not in outlier_dates]
            
            # Take some outliers and fill the rest with random records
            test_records = outlier_records[:min(15, len(outlier_records))]
            remaining_slots = num_tests - len(test_records)
            if remaining_slots > 0:
                test_records.extend(random.sample(regular_records, min(remaining_slots, len(regular_records))))
        else:
            test_records = random.sample(valid_records, min(num_tests, len(valid_records)))
        
        print(f"📊 Testing {len(test_records)} records (including {len([r for r in test_records if r['date'] in outlier_dates])} known outliers)")
        
        self.validation_results = []
        errors = []
        
        for i, record in enumerate(test_records, 1):
            date = record['date']
            day_of_week = record['day_of_week']
            actual_revenue = record['actual_revenue']
            
            # Load events for this date
            events = self.load_historical_events(date)
            
            # Create mock weather data from notes
            weather = self.extract_weather_from_notes(record['notes'])
            
            # Make prediction using comprehensive model
            comprehensive_prediction = self.comprehensive_engine.predict_revenue(date, day_of_week, events, weather)
            
            # Apply holiday/special date adjustments
            holiday_adjustment = self.holiday_handler.apply_special_adjustment(
                comprehensive_prediction['predicted_revenue'], date, weather
            )
            
            predicted_revenue = holiday_adjustment['adjusted_prediction']
            
            # Calculate error
            error_pct = abs(predicted_revenue - actual_revenue) / actual_revenue * 100
            errors.append(error_pct)
            
            # Store detailed results
            result = {
                'test_number': i,
                'date': date,
                'year': record['year'],
                'day_of_week': day_of_week,
                'actual_revenue': actual_revenue,
                'predicted_revenue': predicted_revenue,
                'error_percent': error_pct,
                'events': [e['name'] for e in events],
                'comprehensive_prediction': comprehensive_prediction['predicted_revenue'],
                'holiday_adjustment': holiday_adjustment['adjustment_factor'],
                'holiday_type': holiday_adjustment['adjustment_type'],
                'is_known_outlier': date in outlier_dates
            }
            self.validation_results.append(result)
            
            # Progress indicator with outlier marking
            outlier_mark = "🎯" if date in outlier_dates else ""
            status = "✅" if error_pct <= 5 else "⚠️" if error_pct <= 15 else "❌"
            print(f"[{i}/{len(test_records)}] {date} ({day_of_week[:3].upper()}): {status}{outlier_mark} "
                  f"Actual: ${actual_revenue:,.0f}, Predicted: ${predicted_revenue:,.0f}, "
                  f"Error: {error_pct:.1f}% (Holiday: {holiday_adjustment['adjustment_factor']:.1f}x)")
        
        # Calculate overall statistics
        mean_error = statistics.mean(errors)
        median_error = statistics.median(errors)
        std_error = statistics.stdev(errors) if len(errors) > 1 else 0
        
        # Categorize results
        excellent = len([e for e in errors if e <= 5])
        good = len([e for e in errors if 5 < e <= 15])
        fair = len([e for e in errors if 15 < e <= 30])
        poor = len([e for e in errors if e > 30])
        
        # Analyze outlier performance
        outlier_results = [r for r in self.validation_results if r['is_known_outlier']]
        outlier_errors = [r['error_percent'] for r in outlier_results]
        outlier_improvement = len([e for e in outlier_errors if e <= 15]) if outlier_errors else 0
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 ENHANCED MODEL VALIDATION RESULTS")
        print("=" * 80)
        print(f"🎯 TARGET ACCURACY: 2-5% error range")
        print(f"📈 ACTUAL PERFORMANCE:")
        print(f"   • Mean Error:     {mean_error:.1f}%")
        print(f"   • Median Error:   {median_error:.1f}%")
        print(f"   • Std Deviation:  {std_error:.1f}%")
        print(f"   • Best Prediction: {min(errors):.1f}% error")
        print(f"   • Worst Prediction: {max(errors):.1f}% error")
        print()
        print("📊 ACCURACY DISTRIBUTION:")
        print(f"   • Excellent (≤5% error):    {excellent} predictions ({excellent/len(errors)*100:.1f}%)")
        print(f"   • Good (5-15% error):       {good} predictions ({good/len(errors)*100:.1f}%)")
        print(f"   • Fair (15-30% error):      {fair} predictions ({fair/len(errors)*100:.1f}%)")
        print(f"   • Poor (>30% error):        {poor} predictions ({poor/len(errors)*100:.1f}%)")
        print()
        
        if outlier_errors:
            print(f"🎯 OUTLIER PERFORMANCE:")
            print(f"   • Known outliers tested: {len(outlier_errors)}")
            print(f"   • Outliers now ≤15% error: {outlier_improvement} ({outlier_improvement/len(outlier_errors)*100:.1f}%)")
            print(f"   • Average outlier error: {statistics.mean(outlier_errors):.1f}%")
            print()
        
        # Performance assessment
        if mean_error <= 5:
            performance = "🏆 EXCELLENT - Target achieved!"
        elif mean_error <= 10:
            performance = "✅ GOOD - Close to target"
        elif mean_error <= 20:
            performance = "⚠️ FAIR - Needs improvement"
        else:
            performance = "❌ POOR - Significant improvement needed"
        
        print(f"🎯 OVERALL ASSESSMENT: {performance}")
        
        # Show best and worst predictions
        best_results = sorted(self.validation_results, key=lambda x: x['error_percent'])[:5]
        worst_results = sorted(self.validation_results, key=lambda x: x['error_percent'], reverse=True)[:5]
        
        print("\n🏆 BEST PREDICTIONS:")
        for i, result in enumerate(best_results, 1):
            events_str = ", ".join(result['events']) if result['events'] else "No events"
            outlier_mark = " (Former outlier!)" if result['is_known_outlier'] else ""
            print(f"   {i}. {result['date']} ({result['day_of_week'][:3].upper()}): "
                  f"{result['error_percent']:.1f}% error - {events_str}{outlier_mark}")
        
        print("\n⚠️ REMAINING CHALLENGES:")
        for i, result in enumerate(worst_results, 1):
            events_str = ", ".join(result['events']) if result['events'] else "No events"
            holiday_info = f" (Holiday: {result['holiday_type']}, {result['holiday_adjustment']:.1f}x)"
            print(f"   {i}. {result['date']} ({result['day_of_week'][:3].upper()}): "
                  f"{result['error_percent']:.1f}% error - {events_str}{holiday_info}")
        
        return {
            'mean_error': mean_error,
            'median_error': median_error,
            'std_error': std_error,
            'excellent_count': excellent,
            'good_count': good,
            'fair_count': fair,
            'poor_count': poor,
            'total_tests': len(errors),
            'target_achieved': mean_error <= 5,
            'outlier_improvement': outlier_improvement,
            'outlier_count': len(outlier_errors)
        }
    
    def save_enhanced_validation_results(self, filename=None):
        """Save detailed enhanced validation results"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Reports/Enhanced_Model_Validation_{timestamp}.json"
        
        results = {
            'validation_info': {
                'model_version': '5.0 Comprehensive + Holiday Handler',
                'validation_date': datetime.now().isoformat(),
                'total_tests': len(self.validation_results),
                'target_accuracy': '2-5%'
            },
            'summary_statistics': {
                'mean_error': statistics.mean([r['error_percent'] for r in self.validation_results]),
                'median_error': statistics.median([r['error_percent'] for r in self.validation_results]),
                'std_error': statistics.stdev([r['error_percent'] for r in self.validation_results]) if len(self.validation_results) > 1 else 0
            },
            'detailed_results': self.validation_results
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Enhanced validation results saved: {filename}")
        return filename

def main():
    """Main enhanced validation function"""
    validator = EnhancedModelValidator()
    
    # Run enhanced validation with focus on outliers
    print("🚀 Starting enhanced model validation...")
    print("Focus: Previous outliers + comprehensive accuracy test")
    print()
    
    # Test enhanced system
    results = validator.run_enhanced_validation(num_tests=50, focus_on_outliers=True)
    
    # Save results
    validator.save_enhanced_validation_results()
    
    print("\n🎯 ENHANCED VALIDATION COMPLETE")
    print("=" * 60)
    
    if results['target_achieved']:
        print("🏆 SUCCESS: Target accuracy of 2-5% achieved!")
    else:
        print(f"⚠️  Progress made! Current accuracy: {results['mean_error']:.1f}%")
        print(f"   Outliers improved: {results['outlier_improvement']}/{results['outlier_count']}")
        print("   Continue refinements for full target achievement.")
    
    return results

if __name__ == "__main__":
    results = main()

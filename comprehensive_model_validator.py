#!/usr/bin/env python3
"""
COMPREHENSIVE MODEL VALIDATOR
=============================

Validates the Comprehensive Forecasting Engine v5.0 against historical data
to measure accuracy and compare with previous models.

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
from robust_csv_reader import RobustCSVReader

class ComprehensiveModelValidator:
    """Validates comprehensive forecasting model accuracy"""
    
    def __init__(self):
        self.engine = ComprehensiveForecastingEngine()
        self.csv_reader = RobustCSVReader()
        self.validation_results = []
        
        print("🎯 COMPREHENSIVE MODEL VALIDATOR")
        print("=" * 60)
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
    
    def run_comprehensive_validation(self, num_tests=50, specific_years=None):
        """Run comprehensive validation tests"""
        print(f"🔬 Running {num_tests} comprehensive validation tests...")
        
        # Build the comprehensive model first
        print("🔧 Building comprehensive model...")
        self.engine.build_comprehensive_model()
        
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
                
                # Skip COVID years and filter by specific years if requested
                if year not in [2020, 2021]:
                    if specific_years is None or year in specific_years:
                        valid_records.append({
                            'date': date_str,
                            'year': year,
                            'day_of_week': day_of_week,
                            'actual_revenue': float(record.get('total_revenue', 0)),
                            'notes': record.get('notes', '')
                        })
        
        print(f"📊 Found {len(valid_records)} valid historical records")
        
        # Randomly sample records for testing
        test_records = random.sample(valid_records, min(num_tests, len(valid_records)))
        
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
            prediction = self.engine.predict_revenue(date, day_of_week, events, weather)
            predicted_revenue = prediction['predicted_revenue']
            
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
                'prediction_breakdown': prediction['breakdown']
            }
            self.validation_results.append(result)
            
            # Progress indicator
            status = "✅" if error_pct <= 5 else "⚠️" if error_pct <= 15 else "❌"
            print(f"[{i}/{num_tests}] {date} ({day_of_week[:3].upper()}): {status} "
                  f"Actual: ${actual_revenue:,.0f}, Predicted: ${predicted_revenue:,.0f}, "
                  f"Error: {error_pct:.1f}%")
        
        # Calculate overall statistics
        mean_error = statistics.mean(errors)
        median_error = statistics.median(errors)
        std_error = statistics.stdev(errors) if len(errors) > 1 else 0
        
        # Categorize results
        excellent = len([e for e in errors if e <= 5])
        good = len([e for e in errors if 5 < e <= 15])
        fair = len([e for e in errors if 15 < e <= 30])
        poor = len([e for e in errors if e > 30])
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE MODEL VALIDATION RESULTS")
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
            print(f"   {i}. {result['date']} ({result['day_of_week'][:3].upper()}): "
                  f"{result['error_percent']:.1f}% error - {events_str}")
        
        print("\n⚠️ WORST PREDICTIONS:")
        for i, result in enumerate(worst_results, 1):
            events_str = ", ".join(result['events']) if result['events'] else "No events"
            print(f"   {i}. {result['date']} ({result['day_of_week'][:3].upper()}): "
                  f"{result['error_percent']:.1f}% error - {events_str}")
        
        return {
            'mean_error': mean_error,
            'median_error': median_error,
            'std_error': std_error,
            'excellent_count': excellent,
            'good_count': good,
            'fair_count': fair,
            'poor_count': poor,
            'total_tests': len(errors),
            'target_achieved': mean_error <= 5
        }
    
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
    
    def save_validation_results(self, filename=None):
        """Save detailed validation results"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Reports/Comprehensive_Model_Validation_{timestamp}.json"
        
        results = {
            'validation_info': {
                'model_version': '5.0 Comprehensive',
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
        
        print(f"💾 Validation results saved: {filename}")
        return filename

def main():
    """Main validation function"""
    validator = ComprehensiveModelValidator()
    
    # Run comprehensive validation
    print("🚀 Starting comprehensive model validation...")
    print("Testing against historical data from 2017-2025 (excluding COVID years)")
    print()
    
    # Test on mixed years
    results = validator.run_comprehensive_validation(num_tests=50)
    
    # Save results
    validator.save_validation_results()
    
    print("\n🎯 VALIDATION COMPLETE")
    print("=" * 60)
    
    if results['target_achieved']:
        print("🏆 SUCCESS: Target accuracy of 2-5% achieved!")
    else:
        print(f"⚠️  Target not yet achieved. Current accuracy: {results['mean_error']:.1f}%")
        print("   Consider further model refinements.")
    
    return results

if __name__ == "__main__":
    results = main()

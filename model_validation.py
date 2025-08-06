#!/usr/bin/env python3
"""
Model Validation Script
Predict 50 randomly chosen historic data points and compare to actuals
"""

import random
import csv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics
from run_forecast import EnhancedForecaster

class ModelValidator:
    """Validate forecast model against historical data"""
    
    def __init__(self):
        self.forecaster = EnhancedForecaster()
        self.historical_data = self.load_historical_data()
        
    def load_historical_data(self):
        """Load historical data for validation"""
        print("📊 Loading historical data for validation...")
        
        # Use the robust CSV reader from the forecaster
        normalized_data = self.forecaster.csv_reader.read_csv_robust()
        
        if not normalized_data:
            print("⚠️ No historical data loaded")
            return []
        
        # Convert to validation format
        historical_data = []
        for record in normalized_data:
            # Skip records with missing or invalid data (be more lenient)
            if record.get('total_revenue', 0) > 1000 and record.get('date_str'):  # At least $1000 revenue
                historical_data.append({
                    'date': record['date_str'],
                    'day_of_week': record['day_of_week'],
                    'actual_revenue': record['total_revenue'],
                    'garages': {
                        'Grant Park North': record.get('gpn_revenue', 0),
                        'Grant Park South': record.get('gps_revenue', 0),
                        'Millennium': record.get('millennium_revenue', 0),
                        'Lakeside': record.get('lakeside_revenue', 0),
                        'Online': record.get('online_revenue', 0)
                    }
                })
        
        # Debug: Show sample of loaded data
        if historical_data:
            print(f"📊 Sample historical records:")
            for i, record in enumerate(historical_data[:3]):
                print(f"   {i+1}. {record['date']} ({record['day_of_week']}): ${record['actual_revenue']:,.0f}")
            print(f"   ... and {len(historical_data)-3} more records")
        
        print(f"✅ Loaded {len(historical_data)} historical records for validation")
        return historical_data
    
    def load_historical_events(self, target_date):
        """Load events from appropriate historical calendar (2023 or 2024)"""
        year = target_date[:4]
        
        if year == '2024':
            calendar_file = 'MG Event Calendar 2024.csv'
        elif year == '2023':
            calendar_file = 'MG Event Calendar 2023.csv'
        else:
            # For other years, use current calendar as fallback
            return self.forecaster.load_events_from_csv()
        
        print(f"📁 Loading historical events from: {calendar_file}")
        
        try:
            import csv
            events_data = {}
            
            with open(calendar_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    start_date = row.get('Start Date', '')
                    event_name = row.get('Event', '')
                    tier = row.get('Tier', 'Tier 3')
                    
                    if not start_date or not event_name:
                        continue
                    
                    # Parse date format (e.g., "Mon, Jan 1" -> "2024-01-01")
                    try:
                        # Extract month and day from "Mon, Jan 1" format
                        date_parts = start_date.split(', ')
                        if len(date_parts) >= 2:
                            month_day = date_parts[1]  # "Jan 1"
                            month_name, day = month_day.split(' ')
                            
                            # Convert month name to number
                            month_map = {
                                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                            }
                            
                            month_num = month_map.get(month_name, '01')
                            day_num = day.zfill(2)
                            
                            # Format as YYYY-MM-DD
                            event_date = f"{year}-{month_num}-{day_num}"
                            
                            # Determine multiplier based on tier
                            multiplier = {
                                'Tier 1': 2.5,  # Major events like Lollapalooza
                                'Tier 2': 1.8,  # Large events
                                'Tier 3': 1.3,  # Medium events
                                'Tier 4': 1.0   # Minor/holidays
                            }.get(tier, 1.3)
                            
                            if event_date not in events_data:
                                events_data[event_date] = []
                            
                            events_data[event_date].append({
                                'name': event_name,
                                'multiplier': multiplier,
                                'tier': tier
                            })
                            
                    except Exception as e:
                        continue
            
            print(f"📊 Loaded {len(events_data)} event dates from {calendar_file}")
            return events_data
            
        except Exception as e:
            print(f"⚠️ Error loading {calendar_file}: {e}")
            return self.forecaster.load_events_from_csv()
    
    def select_random_validation_dates(self, count=50):
        """Select random dates ensuring mix of weekends and weekdays"""
        # Filter to 2023 data for analysis
        data_2023 = [d for d in self.historical_data if d['date'].startswith('2023')]
        print(f"📅 Filtering to 2023 data: {len(data_2023)} records available")
        
        if len(data_2023) < count:
            print(f"⚠️ Only {len(data_2023)} 2023 records available, using all")
            return data_2023
        
        # Separate weekends and weekdays (handle different day formats)
        weekends = [d for d in data_2023 if d['day_of_week'] in ['Saturday', 'Sunday', 'SAT', 'SUN']]
        weekdays = [d for d in data_2023 if d['day_of_week'] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'MON', 'TUE', 'WED', 'THU', 'FRI']]
        
        # Debug: Show day distribution
        day_counts = {}
        for d in data_2023:
            day = d['day_of_week']
            day_counts[day] = day_counts.get(day, 0) + 1
        print(f"📊 2023 Day distribution: {day_counts}")
        print(f"📊 Found {len(weekends)} weekends, {len(weekdays)} weekdays")
        
        # Aim for 30% weekends, 70% weekdays (realistic mix)
        weekend_count = min(int(count * 0.3), len(weekends))
        weekday_count = min(count - weekend_count, len(weekdays))
        
        # Randomly select
        selected_weekends = random.sample(weekends, weekend_count)
        selected_weekdays = random.sample(weekdays, weekday_count)
        
        validation_dates = selected_weekends + selected_weekdays
        random.shuffle(validation_dates)  # Randomize order
        
        print(f"📅 Selected {len(validation_dates)} dates for validation:")
        print(f"   • Weekends: {weekend_count}")
        print(f"   • Weekdays: {weekday_count}")
        
        return validation_dates
    
    def predict_single_day(self, target_date, day_of_week):
        """Predict revenue for a single historical day"""
        try:
            # Create a mock forecast for just this day
            forecast_date = datetime.strptime(target_date, '%Y-%m-%d')
            
            # Convert abbreviated day names to full names
            day_mapping = {
                'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 
                'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
            }
            full_day_name = day_mapping.get(day_of_week, day_of_week)
            
            # Get base revenue for this day of week
            base_revenue = self.forecaster.base_daily_revenue[full_day_name]
            
            # Get events for this date from appropriate historical calendar
            events_data = self.load_historical_events(target_date)
            day_events = events_data.get(target_date, [])
            
            # Calculate event multiplier
            event_multiplier = 1.0
            if day_events:
                event_multiplier = max([event['multiplier'] for event in day_events])
            
            # Weather multiplier (use default since historical weather not available)
            weather_multiplier = 1.0
            
            # Calculate predicted revenue
            predicted_revenue = base_revenue * event_multiplier * weather_multiplier
            
            # Calculate garage distribution
            predicted_garages = {}
            for garage, percentage in self.forecaster.garage_distribution.items():
                predicted_garages[garage] = predicted_revenue * percentage
            
            return {
                'predicted_revenue': predicted_revenue,
                'base_revenue': base_revenue,
                'event_multiplier': event_multiplier,
                'weather_multiplier': weather_multiplier,
                'events': [event['name'] for event in day_events],
                'garages': predicted_garages
            }
            
        except Exception as e:
            print(f"⚠️ Error predicting {target_date}: {e}")
            return None
    
    def run_validation(self, count=50):
        """Run comprehensive model validation"""
        print("🔬 STARTING MODEL VALIDATION")
        print("="*80)
        
        # Select validation dates
        validation_dates = self.select_random_validation_dates(count)
        
        results = []
        successful_predictions = 0
        
        print(f"\n🎯 Predicting {len(validation_dates)} historical data points...")
        print("-"*80)
        
        for i, historical_record in enumerate(validation_dates, 1):
            date = historical_record['date']
            day_of_week = historical_record['day_of_week']
            actual_revenue = historical_record['actual_revenue']
            
            print(f"[{i:2d}/{len(validation_dates)}] {date} ({day_of_week}): ", end="")
            
            # Make prediction
            prediction = self.predict_single_day(date, day_of_week)
            
            if prediction:
                predicted_revenue = prediction['predicted_revenue']
                error = abs(predicted_revenue - actual_revenue)
                error_percentage = (error / actual_revenue) * 100
                
                results.append({
                    'date': date,
                    'day_of_week': day_of_week,
                    'actual_revenue': actual_revenue,
                    'predicted_revenue': predicted_revenue,
                    'error': error,
                    'error_percentage': error_percentage,
                    'events': prediction['events'],
                    'event_multiplier': prediction['event_multiplier']
                })
                
                successful_predictions += 1
                print(f"Actual: ${actual_revenue:,.0f}, Predicted: ${predicted_revenue:,.0f}, Error: {error_percentage:.1f}%")
            else:
                print("FAILED")
        
        print(f"\n✅ Successfully predicted {successful_predictions}/{len(validation_dates)} dates")
        
        # Analyze results
        self.analyze_validation_results(results)
        
        # Save detailed results
        self.save_validation_results(results)
        
        return results
    
    def analyze_validation_results(self, results):
        """Analyze and report validation results"""
        if not results:
            print("❌ No successful predictions to analyze")
            return
        
        print("\n📊 VALIDATION RESULTS ANALYSIS")
        print("="*80)
        
        # Overall statistics
        error_percentages = [r['error_percentage'] for r in results]
        mean_error = statistics.mean(error_percentages)
        median_error = statistics.median(error_percentages)
        std_error = statistics.stdev(error_percentages) if len(error_percentages) > 1 else 0
        
        print(f"\n🎯 OVERALL ACCURACY:")
        print(f"   • Mean Error:     {mean_error:.1f}%")
        print(f"   • Median Error:   {median_error:.1f}%")
        print(f"   • Std Deviation:  {std_error:.1f}%")
        print(f"   • Best Prediction: {min(error_percentages):.1f}% error")
        print(f"   • Worst Prediction: {max(error_percentages):.1f}% error")
        
        # Accuracy buckets
        excellent = len([r for r in results if r['error_percentage'] <= 5])
        good = len([r for r in results if 5 < r['error_percentage'] <= 15])
        fair = len([r for r in results if 15 < r['error_percentage'] <= 30])
        poor = len([r for r in results if r['error_percentage'] > 30])
        
        print(f"\n📈 ACCURACY DISTRIBUTION:")
        print(f"   • Excellent (≤5% error):   {excellent:2d} predictions ({excellent/len(results)*100:.1f}%)")
        print(f"   • Good (5-15% error):      {good:2d} predictions ({good/len(results)*100:.1f}%)")
        print(f"   • Fair (15-30% error):     {fair:2d} predictions ({fair/len(results)*100:.1f}%)")
        print(f"   • Poor (>30% error):       {poor:2d} predictions ({poor/len(results)*100:.1f}%)")
        
        # Weekend vs Weekday analysis
        weekend_results = [r for r in results if r['day_of_week'] in ['Saturday', 'Sunday']]
        weekday_results = [r for r in results if r['day_of_week'] not in ['Saturday', 'Sunday']]
        
        if weekend_results and weekday_results:
            weekend_error = statistics.mean([r['error_percentage'] for r in weekend_results])
            weekday_error = statistics.mean([r['error_percentage'] for r in weekday_results])
            
            print(f"\n📅 WEEKEND vs WEEKDAY ACCURACY:")
            print(f"   • Weekend Error:  {weekend_error:.1f}% (n={len(weekend_results)})")
            print(f"   • Weekday Error:  {weekday_error:.1f}% (n={len(weekday_results)})")
        
        # Event vs Non-event analysis
        event_results = [r for r in results if r['events']]
        no_event_results = [r for r in results if not r['events']]
        
        if event_results and no_event_results:
            event_error = statistics.mean([r['error_percentage'] for r in event_results])
            no_event_error = statistics.mean([r['error_percentage'] for r in no_event_results])
            
            print(f"\n🎪 EVENT vs NON-EVENT ACCURACY:")
            print(f"   • Event Days Error:     {event_error:.1f}% (n={len(event_results)})")
            print(f"   • Non-Event Days Error: {no_event_error:.1f}% (n={len(no_event_results)})")
        
        # Best and worst predictions
        best_predictions = sorted(results, key=lambda x: x['error_percentage'])[:5]
        worst_predictions = sorted(results, key=lambda x: x['error_percentage'], reverse=True)[:5]
        
        print(f"\n🏆 BEST PREDICTIONS:")
        for i, r in enumerate(best_predictions, 1):
            events_str = ', '.join(r['events']) if r['events'] else 'No events'
            print(f"   {i}. {r['date']} ({r['day_of_week']}): {r['error_percentage']:.1f}% error - {events_str}")
        
        print(f"\n⚠️  WORST PREDICTIONS:")
        for i, r in enumerate(worst_predictions, 1):
            events_str = ', '.join(r['events']) if r['events'] else 'No events'
            print(f"   {i}. {r['date']} ({r['day_of_week']}): {r['error_percentage']:.1f}% error - {events_str}")
        
        # Model performance assessment
        print(f"\n🎯 MODEL PERFORMANCE ASSESSMENT:")
        if mean_error <= 10:
            print("   ✅ EXCELLENT - Model is highly accurate for business forecasting")
        elif mean_error <= 20:
            print("   ✅ GOOD - Model is suitable for business forecasting with some variance")
        elif mean_error <= 35:
            print("   ⚠️  FAIR - Model provides useful directional guidance but needs improvement")
        else:
            print("   ❌ POOR - Model needs significant improvement before business use")
    
    def save_validation_results(self, results):
        """Save detailed validation results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Reports/Model_Validation_Results_{timestamp}.json"
        
        validation_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_predictions': len(results),
            'mean_error_percentage': statistics.mean([r['error_percentage'] for r in results]) if results else 0,
            'median_error_percentage': statistics.median([r['error_percentage'] for r in results]) if results else 0,
            'detailed_results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(validation_summary, f, indent=2, default=str)
        
        print(f"\n💾 Detailed validation results saved: {filename}")

if __name__ == "__main__":
    validator = ModelValidator()
    results = validator.run_validation(count=50)

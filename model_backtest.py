#!/usr/bin/env python3
"""
Model Backtesting Script
Test the enhanced forecasting model against actual historical data
"""

from datetime import datetime, timedelta
import csv
import json

class ModelBacktester:
    def __init__(self):
        self.base_daily_revenue = {
            'Monday': 48361,
            'Tuesday': 45935,
            'Wednesday': 47514,
            'Thursday': 53478,
            'Friday': 54933,
            'Saturday': 74934,
            'Sunday': 71348
        }
        
        # Enhanced event multipliers from our analysis
        self.event_multipliers = {
            'mega_festival': 1.67,
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
        
        # Day-specific Lollapalooza multipliers
        self.lollapalooza_day_multipliers = {
            'Thursday': 2.49,
            'Friday': 2.12,
            'Saturday': 1.80,
            'Sunday': 2.24
        }
        
        # Load historical data
        self.historical_data = self.load_historical_data()
        self.events_data = self.load_events()
        
    def load_historical_data(self):
        """Load historical booking data"""
        historical_data = {}
        try:
            with open('HIstoric Booking Data.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_str = row.get('Date', '').strip()
                    if date_str:
                        try:
                            # Try different date formats - based on the historical data format
                            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y']:
                                try:
                                    date_obj = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # If standard formats fail, try to handle it manually
                                try:
                                    # Handle formats like "2025-1-15" or "1/15/2025"
                                    if '-' in date_str:
                                        parts = date_str.split('-')
                                        if len(parts) == 3:
                                            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                                            date_obj = datetime(year, month, day)
                                    elif '/' in date_str:
                                        parts = date_str.split('/')
                                        if len(parts) == 3:
                                            # Assume M/D/Y format
                                            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                                            if year < 100:  # Handle 2-digit years
                                                year += 2000
                                            date_obj = datetime(year, month, day)
                                    else:
                                        continue
                                except (ValueError, IndexError):
                                    continue
                            
                            date_key = date_obj.strftime('%Y-%m-%d')
                            revenue = float(row.get('Total Revenue', 0) or 0)
                            historical_data[date_key] = revenue
                        except (ValueError, TypeError):
                            continue
            print(f"Loaded {len(historical_data)} historical data points")
            return historical_data
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return {}
    
    def load_events(self):
        """Load events from calendar"""
        events_by_date = {}
        try:
            with open('MG Event Calendar 2025.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_str = row.get('Start Date', '').strip()
                    if date_str:
                        try:
                            # Parse date in M/D/YY format
                            date_obj = datetime.strptime(date_str, '%m/%d/%y')
                            date_key = date_obj.strftime('%Y-%m-%d')
                            
                            if date_key not in events_by_date:
                                events_by_date[date_key] = []
                            
                            event_name = row.get('Event', '').strip()
                            if event_name and event_name != '-':
                                category = self.categorize_event(event_name)
                                events_by_date[date_key].append({
                                    'name': event_name,
                                    'category': category,
                                    'multiplier': self.get_event_multiplier(event_name, category, date_obj.strftime('%A'))
                                })
                        except ValueError:
                            continue
        except FileNotFoundError:
            print("Event calendar not found - using limited event data")
        
        return events_by_date
    
    def categorize_event(self, event_name):
        """Categorize events based on name"""
        event_lower = event_name.lower()
        
        if 'lollapalooza' in event_lower:
            return 'mega_festival'
        elif any(sport in event_lower for sport in ['bears', 'bulls', 'blackhawks', 'cubs', 'sox', 'fire']):
            return 'sports'
        elif any(term in event_lower for term in ['festival', 'fest']):
            return 'festival'
        elif any(term in event_lower for term in ['broadway', 'symphony', 'opera', 'ballet']):
            return 'major_performance'
        elif any(term in event_lower for term in ['concert', 'music', 'performance', 'show']):
            return 'performance'
        elif any(term in event_lower for term in ['holiday', 'christmas', 'thanksgiving', 'july 4']):
            return 'holiday'
        else:
            return 'other'
    
    def get_event_multiplier(self, event_name, category, day_of_week):
        """Get the appropriate multiplier for an event"""
        event_lower = event_name.lower()
        
        # Check for Lollapalooza with day-specific multipliers
        if 'lollapalooza' in event_lower:
            return self.lollapalooza_day_multipliers.get(day_of_week, self.event_multipliers['mega_festival'])
        
        # Use standard category multipliers for other events
        return self.event_multipliers.get(category, 1.0)
    
    def get_weather_adjustment(self, temp_high=75, precipitation=0, condition='clear'):
        """Calculate weather adjustment multiplier (simplified for backtesting)"""
        # Temperature adjustment (optimal range 70-80°F)
        if 70 <= temp_high <= 80:
            temp_adj = 1.0
        elif temp_high < 50:
            temp_adj = 0.85
        elif temp_high > 95:
            temp_adj = 0.90
        elif temp_high < 70:
            temp_adj = 0.95
        else:  # 80-95°F
            temp_adj = 0.97
        
        # Precipitation adjustment
        if precipitation > 0.5:
            precip_adj = 0.85
        elif precipitation > 0.1:
            precip_adj = 0.95
        else:
            precip_adj = 1.0
        
        # Condition adjustment
        condition_lower = condition.lower()
        if any(bad in condition_lower for bad in ['storm', 'heavy rain', 'snow']):
            condition_adj = 0.80
        elif any(poor in condition_lower for poor in ['rain', 'drizzle', 'overcast']):
            condition_adj = 0.90
        else:
            condition_adj = 1.0
        
        return temp_adj * precip_adj * condition_adj
    
    def generate_forecast_for_date(self, start_date, days=7):
        """Generate a 7-day forecast starting from a specific date"""
        forecast_data = []
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            date_str = forecast_date.strftime('%Y-%m-%d')
            day_name = forecast_date.strftime('%A')
            
            # Base revenue for day of week
            base_revenue = self.base_daily_revenue[day_name]
            
            # Get events for this date
            day_events = self.events_data.get(date_str, [])
            event_multiplier = 1.0
            event_names = []
            
            if day_events:
                event_multiplier = max([event['multiplier'] for event in day_events])
                event_names = [event['name'] for event in day_events]
            
            # Simplified weather adjustment (using seasonal averages)
            month = forecast_date.month
            if month in [1, 2, 12]:  # Winter
                weather_mult = self.get_weather_adjustment(35, 0.1, 'cold')
            elif month in [3, 4, 5]:  # Spring
                weather_mult = self.get_weather_adjustment(65, 0.2, 'mild')
            elif month in [6, 7, 8]:  # Summer
                weather_mult = self.get_weather_adjustment(80, 0.1, 'clear')
            else:  # Fall
                weather_mult = self.get_weather_adjustment(70, 0.15, 'partly cloudy')
            
            # Calculate final revenue
            final_revenue = base_revenue * event_multiplier * weather_mult
            
            forecast_data.append({
                'date': date_str,
                'day': day_name,
                'base_revenue': base_revenue,
                'event_multiplier': event_multiplier,
                'weather_multiplier': weather_mult,
                'predicted_revenue': final_revenue,
                'events': event_names
            })
        
        return forecast_data
    
    def get_actual_revenue(self, date_str):
        """Get actual revenue for a specific date"""
        return self.historical_data.get(date_str)
    
    def run_backtest(self):
        """Run backtest on 6 arbitrary dates from Q1 and Q2 2025"""
        
        # Select 6 test dates from Q1 and Q2 2025
        test_dates = [
            datetime(2025, 1, 15),  # Mid-January
            datetime(2025, 2, 20),  # Late February
            datetime(2025, 3, 10),  # Early March
            datetime(2025, 4, 25),  # Late April
            datetime(2025, 5, 15),  # Mid-May
            datetime(2025, 6, 30),  # End of June
        ]
        
        print("🧪 MODEL BACKTESTING RESULTS")
        print("=" * 80)
        print(f"Testing enhanced forecasting model with day-specific Lollapalooza multipliers")
        print(f"Historical data contains {len(self.historical_data)} records")
        print(f"Event data contains {len(self.events_data)} event dates")
        print()
        
        all_results = []
        
        for i, test_date in enumerate(test_dates, 1):
            print(f"📊 TEST {i}: {test_date.strftime('%B %d, %Y')} ({test_date.strftime('%A')})")
            print("-" * 60)
            
            # Generate 7-day forecast
            forecast = self.generate_forecast_for_date(test_date, 7)
            
            test_results = {
                'test_date': test_date.strftime('%Y-%m-%d'),
                'forecast_data': [],
                'total_predicted': 0,
                'total_actual': 0,
                'days_with_actuals': 0,
                'accuracy_metrics': {}
            }
            
            for day_forecast in forecast:
                actual_revenue = self.get_actual_revenue(day_forecast['date'])
                
                day_result = {
                    'date': day_forecast['date'],
                    'day': day_forecast['day'],
                    'predicted': day_forecast['predicted_revenue'],
                    'actual': actual_revenue,
                    'events': day_forecast['events'],
                    'event_mult': day_forecast['event_multiplier'],
                    'weather_mult': day_forecast['weather_multiplier']
                }
                
                test_results['forecast_data'].append(day_result)
                test_results['total_predicted'] += day_forecast['predicted_revenue']
                
                if actual_revenue is not None:
                    test_results['total_actual'] += actual_revenue
                    test_results['days_with_actuals'] += 1
                    
                    error = abs(day_forecast['predicted_revenue'] - actual_revenue)
                    error_pct = (error / actual_revenue) * 100 if actual_revenue > 0 else 0
                    
                    print(f"  {day_forecast['date']} ({day_forecast['day'][:3]}): "
                          f"Predicted ${day_forecast['predicted_revenue']:,.0f} | "
                          f"Actual ${actual_revenue:,.0f} | "
                          f"Error: {error_pct:.1f}%")
                    
                    if day_forecast['events']:
                        print(f"    Events: {', '.join(day_forecast['events'])} (Mult: {day_forecast['event_multiplier']:.2f}x)")
                else:
                    print(f"  {day_forecast['date']} ({day_forecast['day'][:3]}): "
                          f"Predicted ${day_forecast['predicted_revenue']:,.0f} | "
                          f"Actual: No data available")
            
            # Calculate accuracy metrics
            if test_results['days_with_actuals'] > 0:
                avg_predicted = test_results['total_predicted'] / 7
                avg_actual = test_results['total_actual'] / test_results['days_with_actuals']
                
                total_error = abs(test_results['total_predicted'] - test_results['total_actual'])
                total_error_pct = (total_error / test_results['total_actual']) * 100 if test_results['total_actual'] > 0 else 0
                
                test_results['accuracy_metrics'] = {
                    'total_error_pct': total_error_pct,
                    'avg_predicted': avg_predicted,
                    'avg_actual': avg_actual
                }
                
                print(f"\n  📈 SUMMARY:")
                print(f"    Total Predicted: ${test_results['total_predicted']:,.0f}")
                print(f"    Total Actual: ${test_results['total_actual']:,.0f}")
                print(f"    Total Error: {total_error_pct:.1f}%")
                print(f"    Days with data: {test_results['days_with_actuals']}/7")
            else:
                print(f"\n  ⚠️  No actual data available for this period")
            
            all_results.append(test_results)
            print()
        
        # Overall summary
        self.print_overall_summary(all_results)
        
        return all_results
    
    def print_overall_summary(self, all_results):
        """Print overall backtesting summary"""
        print("🎯 OVERALL BACKTESTING SUMMARY")
        print("=" * 80)
        
        total_predicted = sum(r['total_predicted'] for r in all_results)
        total_actual = sum(r['total_actual'] for r in all_results if r['total_actual'] > 0)
        total_days_with_data = sum(r['days_with_actuals'] for r in all_results)
        
        if total_days_with_data > 0:
            overall_error = abs(total_predicted - total_actual)
            overall_error_pct = (overall_error / total_actual) * 100 if total_actual > 0 else 0
            
            print(f"Total Days Tested: {len(all_results) * 7}")
            print(f"Days with Actual Data: {total_days_with_data}")
            print(f"Data Coverage: {(total_days_with_data / (len(all_results) * 7)) * 100:.1f}%")
            print()
            print(f"Total Predicted Revenue: ${total_predicted:,.0f}")
            print(f"Total Actual Revenue: ${total_actual:,.0f}")
            print(f"Overall Model Error: {overall_error_pct:.1f}%")
            print()
            
            # Error analysis
            valid_results = [r for r in all_results if r['days_with_actuals'] > 0]
            if valid_results:
                errors = [r['accuracy_metrics']['total_error_pct'] for r in valid_results if 'accuracy_metrics' in r]
                if errors:
                    avg_error = sum(errors) / len(errors)
                    min_error = min(errors)
                    max_error = max(errors)
                    
                    print(f"Error Statistics:")
                    print(f"  Average Error: {avg_error:.1f}%")
                    print(f"  Best Performance: {min_error:.1f}%")
                    print(f"  Worst Performance: {max_error:.1f}%")
                    
                    if avg_error < 15:
                        print(f"✅ Model Performance: EXCELLENT (< 15% error)")
                    elif avg_error < 25:
                        print(f"✅ Model Performance: GOOD (< 25% error)")
                    elif avg_error < 35:
                        print(f"⚠️  Model Performance: FAIR (< 35% error)")
                    else:
                        print(f"❌ Model Performance: NEEDS IMPROVEMENT (> 35% error)")
        else:
            print("❌ No actual data available for comparison")
        
        print()
        print("📝 Notes:")
        print("- Weather adjustments use seasonal averages (historical weather data not available)")
        print("- Day-specific Lollapalooza multipliers applied when detected")
        print("- Model includes enhanced event categorization and refined multipliers")

if __name__ == "__main__":
    backtester = ModelBacktester()
    results = backtester.run_backtest()

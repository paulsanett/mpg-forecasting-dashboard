#!/usr/bin/env python3
"""
CONFIDENCE ANALYZER
Calculates prediction confidence for each forecast day
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from datetime import datetime
import statistics
from collections import defaultdict

class ConfidenceAnalyzer:
    def __init__(self):
        self.reader = RobustCSVReader()
        self.confidence_data = {}
        self.load_confidence_patterns()
    
    def load_confidence_patterns(self):
        """Analyze historical data to determine confidence patterns"""
        data = self.reader.read_csv_robust()
        
        # Filter for recent data
        cutoff_date = datetime(2024, 8, 6)
        analysis_data = []
        
        for record in data:
            if (record.get('date') and record.get('total_revenue', 0) > 0):
                try:
                    date_str = str(record.get('date', ''))
                    date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    
                    if date_obj >= cutoff_date:
                        analysis_data.append({
                            'date': date_obj,
                            'day_of_week': record.get('day_of_week', '').strip(),
                            'total_revenue': record.get('total_revenue', 0),
                            'month': date_obj.month
                        })
                except:
                    continue
        
        # Analyze by day of week
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        for day_abbr, day_name in day_mapping.items():
            day_data = [d for d in analysis_data if d['day_of_week'].upper() == day_abbr]
            
            if len(day_data) >= 10:
                revenues = [d['total_revenue'] for d in day_data]
                
                # Calculate variability metrics
                mean_rev = statistics.mean(revenues)
                median_rev = statistics.median(revenues)
                std_dev = statistics.stdev(revenues) if len(revenues) > 1 else 0
                cv = (std_dev / mean_rev) * 100 if mean_rev > 0 else 100
                
                # Calculate confidence ranges
                within_5pct = len([r for r in revenues if abs(r - median_rev) / median_rev <= 0.05])
                within_10pct = len([r for r in revenues if abs(r - median_rev) / median_rev <= 0.10])
                within_15pct = len([r for r in revenues if abs(r - median_rev) / median_rev <= 0.15])
                
                # Determine confidence level
                pct_within_5 = within_5pct / len(revenues) * 100
                pct_within_10 = within_10pct / len(revenues) * 100
                pct_within_15 = within_15pct / len(revenues) * 100
                
                if cv < 12 and pct_within_10 >= 60:
                    confidence_level = 'HIGH'
                    expected_accuracy = '5-10%'
                    confidence_score = 85
                elif cv < 20 and pct_within_15 >= 50:
                    confidence_level = 'MEDIUM'
                    expected_accuracy = '10-20%'
                    confidence_score = 65
                else:
                    confidence_level = 'LOW'
                    expected_accuracy = '15-30%'
                    confidence_score = 40
                
                self.confidence_data[day_name] = {
                    'confidence_level': confidence_level,
                    'expected_accuracy': expected_accuracy,
                    'confidence_score': confidence_score,
                    'coefficient_variation': cv,
                    'within_5pct': pct_within_5,
                    'within_10pct': pct_within_10,
                    'within_15pct': pct_within_15,
                    'sample_size': len(day_data)
                }
            else:
                # Default for insufficient data
                self.confidence_data[day_name] = {
                    'confidence_level': 'LOW',
                    'expected_accuracy': '20-40%',
                    'confidence_score': 30,
                    'coefficient_variation': 50,
                    'within_5pct': 10,
                    'within_10pct': 25,
                    'within_15pct': 40,
                    'sample_size': len(day_data) if day_data else 0
                }
    
    def get_day_confidence(self, day_name):
        """Get confidence metrics for a specific day"""
        return self.confidence_data.get(day_name, {
            'confidence_level': 'LOW',
            'expected_accuracy': '20-40%',
            'confidence_score': 30,
            'coefficient_variation': 50,
            'within_5pct': 10,
            'within_10pct': 25,
            'within_15pct': 40,
            'sample_size': 0
        })
    
    def get_event_confidence_adjustment(self, is_event_day, event_type=None):
        """Adjust confidence for event days"""
        if not is_event_day:
            return 1.0, "Regular day"
        
        # Handle both string and dict event types
        event_name = ""
        if isinstance(event_type, dict):
            event_name = event_type.get('name', '').lower()
        elif isinstance(event_type, str):
            event_name = event_type.lower()
        
        if event_name and 'lollapalooza' in event_name:
            return 1.2, "Lollapalooza (higher confidence due to consistent patterns)"
        else:
            return 0.8, "Unknown event (lower confidence)"
    
    def analyze_forecast_confidence(self, forecast_data):
        """Add confidence indicators to forecast data"""
        enhanced_forecast = []
        
        for day_forecast in forecast_data:
            day_name = day_forecast.get('day_name', '')
            is_event = len(day_forecast.get('events', [])) > 0
            event_types = day_forecast.get('events', [])
            
            # Get base confidence
            base_confidence = self.get_day_confidence(day_name)
            
            # Adjust for events
            event_multiplier, event_note = self.get_event_confidence_adjustment(
                is_event, 
                event_types[0] if event_types else None
            )
            
            # Calculate final confidence
            final_confidence_score = min(95, int(base_confidence['confidence_score'] * event_multiplier))
            
            # Determine final expected accuracy
            if final_confidence_score >= 80:
                final_accuracy = '5-12%'
                confidence_rating = 'HIGH'
            elif final_confidence_score >= 60:
                final_accuracy = '10-18%'
                confidence_rating = 'MEDIUM'
            else:
                final_accuracy = '15-30%'
                confidence_rating = 'LOW'
            
            # Enhanced forecast with confidence
            enhanced_day = day_forecast.copy()
            enhanced_day.update({
                'confidence_score': final_confidence_score,
                'confidence_level': confidence_rating,
                'expected_accuracy': final_accuracy,
                'prediction_notes': event_note if is_event else f"Based on {base_confidence['sample_size']} historical samples",
                'variability_coefficient': base_confidence['coefficient_variation'],
                'historical_within_10pct': base_confidence['within_10pct']
            })
            
            enhanced_forecast.append(enhanced_day)
        
        return enhanced_forecast
    
    def print_confidence_summary(self):
        """Print summary of confidence analysis"""
        print('📊 FORECAST CONFIDENCE ANALYSIS')
        print('=' * 50)
        print('Day        Confidence  Expected Accuracy  CV%   Samples')
        print('-' * 50)
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            conf = self.confidence_data[day]
            print(f'{day:>9}: {conf["confidence_level"]:>10} {conf["expected_accuracy"]:>15} {conf["coefficient_variation"]:>6.1f}% {conf["sample_size"]:>7}')
        
        print()
        print('💡 CONFIDENCE LEVELS:')
        print('🟢 HIGH: Consistent patterns, 5-12% expected accuracy')
        print('🟡 MEDIUM: Moderate variability, 10-18% expected accuracy')
        print('🔴 LOW: High variability, 15-30% expected accuracy')

def main():
    analyzer = ConfidenceAnalyzer()
    analyzer.print_confidence_summary()
    return analyzer

if __name__ == "__main__":
    main()

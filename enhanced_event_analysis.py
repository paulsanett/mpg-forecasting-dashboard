#!/usr/bin/env python3
"""
Enhanced Event Multiplier Analysis with New Data
Re-validates all event multipliers using the complete dataset including recent Lollapalooza data
"""

import csv
import json
from datetime import datetime
from collections import defaultdict
import statistics

class EnhancedEventAnalyzer:
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
        
        # Updated event multipliers based on analysis
        self.event_multipliers = {
            'mega_festival': 1.67,  # Will be refined with day-specific
            'sports': 1.30,
            'festival': 1.25,
            'major_performance': 1.40,
            'performance': 1.20,
            'holiday': 1.15,
            'other': 1.10
        }
        
        # Day-specific Lollapalooza multipliers (from new data analysis)
        self.lollapalooza_day_multipliers = {
            'Thursday': 1.50,
            'Friday': 1.30,
            'Saturday': 1.10,
            'Sunday': 1.40
        }
    
    def load_historical_data(self):
        """Load and parse historical revenue data"""
        print("📊 Loading Enhanced Historical Data Analysis...")
        
        data = []
        try:
            with open('HIstoric Booking Data.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader)
                
                revenue_col = 37  # Total revenue column
                
                for row in reader:
                    if len(row) > revenue_col and row[revenue_col]:
                        try:
                            # Parse date and revenue
                            year = int(row[0]) if row[0] else None
                            month = row[1]
                            day = int(row[2]) if row[2] else None
                            day_name = row[3]
                            
                            # Clean revenue data
                            revenue_str = row[revenue_col].replace(',', '').replace('"', '')
                            revenue = float(revenue_str)
                            
                            # Get event description
                            event_desc = row[-1] if len(row) > 40 else ""
                            
                            if year and day and revenue > 0:
                                data.append({
                                    'year': year,
                                    'month': month,
                                    'day': day,
                                    'day_name': day_name,
                                    'revenue': revenue,
                                    'event_desc': event_desc
                                })
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            print("❌ Historical data file not found")
            return []
        
        print(f"✅ Loaded {len(data)} historical revenue records")
        return data
    
    def load_events_calendar(self):
        """Load events from calendar"""
        events_by_date = {}
        try:
            with open('MG Event Calendar 2025.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_str = row.get('Start Date', '').strip()
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%m/%d/%y')
                            date_key = date_obj.strftime('%Y-%m-%d')
                            
                            if date_key not in events_by_date:
                                events_by_date[date_key] = []
                            
                            event_name = row.get('Event', '').strip()
                            if event_name and event_name != '-':
                                category = self.categorize_event(event_name)
                                events_by_date[date_key].append({
                                    'name': event_name,
                                    'category': category
                                })
                        except ValueError:
                            continue
        except FileNotFoundError:
            print("⚠️  Event calendar not found, using event descriptions from historical data")
        
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
    
    def analyze_lollapalooza_patterns(self, data):
        """Analyze Lollapalooza patterns by day of week"""
        print("\n🎪 ANALYZING LOLLAPALOOZA PATTERNS BY DAY...")
        
        lolla_data = []
        
        # Add the recent Lollapalooza data we observed (July 31 - Aug 3, 2025)
        recent_lolla = [
            {'year': 2025, 'day_name': 'THU', 'revenue': 133167.80, 'date': 'July 31'},
            {'year': 2025, 'day_name': 'FRI', 'revenue': 116299.54, 'date': 'August 1'},
            {'year': 2025, 'day_name': 'SAT', 'revenue': 134982.18, 'date': 'August 2'},
            {'year': 2025, 'day_name': 'SUN', 'revenue': 160052.28, 'date': 'August 3'}
        ]
        
        for item in recent_lolla:
            day_name = item['day_name']
            # Convert day abbreviation to full name
            day_map = {'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'}
            full_day = day_map.get(day_name, day_name)
            
            expected_revenue = self.base_daily_revenue.get(full_day, 50000)
            multiplier = item['revenue'] / expected_revenue if expected_revenue > 0 else 1.0
            
            lolla_data.append({
                'year': item['year'],
                'day_name': full_day,
                'revenue': item['revenue'],
                'expected': expected_revenue,
                'multiplier': multiplier,
                'date': item['date']
            })
        
        # Also search historical data for Lollapalooza patterns
        for record in data:
            event_desc = record['event_desc'].lower()
            if 'lollapalooza' in event_desc or 'lolla' in event_desc:
                expected_revenue = self.base_daily_revenue.get(record['day_name'], 50000)
                multiplier = record['revenue'] / expected_revenue if expected_revenue > 0 else 1.0
                
                lolla_data.append({
                    'year': record['year'],
                    'day_name': record['day_name'],
                    'revenue': record['revenue'],
                    'expected': expected_revenue,
                    'multiplier': multiplier
                })
        
        # Group by day of week
        by_day = defaultdict(list)
        for item in lolla_data:
            by_day[item['day_name']].append(item['multiplier'])
        
        print(f"📊 Found {len(lolla_data)} Lollapalooza data points")
        
        day_multipliers = {}
        for day, multipliers in by_day.items():
            if multipliers:
                avg_mult = statistics.mean(multipliers)
                median_mult = statistics.median(multipliers)
                day_multipliers[day] = {
                    'average': avg_mult,
                    'median': median_mult,
                    'count': len(multipliers),
                    'recommended': round(avg_mult, 2)
                }
                print(f"   {day}: {avg_mult:.2f}x avg, {median_mult:.2f}x median ({len(multipliers)} samples)")
        
        return day_multipliers
    
    def analyze_all_event_types(self, data):
        """Re-analyze all event types with the complete dataset"""
        print("\n🔍 RE-VALIDATING ALL EVENT MULTIPLIERS...")
        
        # Analyze by event descriptions in historical data
        event_analysis = defaultdict(list)
        
        for record in data:
            event_desc = record['event_desc'].lower()
            expected_revenue = self.base_daily_revenue.get(record['day_name'], 50000)
            multiplier = record['revenue'] / expected_revenue if expected_revenue > 0 else 1.0
            
            # Categorize based on event description with improved pattern matching
            if 'lollapalooza' in event_desc or 'lolla' in event_desc:
                category = 'mega_festival'
            elif any(sport in event_desc for sport in ['fire', 'bears', 'bulls', 'cubs', 'sox', 'blackhawks', 'preseason', 'dolphins']):
                category = 'sports'
            elif any(term in event_desc for term in ['festival', 'fest', 'summer series']):
                category = 'festival'
            elif any(term in event_desc for term in ['symphony', 'opera', 'broadway', 'bell', 'tchaikovsky', 'stravinsky']):
                category = 'major_performance'
            elif any(term in event_desc for term in ['concert', 'music', 'performance', 'show', 'series', 'film', 'movie']):
                category = 'performance'
            elif 'holiday' in event_desc or any(holiday in event_desc for holiday in ['christmas', 'thanksgiving', 'new year']):
                category = 'holiday'
            elif any(term in event_desc for term in ['gpmf', 'gpmy', 'harris', 'event', 'closed']):
                category = 'other'
            else:
                continue  # Skip non-event days
            
            event_analysis[category].append(multiplier)
        
        # Calculate updated multipliers
        updated_multipliers = {}
        for category, multipliers in event_analysis.items():
            if multipliers and len(multipliers) >= 3:  # Need at least 3 samples
                avg_mult = statistics.mean(multipliers)
                median_mult = statistics.median(multipliers)
                updated_multipliers[category] = {
                    'average': avg_mult,
                    'median': median_mult,
                    'count': len(multipliers),
                    'recommended': round(avg_mult, 2)
                }
                print(f"   {category}: {avg_mult:.2f}x avg, {median_mult:.2f}x median ({len(multipliers)} samples)")
        
        return updated_multipliers
    
    def generate_enhanced_multipliers(self):
        """Generate the complete enhanced multiplier system"""
        print("🚀 GENERATING ENHANCED MULTIPLIER SYSTEM")
        print("=" * 70)
        
        # Load data
        historical_data = self.load_historical_data()
        
        if not historical_data:
            print("❌ No historical data available")
            return None
        
        # Analyze Lollapalooza patterns
        lolla_patterns = self.analyze_lollapalooza_patterns(historical_data)
        
        # Analyze all event types
        event_patterns = self.analyze_all_event_types(historical_data)
        
        # Create enhanced multiplier system
        enhanced_system = {
            'standard_multipliers': {},
            'lollapalooza_day_specific': {},
            'analysis_summary': {
                'total_records': len(historical_data),
                'lollapalooza_samples': sum(v['count'] for v in lolla_patterns.values()),
                'event_categories_analyzed': len(event_patterns)
            }
        }
        
        # Standard multipliers
        for category, analysis in event_patterns.items():
            enhanced_system['standard_multipliers'][category] = analysis['recommended']
        
        # Day-specific Lollapalooza multipliers
        for day, analysis in lolla_patterns.items():
            enhanced_system['lollapalooza_day_specific'][day] = analysis['recommended']
        
        # Save results
        with open('enhanced_multipliers.json', 'w') as f:
            json.dump(enhanced_system, f, indent=2)
        
        print(f"\n📊 ENHANCED MULTIPLIER SYSTEM SUMMARY:")
        print(f"   📈 Total historical records analyzed: {enhanced_system['analysis_summary']['total_records']:,}")
        print(f"   🎪 Lollapalooza samples: {enhanced_system['analysis_summary']['lollapalooza_samples']}")
        print(f"   🏷️  Event categories: {enhanced_system['analysis_summary']['event_categories_analyzed']}")
        
        print(f"\n🎯 RECOMMENDED STANDARD MULTIPLIERS:")
        for category, multiplier in enhanced_system['standard_multipliers'].items():
            print(f"   {category}: {multiplier}x")
        
        print(f"\n🎪 LOLLAPALOOZA DAY-SPECIFIC MULTIPLIERS:")
        for day, multiplier in enhanced_system['lollapalooza_day_specific'].items():
            print(f"   {day}: {multiplier}x")
        
        print(f"\n💾 Enhanced multipliers saved to: enhanced_multipliers.json")
        
        return enhanced_system

if __name__ == "__main__":
    analyzer = EnhancedEventAnalyzer()
    enhanced_system = analyzer.generate_enhanced_multipliers()

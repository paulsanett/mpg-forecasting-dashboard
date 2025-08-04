#!/usr/bin/env python3
"""
Historical Lollapalooza Impact Analysis
Analyze actual historical data to determine real Lollapalooza impact on parking revenue
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import re

class LollapaloozaHistoricalAnalyzer:
    def __init__(self):
        self.revenue_data = []
        self.lollapalooza_dates = []
        self.garage_names = ['Grant Park North', 'Grant Park South', 'Millennium', 'Lakeside']
        
    def load_historical_data(self):
        """Load historical revenue data"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🔍 LOLLAPALOOZA HISTORICAL IMPACT ANALYSIS")
        print("=" * 75)
        print("📊 Loading historical data to validate Lollapalooza impact...")
        
        data = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            valid_count = 0
            total_revenue = 0
            
            for row in reader:
                if len(row) < 40:
                    continue
                
                try:
                    # Extract date components
                    year_str = row[0].strip() if len(row) > 0 else ""
                    month_str = row[1].strip() if len(row) > 1 else ""
                    date_str = row[2].strip() if len(row) > 2 else ""
                    
                    if not year_str or not month_str or not date_str:
                        continue
                    
                    # Parse date
                    year = int(year_str)
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    month_lower = month_str.lower()
                    if month_lower in month_map:
                        month = month_map[month_lower]
                    else:
                        month = int(month_str)
                    
                    day = int(date_str)
                    date = datetime(year, month, day)
                    
                    # Get total revenue from main column
                    total_revenue_val = 0
                    if len(row) > 37:
                        total_revenue_str = row[37].strip()
                        if total_revenue_str:
                            clean_total = ""
                            for char in total_revenue_str:
                                if char.isdigit() or char == '.' or char == '-':
                                    clean_total += char
                            
                            if clean_total and clean_total != '-' and clean_total != '.':
                                try:
                                    total_revenue_val = float(clean_total)
                                except:
                                    pass
                    
                    # Get notes column for event detection
                    notes = ""
                    if len(row) > 40:  # Notes are typically in later columns
                        notes = row[40].strip() if row[40] else ""
                    
                    if total_revenue_val > 1000:  # Valid day
                        data.append({
                            'date': date,
                            'total_revenue': total_revenue_val,
                            'year': year,
                            'month': month,
                            'day': day,
                            'day_of_week': date.weekday(),
                            'notes': notes
                        })
                        total_revenue += total_revenue_val
                        valid_count += 1
                
                except:
                    continue
            
            print(f"✅ Historical Data Loaded: {valid_count:,} records")
            print(f"💰 Total Revenue: ${total_revenue:,.2f}")
            print(f"📅 Date Range: {min(d['date'] for d in data).strftime('%Y-%m-%d')} to {max(d['date'] for d in data).strftime('%Y-%m-%d')}")
            
            data.sort(key=lambda x: x['date'])
            self.revenue_data = data
            
            return data
    
    def identify_lollapalooza_dates(self):
        """Identify historical Lollapalooza dates from notes and typical timing"""
        print(f"\n🎪 Identifying Historical Lollapalooza Dates...")
        
        lolla_dates = []
        potential_lolla_dates = []
        
        # Search for Lollapalooza mentions in notes
        for record in self.revenue_data:
            notes_lower = record['notes'].lower()
            if 'lolla' in notes_lower or 'lollapalooza' in notes_lower:
                lolla_dates.append(record)
                print(f"   🔥 Found Lolla mention: {record['date'].strftime('%Y-%m-%d')} - {record['notes'][:100]}...")
        
        # Also look for typical Lollapalooza timing (late July/early August, high revenue days)
        # Lollapalooza typically happens in Grant Park in late July/early August
        for record in self.revenue_data:
            date = record['date']
            # Check if it's late July or early August
            if (date.month == 7 and date.day >= 25) or (date.month == 8 and date.day <= 10):
                # Check if it's a weekend with unusually high revenue
                if date.weekday() in [5, 6]:  # Saturday or Sunday
                    potential_lolla_dates.append(record)
        
        # Sort potential dates by revenue to find the highest revenue weekend days in Lolla season
        potential_lolla_dates.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Direct Lolla mentions: {len(lolla_dates)} days")
        print(f"   High-revenue late July/early August weekends: {len(potential_lolla_dates[:20])} top days")
        
        # Show top revenue days in Lolla season
        print(f"\n🏆 TOP REVENUE DAYS in Lollapalooza Season (Late July/Early August):")
        for i, record in enumerate(potential_lolla_dates[:10]):
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][record['day_of_week']]
            print(f"   {i+1:2d}. {record['date'].strftime('%Y-%m-%d')} ({day_name}): ${record['total_revenue']:,.2f}")
        
        self.lollapalooza_dates = lolla_dates
        return lolla_dates, potential_lolla_dates[:20]
    
    def analyze_lollapalooza_impact(self):
        """Analyze actual Lollapalooza impact vs normal days"""
        print(f"\n📈 ANALYZING ACTUAL LOLLAPALOOZA IMPACT...")
        
        # Get baseline revenue for each day of week
        dow_revenues = defaultdict(list)
        
        for record in self.revenue_data:
            # Exclude potential Lolla dates from baseline calculation
            date = record['date']
            is_potential_lolla = ((date.month == 7 and date.day >= 25) or (date.month == 8 and date.day <= 10))
            
            if not is_potential_lolla:
                dow_revenues[record['day_of_week']].append(record['total_revenue'])
        
        # Calculate baseline averages
        dow_baselines = {}
        for dow in range(7):
            if dow in dow_revenues and dow_revenues[dow]:
                dow_baselines[dow] = statistics.mean(dow_revenues[dow])
            else:
                dow_baselines[dow] = 50000  # Default baseline
        
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        print(f"\n📊 BASELINE REVENUE (excluding potential Lolla dates):")
        for dow in range(7):
            print(f"   {days_names[dow]}: ${dow_baselines[dow]:,.2f}")
        
        # Analyze high revenue days in Lolla season
        lolla_dates, potential_lolla = self.identify_lollapalooza_dates()
        
        print(f"\n🔍 LOLLAPALOOZA IMPACT ANALYSIS:")
        
        # Look at top 10 revenue days in Lolla season
        lolla_impacts = []
        
        for record in potential_lolla[:10]:
            baseline = dow_baselines[record['day_of_week']]
            actual = record['total_revenue']
            impact_ratio = actual / baseline if baseline > 0 else 1.0
            impact_percent = (impact_ratio - 1.0) * 100
            
            day_name = days_names[record['day_of_week']]
            
            print(f"   {record['date'].strftime('%Y-%m-%d')} ({day_name}):")
            print(f"      Actual: ${actual:,.2f}")
            print(f"      Baseline: ${baseline:,.2f}")
            print(f"      Impact: {impact_ratio:.2f}x ({impact_percent:+.1f}%)")
            
            lolla_impacts.append(impact_ratio)
        
        # Calculate average impact
        if lolla_impacts:
            avg_impact = statistics.mean(lolla_impacts)
            median_impact = statistics.median(lolla_impacts)
            max_impact = max(lolla_impacts)
            min_impact = min(lolla_impacts)
            
            print(f"\n📊 LOLLAPALOOZA IMPACT STATISTICS:")
            print(f"   Average Impact: {avg_impact:.2f}x ({(avg_impact-1)*100:+.1f}%)")
            print(f"   Median Impact: {median_impact:.2f}x ({(median_impact-1)*100:+.1f}%)")
            print(f"   Max Impact: {max_impact:.2f}x ({(max_impact-1)*100:+.1f}%)")
            print(f"   Min Impact: {min_impact:.2f}x ({(min_impact-1)*100:+.1f}%)")
            
            # Recommendation
            print(f"\n🎯 RECOMMENDED LOLLAPALOOZA MULTIPLIER:")
            conservative_multiplier = min(avg_impact, 1.5)  # Cap at 1.5x for safety
            print(f"   Conservative: {conservative_multiplier:.2f}x ({(conservative_multiplier-1)*100:+.1f}%)")
            print(f"   Realistic: {avg_impact:.2f}x ({(avg_impact-1)*100:+.1f}%)")
            
            return {
                'average_impact': avg_impact,
                'median_impact': median_impact,
                'conservative_multiplier': conservative_multiplier,
                'recommended_multiplier': avg_impact
            }
        else:
            print(f"   ⚠️  No clear Lollapalooza impact found in historical data")
            return {
                'average_impact': 1.0,
                'median_impact': 1.0,
                'conservative_multiplier': 1.0,
                'recommended_multiplier': 1.0
            }
    
    def analyze_other_major_events(self):
        """Analyze impact of other major events mentioned in notes"""
        print(f"\n🎭 ANALYZING OTHER MAJOR EVENT IMPACTS...")
        
        # Look for other major events in notes
        major_events = {
            'bears': [],
            'fire': [],
            'marathon': [],
            'cubs': [],
            'taste of chicago': [],
            'air and water show': [],
            'chicago blues': [],
            'grant park music': []
        }
        
        for record in self.revenue_data:
            notes_lower = record['notes'].lower()
            for event_key in major_events.keys():
                if event_key in notes_lower:
                    major_events[event_key].append(record)
        
        # Calculate baseline (non-event days)
        all_event_dates = set()
        for event_records in major_events.values():
            for record in event_records:
                all_event_dates.add(record['date'])
        
        # Calculate baseline excluding all major event days
        dow_baselines = defaultdict(list)
        for record in self.revenue_data:
            if record['date'] not in all_event_dates:
                dow_baselines[record['day_of_week']].append(record['total_revenue'])
        
        baseline_averages = {}
        for dow in range(7):
            if dow in dow_baselines and dow_baselines[dow]:
                baseline_averages[dow] = statistics.mean(dow_baselines[dow])
            else:
                baseline_averages[dow] = 50000
        
        # Analyze each event type
        event_impacts = {}
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for event_name, event_records in major_events.items():
            if len(event_records) >= 3:  # Only analyze if we have enough data
                impacts = []
                
                print(f"\n🎪 {event_name.upper()} IMPACT ({len(event_records)} days):")
                
                for record in event_records[:5]:  # Show top 5
                    baseline = baseline_averages[record['day_of_week']]
                    actual = record['total_revenue']
                    impact_ratio = actual / baseline if baseline > 0 else 1.0
                    
                    day_name = days_names[record['day_of_week']]
                    print(f"   {record['date'].strftime('%Y-%m-%d')} ({day_name}): ${actual:,.2f} vs ${baseline:,.2f} = {impact_ratio:.2f}x")
                    
                    impacts.append(impact_ratio)
                
                if impacts:
                    avg_impact = statistics.mean(impacts)
                    event_impacts[event_name] = avg_impact
                    print(f"   Average Impact: {avg_impact:.2f}x ({(avg_impact-1)*100:+.1f}%)")
        
        return event_impacts

def main():
    analyzer = LollapaloozaHistoricalAnalyzer()
    
    # Load historical data
    revenue_data = analyzer.load_historical_data()
    if not revenue_data:
        print("❌ Could not load historical data")
        return
    
    # Identify and analyze Lollapalooza impact
    lolla_impact = analyzer.analyze_lollapalooza_impact()
    
    # Analyze other major events
    other_impacts = analyzer.analyze_other_major_events()
    
    print(f"\n🎯 FINAL RECOMMENDATIONS:")
    print(f"   Lollapalooza Multiplier: {lolla_impact['recommended_multiplier']:.2f}x")
    print(f"   Conservative Lollapalooza: {lolla_impact['conservative_multiplier']:.2f}x")
    
    if other_impacts:
        print(f"\n   Other Event Multipliers:")
        for event, impact in sorted(other_impacts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {event.title()}: {impact:.2f}x")
    
    print(f"\n✅ Historical validation complete!")
    print(f"   Use these multipliers instead of the arbitrary +150% assumption.")

if __name__ == "__main__":
    main()

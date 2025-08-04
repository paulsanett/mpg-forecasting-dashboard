#!/usr/bin/env python3
"""
Complete 7-Day Forecast with Massive Lollapalooza Impact
Shows the incredible revenue boost from Lollapalooza's +150% impact factor
"""

import csv
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import urllib.request
import urllib.parse
import re

class LollapaloozaImpactForecaster:
    def __init__(self, api_key):
        self.api_key = api_key
        self.revenue_data = []
        self.garage_data = {}
        self.events_data = {}
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Correct garage names
        self.garage_names = ['Grant Park North', 'Grant Park South', 'Millennium', 'Lakeside']
        
    def load_revenue_data(self):
        """Load revenue data with correct garage mapping"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/HIstoric Booking Data.csv"
        
        print("🎪 LOLLAPALOOZA IMPACT FORECASTING SYSTEM")
        print("=" * 75)
        print("🔥 Analyzing massive revenue impact from Lollapalooza +150% boost...")
        
        data = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            valid_count = 0
            total_revenue = 0
            garage_totals = defaultdict(float)
            garage_counts = defaultdict(int)
            
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
                    
                    # Extract garage revenues
                    garage_revenues = {}
                    daily_total = 0
                    
                    # Map to correct garage names
                    revenue_cols = [9, 15, 21, 27]  # 4 main revenue columns
                    
                    for i, (garage_name, col_idx) in enumerate(zip(self.garage_names, revenue_cols)):
                        if col_idx < len(row):
                            revenue_str = row[col_idx].strip()
                            if revenue_str:
                                clean_revenue = ""
                                for char in revenue_str:
                                    if char.isdigit() or char == '.' or char == '-':
                                        clean_revenue += char
                                
                                if clean_revenue and clean_revenue != '-' and clean_revenue != '.':
                                    try:
                                        revenue = float(clean_revenue)
                                        if revenue > 100:
                                            garage_revenues[garage_name] = revenue
                                            daily_total += revenue
                                            garage_totals[garage_name] += revenue
                                            garage_counts[garage_name] += 1
                                    except:
                                        continue
                    
                    # Get total revenue from main column
                    if len(row) > 37:
                        total_revenue_str = row[37].strip()
                        if total_revenue_str:
                            clean_total = ""
                            for char in total_revenue_str:
                                if char.isdigit() or char == '.' or char == '-':
                                    clean_total += char
                            
                            if clean_total and clean_total != '-' and clean_total != '.':
                                try:
                                    total_rev = float(clean_total)
                                    if total_rev > 1000:
                                        daily_total = max(daily_total, total_rev)
                                except:
                                    pass
                    
                    if daily_total > 1000:
                        data.append({
                            'date': date,
                            'total_revenue': daily_total,
                            'garage_revenues': garage_revenues,
                            'day_of_week': date.weekday()
                        })
                        total_revenue += daily_total
                        valid_count += 1
                
                except:
                    continue
            
            print(f"✅ Revenue Data: {valid_count:,} records, ${total_revenue:,.2f} total")
            
            data.sort(key=lambda x: x['date'])
            self.revenue_data = data
            self.garage_data = {
                'totals': garage_totals,
                'counts': garage_counts,
                'names': self.garage_names
            }
            
            return data
    
    def load_events_with_lollapalooza(self):
        """Load events with special focus on Lollapalooza impact"""
        file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/MG Event Calendar 2025.csv"
        
        print(f"\n🎉 Loading Events with Lollapalooza Detection...")
        
        events_by_date = {}
        lollapalooza_dates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        start_date_str = row.get('Start Date', '').strip()
                        end_date_str = row.get('End Date', '').strip()
                        event_name = row.get('Event', '').strip()
                        event_type = row.get('Event Type', '').strip()
                        location = row.get('Location', '').strip()
                        tier = row.get('Tier', '').strip()
                        
                        if not start_date_str or not end_date_str or not event_name:
                            continue
                        
                        # Parse dates
                        start_date_clean = re.sub(r'^[A-Za-z]+,\s*', '', start_date_str)
                        end_date_clean = re.sub(r'^[A-Za-z]+,\s*', '', end_date_str)
                        
                        start_date_obj = None
                        end_date_obj = None
                        
                        date_formats = ['%b %d', '%B %d', '%m/%d', '%m-%d']
                        
                        for fmt in date_formats:
                            try:
                                start_parsed = datetime.strptime(start_date_clean, fmt)
                                start_date_obj = start_parsed.replace(year=2025)
                                break
                            except:
                                continue
                        
                        for fmt in date_formats:
                            try:
                                end_parsed = datetime.strptime(end_date_clean, fmt)
                                end_date_obj = end_parsed.replace(year=2025)
                                break
                            except:
                                continue
                        
                        if start_date_obj and end_date_obj:
                            # Create event for every day in range
                            current_date = start_date_obj
                            
                            while current_date <= end_date_obj:
                                date_key = current_date.strftime('%Y-%m-%d')
                                
                                if date_key not in events_by_date:
                                    events_by_date[date_key] = []
                                
                                impact_category = self.categorize_event(event_name, event_type, location, tier)
                                impact_factor = self.get_event_impact_factor(impact_category, tier)
                                
                                events_by_date[date_key].append({
                                    'name': event_name,
                                    'type': event_type,
                                    'location': location,
                                    'tier': tier,
                                    'impact_category': impact_category,
                                    'impact_factor': impact_factor
                                })
                                
                                # Track Lollapalooza specifically
                                if 'lollapalooza' in event_name.lower() or 'lolla' in event_name.lower():
                                    lollapalooza_dates.append(date_key)
                                
                                current_date += timedelta(days=1)
                    
                    except:
                        continue
            
            print(f"✅ Events loaded successfully")
            
            if lollapalooza_dates:
                print(f"\n🔥 LOLLAPALOOZA DETECTED!")
                print(f"   Dates: {', '.join(sorted(set(lollapalooza_dates)))}")
                print(f"   Impact: +150% revenue boost (2.5x multiplier)")
            
            self.events_data = events_by_date
            return events_by_date
            
        except Exception as e:
            print(f"⚠️  Could not load events: {e}")
            return {}
    
    def categorize_event(self, name, event_type, location, tier):
        """Categorize events with special Lollapalooza handling"""
        name_lower = name.lower()
        
        if 'lollapalooza' in name_lower or 'lolla' in name_lower:
            return 'mega_festival'
        elif 'fire fc' in name_lower or 'bears' in name_lower:
            return 'major_sports'
        elif 'symphony' in name_lower or 'orchestra' in name_lower:
            return 'major_performance'
        elif event_type.lower() == 'holiday':
            return 'holiday'
        elif 'festival' in name_lower:
            return 'festival'
        elif event_type.lower() == 'performance':
            return 'performance'
        else:
            return 'other'
    
    def get_event_impact_factor(self, category, tier):
        """Get impact factors with massive Lollapalooza boost"""
        base_factors = {
            'mega_festival': 2.50,     # Lollapalooza: +150%
            'major_sports': 1.45,      # Major sports: +45%
            'major_performance': 1.35, # Major performances: +35%
            'holiday': 1.25,           # Holidays: +25%
            'performance': 1.20,       # Performances: +20%
            'festival': 1.30,          # Festivals: +30%
            'other': 1.05              # Other: +5%
        }
        
        base_factor = base_factors.get(category, 1.0)
        
        # Tier adjustments
        if tier == 'Tier 1':
            base_factor *= 1.2
        elif tier == 'Tier 2':
            base_factor *= 1.1
        elif tier == 'Tier 3':
            base_factor *= 1.05
        
        return min(base_factor, 3.0)
    
    def create_lollapalooza_forecast(self, days=7):
        """Create 7-day forecast highlighting Lollapalooza impact"""
        print(f"\n🔮 Creating 7-Day Forecast with Lollapalooza Impact")
        print("=" * 70)
        
        # Start from tomorrow
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today + timedelta(days=1)
        
        print(f"📅 Forecast Period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=days-1)).strftime('%Y-%m-%d')}")
        
        # Calculate baseline patterns
        recent_cutoff = today - timedelta(days=90)
        recent_data = [d for d in self.revenue_data if d['date'] >= recent_cutoff]
        
        if len(recent_data) < 10:
            recent_data = self.revenue_data[-30:] if len(self.revenue_data) >= 30 else self.revenue_data
        
        # Day-of-week patterns
        dow_total = defaultdict(list)
        dow_garages = {garage: defaultdict(list) for garage in self.garage_names}
        
        for record in recent_data:
            dow = record['day_of_week']
            dow_total[dow].append(record['total_revenue'])
            
            for garage_name in self.garage_names:
                if garage_name in record['garage_revenues']:
                    dow_garages[garage_name][dow].append(record['garage_revenues'][garage_name])
        
        # Calculate averages
        dow_avg_total = {}
        dow_avg_garages = {garage: {} for garage in self.garage_names}
        overall_avg = statistics.mean([r['total_revenue'] for r in recent_data])
        
        for dow in range(7):
            if dow in dow_total and dow_total[dow]:
                dow_avg_total[dow] = statistics.mean(dow_total[dow])
            else:
                dow_avg_total[dow] = overall_avg
            
            for garage_name in self.garage_names:
                if dow in dow_garages[garage_name] and dow_garages[garage_name][dow]:
                    dow_avg_garages[garage_name][dow] = statistics.mean(dow_garages[garage_name][dow])
                else:
                    # Proportional share
                    if garage_name in self.garage_data['totals'] and self.garage_data['counts'][garage_name] > 0:
                        garage_avg = self.garage_data['totals'][garage_name] / self.garage_data['counts'][garage_name]
                        total_garage_avg = sum(self.garage_data['totals'][g] / max(self.garage_data['counts'][g], 1) for g in self.garage_names)
                        if total_garage_avg > 0:
                            proportion = garage_avg / total_garage_avg
                            dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * proportion
                        else:
                            dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * 0.25
                    else:
                        dow_avg_garages[garage_name][dow] = dow_avg_total[dow] * 0.25
        
        # Generate forecast
        forecast = []
        days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            dow = forecast_date.weekday()
            date_str = forecast_date.strftime('%Y-%m-%d')
            
            # Base forecast
            base_total = dow_avg_total[dow]
            base_garages = {garage: dow_avg_garages[garage][dow] for garage in self.garage_names}
            
            # Events adjustment
            events_adjustment = 1.0
            events_info = []
            lollapalooza_active = False
            
            if date_str in self.events_data:
                events_info = self.events_data[date_str]
                for event in events_info:
                    events_adjustment *= event['impact_factor']
                    if event['impact_category'] == 'mega_festival':
                        lollapalooza_active = True
                events_adjustment = min(events_adjustment, 3.0)
            
            # Final predictions
            final_total = base_total * events_adjustment
            final_garages = {garage: base_garages[garage] * events_adjustment for garage in self.garage_names}
            
            forecast_item = {
                'date': date_str,
                'day_name': days_names[dow],
                'base_total': round(base_total, 2),
                'base_garages': {garage: round(base_garages[garage], 2) for garage in self.garage_names},
                'events_adjustment': round(events_adjustment, 3),
                'final_total': round(final_total, 2),
                'final_garages': {garage: round(final_garages[garage], 2) for garage in self.garage_names},
                'events_info': events_info,
                'lollapalooza_active': lollapalooza_active
            }
            
            forecast.append(forecast_item)
        
        return forecast
    
    def display_lollapalooza_forecast(self, forecast):
        """Display forecast with Lollapalooza impact highlighted"""
        total_forecast = sum(day['final_total'] for day in forecast)
        base_total = sum(day['base_total'] for day in forecast)
        lollapalooza_boost = total_forecast - base_total
        
        print(f"\n📈 7-DAY FORECAST WITH LOLLAPALOOZA IMPACT")
        print("=" * 75)
        print(f"💰 Total Forecasted Revenue: ${total_forecast:,.2f}")
        print(f"📊 Base Revenue (without events): ${base_total:,.2f}")
        print(f"🔥 LOLLAPALOOZA BOOST: +${lollapalooza_boost:,.2f}")
        print(f"📅 Monthly Projection: ${(total_forecast/len(forecast))*30:,.2f}")
        
        print(f"\n🎯 DETAILED DAILY FORECAST:")
        print("-" * 75)
        
        for day in forecast:
            lolla_indicator = "🔥 LOLLAPALOOZA DAY!" if day['lollapalooza_active'] else ""
            
            print(f"\n📅 {day['date']} ({day['day_name']}) {lolla_indicator}")
            
            # Base forecast
            print(f"   📊 BASE FORECAST: ${day['base_total']:,.2f}")
            for garage in self.garage_names:
                if garage in day['base_garages']:
                    print(f"      {garage}: ${day['base_garages'][garage]:,.2f}")
            
            # Events impact
            if day['events_info']:
                print(f"   🎉 EVENTS IMPACT: {day['events_adjustment']:.3f}x")
                for event in day['events_info'][:3]:
                    impact_emoji = "🔥" if event['impact_category'] == 'mega_festival' else "🎪"
                    print(f"      {impact_emoji} {event['name']} ({event['impact_category']})")
            
            # Final forecast with boost
            boost_amount = day['final_total'] - day['base_total']
            print(f"   🎯 FINAL FORECAST: ${day['final_total']:,.2f} (+${boost_amount:,.2f})")
            
            if day['lollapalooza_active']:
                print(f"   🔥 LOLLAPALOOZA GARAGE BREAKDOWN:")
                for garage in self.garage_names:
                    if garage in day['final_garages']:
                        garage_boost = day['final_garages'][garage] - day['base_garages'][garage]
                        print(f"      {garage}: ${day['final_garages'][garage]:,.2f} (+${garage_boost:,.2f})")
            else:
                print(f"   🏢 GARAGE BREAKDOWN:")
                for garage in self.garage_names:
                    if garage in day['final_garages']:
                        print(f"      {garage}: ${day['final_garages'][garage]:,.2f}")
        
        # Save results
        filename = 'lollapalooza_impact_forecast.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            headers = ['Date', 'Day', 'Base_Total', 'Events_Adj', 'Final_Total', 'Lollapalooza_Active']
            for garage in self.garage_names:
                headers.extend([f'{garage}_Base', f'{garage}_Final', f'{garage}_Boost'])
            headers.append('Major_Events')
            writer.writerow(headers)
            
            for day in forecast:
                events = day['events_info'] or []
                major_events = '; '.join([e['name'] for e in events[:2]])
                
                row = [
                    day['date'], day['day_name'], day['base_total'],
                    day['events_adjustment'], day['final_total'], day['lollapalooza_active']
                ]
                
                for garage in self.garage_names:
                    base = day['base_garages'].get(garage, 0)
                    final = day['final_garages'].get(garage, 0)
                    boost = final - base
                    row.extend([base, final, boost])
                
                row.append(major_events)
                writer.writerow(row)
        
        print(f"\n💾 Lollapalooza impact forecast saved to: {filename}")
        
        # Summary
        lolla_days = sum(1 for day in forecast if day['lollapalooza_active'])
        if lolla_days > 0:
            print(f"\n🔥 LOLLAPALOOZA IMPACT SUMMARY:")
            print(f"   🎪 Lollapalooza Days: {lolla_days} of {len(forecast)} days")
            print(f"   💰 Total Revenue Boost: +${lollapalooza_boost:,.2f}")
            print(f"   📈 Average Daily Boost: +${lollapalooza_boost/lolla_days:,.2f} per Lolla day")
            print(f"   🚀 This is MASSIVE for your parking business!")
        
        print(f"\n🏆 LOLLAPALOOZA FORECASTING COMPLETE!")

def main():
    api_key = "db6ca4a5eb88cfbb09ae4bd8713460b7"
    
    forecaster = LollapaloozaImpactForecaster(api_key)
    
    # Load data
    revenue_data = forecaster.load_revenue_data()
    if not revenue_data:
        print("❌ Could not load revenue data")
        return
    
    events_data = forecaster.load_events_with_lollapalooza()
    
    # Create and display forecast
    forecast = forecaster.create_lollapalooza_forecast(days=7)
    forecaster.display_lollapalooza_forecast(forecast)

if __name__ == "__main__":
    main()

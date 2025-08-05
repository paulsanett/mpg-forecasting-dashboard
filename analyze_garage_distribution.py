#!/usr/bin/env python3
"""
Analyze actual garage distribution from historical data using correct column mappings
"""

from robust_csv_reader import RobustCSVReader
import statistics

def analyze_garage_distribution():
    """Analyze actual garage distribution from historical data"""
    
    print("📊 ANALYZING ACTUAL GARAGE DISTRIBUTION FROM HISTORICAL DATA")
    print("="*80)
    
    # Load historical data using corrected column mappings
    csv_reader = RobustCSVReader('HIstoric Booking Data.csv')
    historical_data = csv_reader.read_csv_robust()
    
    if not historical_data:
        print("❌ Error: Could not load historical data")
        return
    
    print(f"✅ Loaded {len(historical_data)} historical records")
    
    # Analyze garage revenue distribution
    garage_totals = {
        'Grant Park North': 0,
        'Grant Park South': 0,
        'Millennium': 0,
        'Lakeside': 0,
        'Online': 0,
        'Total': 0
    }
    
    valid_records = 0
    
    for record in historical_data:
        # Only analyze records with complete garage data
        if all(key in record for key in ['gpn_revenue', 'gps_revenue', 'millennium_revenue', 'lakeside_revenue', 'online_revenue', 'total_revenue']):
            garage_totals['Grant Park North'] += record['gpn_revenue']
            garage_totals['Grant Park South'] += record['gps_revenue']
            garage_totals['Millennium'] += record['millennium_revenue']
            garage_totals['Lakeside'] += record['lakeside_revenue']
            garage_totals['Online'] += record['online_revenue']
            garage_totals['Total'] += record['total_revenue']
            valid_records += 1
    
    if valid_records == 0:
        print("❌ No records found with complete garage data")
        print("📋 Available fields in data:")
        if historical_data:
            print(f"   Sample record keys: {list(historical_data[0].keys())}")
        return
    
    print(f"✅ Analyzed {valid_records} records with complete garage data")
    
    # Calculate percentages
    total_revenue = garage_totals['Total']
    if total_revenue == 0:
        print("❌ Total revenue is zero - cannot calculate percentages")
        return
    
    print(f"\n📊 ACTUAL GARAGE REVENUE DISTRIBUTION")
    print("-" * 60)
    print(f"{'Garage':<20} {'Total Revenue':<15} {'Percentage':<12}")
    print("-" * 60)
    
    garage_percentages = {}
    garage_sum = 0
    
    for garage in ['Grant Park North', 'Grant Park South', 'Millennium', 'Lakeside', 'Online']:
        revenue = garage_totals[garage]
        percentage = (revenue / total_revenue) * 100
        garage_percentages[garage] = percentage / 100  # Convert to decimal
        garage_sum += revenue
        
        print(f"{garage:<20} ${revenue:>12,.0f} {percentage:>10.1f}%")
    
    print("-" * 60)
    print(f"{'Sum of Garages':<20} ${garage_sum:>12,.0f} {(garage_sum/total_revenue)*100:>10.1f}%")
    print(f"{'Total Revenue':<20} ${total_revenue:>12,.0f} {100.0:>10.1f}%")
    
    # Check if garage sum matches total
    discrepancy = total_revenue - garage_sum
    if abs(discrepancy) > 1:  # Allow for small rounding errors
        print(f"⚠️  DISCREPANCY: ${discrepancy:,.0f} ({(discrepancy/total_revenue)*100:.1f}%)")
    else:
        print("✅ Garage sum matches total revenue!")
    
    # Generate updated garage distribution for forecasting system
    print(f"\n🔧 UPDATED GARAGE DISTRIBUTION FOR FORECASTING SYSTEM")
    print("-" * 60)
    print("# Updated garage distribution based on actual historical data:")
    print("self.garage_distribution = {")
    for garage in ['Grant Park North', 'Grant Park South', 'Millennium', 'Lakeside', 'Online']:
        percentage = garage_percentages[garage]
        garage_key = garage.replace(' ', '_').replace('Park', '').lower()
        if garage == 'Grant Park North':
            garage_key = 'grant_park_north'
        elif garage == 'Grant Park South':
            garage_key = 'grant_park_south'
        elif garage == 'Millennium':
            garage_key = 'millennium'
        elif garage == 'Lakeside':
            garage_key = 'lakeside'
        elif garage == 'Online':
            garage_key = 'online'
        
        print(f"    '{garage}': {percentage:.3f},  # {percentage*100:.1f}%")
    print("}")
    
    # Analyze recent trends (last 30 days)
    print(f"\n📈 RECENT TRENDS ANALYSIS (Last 30 Records)")
    print("-" * 60)
    
    recent_data = historical_data[-30:] if len(historical_data) >= 30 else historical_data
    recent_totals = {garage: 0 for garage in garage_totals.keys()}
    recent_valid = 0
    
    for record in recent_data:
        if all(key in record for key in ['gpn_revenue', 'gps_revenue', 'millennium_revenue', 'lakeside_revenue', 'online_revenue', 'total_revenue']):
            recent_totals['Grant Park North'] += record['gpn_revenue']
            recent_totals['Grant Park South'] += record['gps_revenue']
            recent_totals['Millennium'] += record['millennium_revenue']
            recent_totals['Lakeside'] += record['lakeside_revenue']
            recent_totals['Online'] += record['online_revenue']
            recent_totals['Total'] += record['total_revenue']
            recent_valid += 1
    
    if recent_valid > 0 and recent_totals['Total'] > 0:
        print(f"Recent data ({recent_valid} records):")
        for garage in ['Grant Park North', 'Grant Park South', 'Millennium', 'Lakeside', 'Online']:
            recent_pct = (recent_totals[garage] / recent_totals['Total']) * 100
            historical_pct = garage_percentages[garage] * 100
            trend = recent_pct - historical_pct
            trend_symbol = "📈" if trend > 1 else "📉" if trend < -1 else "➡️"
            print(f"  {garage:<20}: {recent_pct:>5.1f}% (vs {historical_pct:>5.1f}% historical) {trend_symbol}")

if __name__ == "__main__":
    analyze_garage_distribution()

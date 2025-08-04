#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def load_parking_data(file_path):
    """Load and parse the parking data"""
    data = []
    garages = set()
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                date = datetime.strptime(row['Date'], '%Y-%m-%d')
                garage = row['Garage']
                revenue = float(row['Revenue'])
                
                data.append({
                    'date': date,
                    'garage': garage,
                    'revenue': revenue,
                    'day_of_week': date.weekday(),
                    'month': date.month,
                    'year': date.year
                })
                garages.add(garage)
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e}")
                continue
    
    return data, list(garages)

def analyze_garage_data(data, garage_name):
    """Analyze data for a specific garage"""
    garage_data = [row for row in data if row['garage'] == garage_name]
    
    if not garage_data:
        return None
    
    # Sort by date
    garage_data.sort(key=lambda x: x['date'])
    
    # Basic statistics
    revenues = [row['revenue'] for row in garage_data]
    total_revenue = sum(revenues)
    avg_revenue = statistics.mean(revenues)
    median_revenue = statistics.median(revenues)
    std_revenue = statistics.stdev(revenues) if len(revenues) > 1 else 0
    
    # Day of week analysis
    dow_revenues = defaultdict(list)
    for row in garage_data:
        dow_revenues[row['day_of_week']].append(row['revenue'])
    
    dow_averages = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for dow in range(7):
        if dow in dow_revenues:
            dow_averages[days[dow]] = statistics.mean(dow_revenues[dow])
    
    # Monthly analysis
    monthly_revenues = defaultdict(list)
    for row in garage_data:
        monthly_revenues[row['month']].append(row['revenue'])
    
    monthly_averages = {}
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month in range(1, 13):
        if month in monthly_revenues:
            monthly_averages[months[month-1]] = statistics.mean(monthly_revenues[month])
    
    # Recent trend (last 30 days)
    recent_data = [row for row in garage_data if row['date'] >= garage_data[-1]['date'] - timedelta(days=30)]
    recent_avg = statistics.mean([row['revenue'] for row in recent_data]) if recent_data else 0
    
    return {
        'garage': garage_name,
        'total_records': len(garage_data),
        'date_range': (garage_data[0]['date'], garage_data[-1]['date']),
        'total_revenue': total_revenue,
        'avg_revenue': avg_revenue,
        'median_revenue': median_revenue,
        'std_revenue': std_revenue,
        'dow_averages': dow_averages,
        'monthly_averages': monthly_averages,
        'recent_avg': recent_avg,
        'data': garage_data
    }

def simple_forecast(garage_analysis, days=30):
    """Create a simple forecast based on historical patterns"""
    if not garage_analysis:
        return None
    
    data = garage_analysis['data']
    last_date = data[-1]['date']
    
    # Calculate seasonal factors
    dow_factors = {}
    overall_avg = garage_analysis['avg_revenue']
    
    for day, avg in garage_analysis['dow_averages'].items():
        dow_factors[day] = avg / overall_avg if overall_avg > 0 else 1
    
    # Generate forecast
    forecast = []
    for i in range(1, days + 1):
        forecast_date = last_date + timedelta(days=i)
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][forecast_date.weekday()]
        
        # Base forecast on recent average adjusted by day-of-week factor
        base_forecast = garage_analysis['recent_avg']
        dow_factor = dow_factors.get(day_name, 1)
        
        predicted_revenue = base_forecast * dow_factor
        
        forecast.append({
            'date': forecast_date,
            'day_name': day_name,
            'predicted_revenue': predicted_revenue
        })
    
    return forecast

def main():
    print("🚗 Simple Parking Revenue Analysis")
    print("=" * 50)
    
    file_path = "/Users/PaulSanett/Desktop/CascadeProjects/windsurf-project/Cleaned_Transient_Revenue_Data_updated.csv"
    
    try:
        # Load data
        print("📊 Loading parking data...")
        data, garages = load_parking_data(file_path)
        
        print(f"✅ Loaded {len(data):,} records")
        print(f"🏢 Garages found: {', '.join(garages)}")
        
        # Analyze each garage
        garage_analyses = {}
        for garage in garages:
            print(f"\n🎯 Analyzing {garage} garage...")
            analysis = analyze_garage_data(data, garage)
            if analysis:
                garage_analyses[garage] = analysis
                
                print(f"  📈 Records: {analysis['total_records']:,}")
                print(f"  📅 Date range: {analysis['date_range'][0].strftime('%Y-%m-%d')} to {analysis['date_range'][1].strftime('%Y-%m-%d')}")
                print(f"  💰 Total revenue: ${analysis['total_revenue']:,.2f}")
                print(f"  📊 Average daily: ${analysis['avg_revenue']:.2f}")
                print(f"  📊 Recent 30-day avg: ${analysis['recent_avg']:.2f}")
                
                print(f"  📊 Day of week averages:")
                for day, avg in analysis['dow_averages'].items():
                    print(f"    {day}: ${avg:.2f}")
        
        # Focus on GPN (appears to have the most complete data)
        if 'GPN' in garage_analyses:
            print(f"\n🔮 Generating 30-day forecast for GPN garage...")
            gpn_analysis = garage_analyses['GPN']
            forecast = simple_forecast(gpn_analysis, 30)
            
            if forecast:
                total_forecast = sum(day['predicted_revenue'] for day in forecast)
                avg_forecast = total_forecast / len(forecast)
                
                print(f"📈 Forecast Summary (next 30 days):")
                print(f"  Average daily revenue: ${avg_forecast:.2f}")
                print(f"  Total forecasted revenue: ${total_forecast:.2f}")
                print(f"  Min daily forecast: ${min(day['predicted_revenue'] for day in forecast):.2f}")
                print(f"  Max daily forecast: ${max(day['predicted_revenue'] for day in forecast):.2f}")
                
                print(f"\n📅 Next 7 days forecast:")
                for i in range(min(7, len(forecast))):
                    day = forecast[i]
                    print(f"  {day['date'].strftime('%Y-%m-%d')} ({day['day_name']}): ${day['predicted_revenue']:.2f}")
                
                # Calculate accuracy estimate based on recent variance
                recent_revenues = [row['revenue'] for row in gpn_analysis['data'][-30:]]
                if len(recent_revenues) > 1:
                    recent_std = statistics.stdev(recent_revenues)
                    recent_avg = statistics.mean(recent_revenues)
                    cv = (recent_std / recent_avg) * 100 if recent_avg > 0 else 0
                    print(f"\n📊 Model Accuracy Estimate:")
                    print(f"  Recent coefficient of variation: {cv:.1f}%")
                    print(f"  Expected forecast accuracy: ±{cv:.1f}%")
                
                # Save forecast
                with open('simple_parking_forecast.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Day', 'Predicted_Revenue'])
                    for day in forecast:
                        writer.writerow([
                            day['date'].strftime('%Y-%m-%d'),
                            day['day_name'],
                            f"{day['predicted_revenue']:.2f}"
                        ])
                
                print(f"\n💾 Forecast saved to: simple_parking_forecast.csv")
        
        print(f"\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

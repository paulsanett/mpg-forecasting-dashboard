#!/usr/bin/env python3
"""
DATA QUALITY INVESTIGATOR
Investigates potential data quality issues preventing 2-5% accuracy
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import numpy as np

class DataQualityInvestigator:
    def __init__(self):
        self.reader = RobustCSVReader()
        self.data = None
        self.issues_found = []
        
    def load_data(self):
        """Load and prepare data for quality analysis"""
        print('🔍 LOADING DATA FOR QUALITY INVESTIGATION')
        print('=' * 60)
        
        self.data = self.reader.read_csv_robust()
        
        # Filter for recent data
        cutoff_date = datetime(2024, 8, 6)
        quality_data = []
        
        for record in self.data:
            if record.get('date') and record.get('total_revenue', 0) > 0:
                try:
                    date_str = str(record.get('date', ''))
                    date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    
                    if date_obj >= cutoff_date:
                        quality_data.append({
                            'date': date_obj,
                            'day_of_week': record.get('day_of_week', '').strip(),
                            'total_revenue': record.get('total_revenue', 0),
                            'gpn_revenue': record.get('gpn_revenue', 0),
                            'gps_revenue': record.get('gps_revenue', 0),
                            'millennium_revenue': record.get('millennium_revenue', 0),
                            'lakeside_revenue': record.get('lakeside_revenue', 0),
                            'online_revenue': record.get('online_revenue', 0),
                            'month': date_obj.month,
                            'year': date_obj.year
                        })
                except:
                    continue
        
        print(f'✅ Loaded {len(quality_data)} records for quality analysis')
        return quality_data
    
    def investigate_revenue_consistency(self, data):
        """Check for revenue consistency issues"""
        print('\n🔍 INVESTIGATING REVENUE CONSISTENCY')
        print('=' * 50)
        
        consistency_issues = []
        
        for record in data:
            total = record['total_revenue']
            garage_sum = (record['gpn_revenue'] + record['gps_revenue'] + 
                         record['millennium_revenue'] + record['lakeside_revenue'] + 
                         record['online_revenue'])
            
            if abs(total - garage_sum) > 100:  # Allow $100 tolerance
                consistency_issues.append({
                    'date': record['date'],
                    'total_revenue': total,
                    'garage_sum': garage_sum,
                    'difference': abs(total - garage_sum)
                })
        
        if consistency_issues:
            print(f'❌ Found {len(consistency_issues)} revenue consistency issues')
            print('Top 5 largest discrepancies:')
            consistency_issues.sort(key=lambda x: x['difference'], reverse=True)
            for issue in consistency_issues[:5]:
                print(f"  {issue['date'].strftime('%Y-%m-%d')}: Total ${issue['total_revenue']:,.0f} vs Sum ${issue['garage_sum']:,.0f} (Diff: ${issue['difference']:,.0f})")
            
            self.issues_found.append(f"Revenue consistency: {len(consistency_issues)} records with garage/total mismatches")
        else:
            print('✅ Revenue consistency: All records consistent')
        
        return len(consistency_issues)
    
    def investigate_outliers(self, data):
        """Identify potential data outliers"""
        print('\n🔍 INVESTIGATING REVENUE OUTLIERS')
        print('=' * 40)
        
        # Group by day of week
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        outliers_found = []
        
        for day_abbr, day_name in day_mapping.items():
            day_data = [d for d in data if d['day_of_week'].upper() == day_abbr]
            
            if len(day_data) >= 10:
                revenues = [d['total_revenue'] for d in day_data]
                
                # Calculate outlier thresholds using IQR method
                q1 = np.percentile(revenues, 25)
                q3 = np.percentile(revenues, 75)
                iqr = q3 - q1
                lower_bound = q1 - 2.0 * iqr  # More aggressive outlier detection
                upper_bound = q3 + 2.0 * iqr
                
                day_outliers = [d for d in day_data if d['total_revenue'] < lower_bound or d['total_revenue'] > upper_bound]
                
                if day_outliers:
                    print(f'{day_name}: {len(day_outliers)} outliers (Range: ${lower_bound:,.0f} - ${upper_bound:,.0f})')
                    for outlier in day_outliers[:3]:  # Show top 3
                        print(f"  {outlier['date'].strftime('%Y-%m-%d')}: ${outlier['total_revenue']:,.0f}")
                    
                    outliers_found.extend(day_outliers)
        
        if outliers_found:
            self.issues_found.append(f"Revenue outliers: {len(outliers_found)} extreme values detected")
        
        print(f'\n📊 Total outliers found: {len(outliers_found)}')
        return len(outliers_found)
    
    def investigate_missing_factors(self, data):
        """Investigate potentially missing predictive factors"""
        print('\n🔍 INVESTIGATING MISSING PREDICTIVE FACTORS')
        print('=' * 55)
        
        # Analyze unexplained variance patterns
        day_variance_analysis = {}
        
        day_mapping = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday'
        }
        
        for day_abbr, day_name in day_mapping.items():
            day_data = [d for d in data if d['day_of_week'].upper() == day_abbr]
            
            if len(day_data) >= 10:
                revenues = [d['total_revenue'] for d in day_data]
                
                # Calculate variance metrics
                mean_rev = statistics.mean(revenues)
                std_dev = statistics.stdev(revenues)
                cv = (std_dev / mean_rev) * 100
                
                # Seasonal analysis
                seasonal_variance = {}
                for season in ['Winter', 'Spring', 'Summer', 'Fall']:
                    season_data = []
                    for d in day_data:
                        if season == 'Winter' and d['month'] in [12, 1, 2]:
                            season_data.append(d['total_revenue'])
                        elif season == 'Spring' and d['month'] in [3, 4, 5]:
                            season_data.append(d['total_revenue'])
                        elif season == 'Summer' and d['month'] in [6, 7, 8]:
                            season_data.append(d['total_revenue'])
                        elif season == 'Fall' and d['month'] in [9, 10, 11]:
                            season_data.append(d['total_revenue'])
                    
                    if len(season_data) >= 3:
                        seasonal_variance[season] = statistics.stdev(season_data) / statistics.mean(season_data) * 100
                
                day_variance_analysis[day_name] = {
                    'overall_cv': cv,
                    'seasonal_cv': seasonal_variance,
                    'sample_size': len(day_data)
                }
        
        print('Day-of-Week Variance Analysis:')
        print('Day        Overall CV%  Winter CV%  Spring CV%  Summer CV%  Fall CV%')
        print('-' * 70)
        
        high_variance_days = []
        
        for day, analysis in day_variance_analysis.items():
            seasonal_cvs = analysis['seasonal_cv']
            winter_cv = seasonal_cvs.get('Winter', 0)
            spring_cv = seasonal_cvs.get('Spring', 0)
            summer_cv = seasonal_cvs.get('Summer', 0)
            fall_cv = seasonal_cvs.get('Fall', 0)
            
            print(f'{day:>9}: {analysis["overall_cv"]:>10.1f}% {winter_cv:>10.1f}% {spring_cv:>10.1f}% {summer_cv:>10.1f}% {fall_cv:>10.1f}%')
            
            if analysis['overall_cv'] > 25:
                high_variance_days.append(day)
        
        if high_variance_days:
            print(f'\n⚠️  High variance days: {", ".join(high_variance_days)}')
            self.issues_found.append(f"High variance: {len(high_variance_days)} days with >25% coefficient of variation")
        
        # Check for potential missing factors
        print('\n💡 POTENTIAL MISSING FACTORS:')
        missing_factors = []
        
        # Weather impact analysis
        print('1. Weather Impact: Not fully captured in current model')
        missing_factors.append('Detailed weather conditions (temperature, precipitation, wind)')
        
        # Event detection gaps
        print('2. Event Detection: May be missing smaller events')
        missing_factors.append('Local events, concerts, festivals not in main calendar')
        
        # Economic factors
        print('3. Economic Factors: Not considered')
        missing_factors.append('Gas prices, economic conditions, tourism patterns')
        
        # Day-of-month effects
        print('4. Day-of-Month Effects: Payroll cycles, month-end patterns')
        missing_factors.append('Payroll dates, month-end effects, holiday proximity')
        
        # Competition effects
        print('5. Competition: Other parking options')
        missing_factors.append('Street parking availability, competing garages, ride-share usage')
        
        self.issues_found.extend([f"Missing factor: {factor}" for factor in missing_factors])
        
        return len(missing_factors)
    
    def investigate_data_gaps(self, data):
        """Check for data gaps and inconsistencies"""
        print('\n🔍 INVESTIGATING DATA GAPS')
        print('=' * 35)
        
        # Check for missing days
        if not data:
            return 0
        
        start_date = min(d['date'] for d in data)
        end_date = max(d['date'] for d in data)
        
        expected_days = (end_date - start_date).days + 1
        actual_days = len(data)
        missing_days = expected_days - actual_days
        
        print(f'Date Range: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
        print(f'Expected Days: {expected_days}')
        print(f'Actual Days: {actual_days}')
        print(f'Missing Days: {missing_days}')
        
        if missing_days > 0:
            self.issues_found.append(f"Data gaps: {missing_days} missing days in dataset")
        
        # Check for zero revenue days
        zero_revenue_days = len([d for d in data if d['total_revenue'] == 0])
        if zero_revenue_days > 0:
            print(f'Zero Revenue Days: {zero_revenue_days}')
            self.issues_found.append(f"Zero revenue: {zero_revenue_days} days with zero revenue")
        
        return missing_days
    
    def generate_recommendations(self):
        """Generate recommendations to improve accuracy"""
        print('\n💡 RECOMMENDATIONS TO ACHIEVE 2-5% ACCURACY')
        print('=' * 60)
        
        recommendations = []
        
        # Based on issues found
        if any('consistency' in issue for issue in self.issues_found):
            recommendations.append('1. Fix revenue consistency issues - clean data discrepancies')
        
        if any('outliers' in issue for issue in self.issues_found):
            recommendations.append('2. Investigate and handle outliers - may indicate data errors or special events')
        
        if any('variance' in issue for issue in self.issues_found):
            recommendations.append('3. Reduce unexplained variance by adding missing predictive factors')
        
        # Always recommend these
        recommendations.extend([
            '4. Enhance weather integration - use detailed weather conditions',
            '5. Improve event detection - capture all local events and activities',
            '6. Add economic indicators - gas prices, tourism data, economic conditions',
            '7. Include temporal patterns - day-of-month effects, payroll cycles',
            '8. Consider external factors - competition, street parking, ride-share',
            '9. Implement ensemble modeling - combine multiple prediction approaches',
            '10. Use real-time calibration - continuously adjust based on recent actuals'
        ])
        
        for rec in recommendations:
            print(rec)
        
        print('\n🎯 PRIORITY ACTIONS FOR 2-5% ACCURACY:')
        print('1. Clean data inconsistencies (immediate impact)')
        print('2. Add detailed weather data (moderate impact)')
        print('3. Enhance event detection (moderate impact)')
        print('4. Implement ensemble modeling (high impact)')
        
        return recommendations
    
    def run_investigation(self):
        """Run complete data quality investigation"""
        print('🔍 DATA QUALITY INVESTIGATION')
        print('=' * 50)
        print('Investigating why we cannot achieve 2-5% accuracy target')
        print()
        
        # Load data
        data = self.load_data()
        
        if not data:
            print('❌ No data available for investigation')
            return
        
        # Run investigations
        consistency_issues = self.investigate_revenue_consistency(data)
        outlier_count = self.investigate_outliers(data)
        missing_factors = self.investigate_missing_factors(data)
        data_gaps = self.investigate_data_gaps(data)
        
        # Summary
        print('\n📊 INVESTIGATION SUMMARY')
        print('=' * 35)
        print(f'Total Issues Found: {len(self.issues_found)}')
        
        for i, issue in enumerate(self.issues_found, 1):
            print(f'{i:2d}. {issue}')
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        print('\n🎯 CONCLUSION')
        print('=' * 20)
        print('The 2-5% accuracy target is challenging due to:')
        print('• Inherent revenue variability in parking business')
        print('• Missing predictive factors (weather, events, economic)')
        print('• Data quality issues requiring cleanup')
        print('• Need for more sophisticated modeling approaches')
        
        return {
            'issues_found': self.issues_found,
            'recommendations': recommendations,
            'data_quality_score': max(0, 100 - len(self.issues_found) * 5)
        }

def main():
    investigator = DataQualityInvestigator()
    results = investigator.run_investigation()
    return results

if __name__ == "__main__":
    main()

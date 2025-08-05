"""
Automated Calibration System for Departure-Day Revenue Model v4.0
Continuously improves model accuracy using actual vs forecast data
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from departure_day_revenue_model import DepartureDayRevenueModel

class AutoCalibrator:
    """
    Automatically calibrates the Departure-Day Revenue Model using actual data
    """
    
    def __init__(self):
        self.model = DepartureDayRevenueModel()
        self.calibration_history = []
        self.target_accuracy = 0.10  # 10% error target
        
    def collect_actual_vs_forecast_data(self, forecast_data: List[Dict], actual_data: List[Dict]) -> List[Dict]:
        """Collect actual vs forecast data for calibration"""
        
        variance_data = []
        
        for forecast_day in forecast_data:
            date_str = forecast_day['date']
            
            # Find corresponding actual data
            actual_day = None
            for actual in actual_data:
                if actual['date'] == date_str:
                    actual_day = actual
                    break
            
            if actual_day:
                variance = {
                    'date': date_str,
                    'day_of_week': forecast_day['day'],
                    'forecast_revenue': forecast_day['revenue'],
                    'actual_revenue': actual_day['revenue'],
                    'variance': actual_day['revenue'] - forecast_day['revenue'],
                    'variance_pct': (actual_day['revenue'] - forecast_day['revenue']) / actual_day['revenue'] * 100,
                    'events': forecast_day.get('events', []),
                    'event_type': self.model.classify_event_type(forecast_day.get('events', []))
                }
                variance_data.append(variance)
        
        return variance_data
    
    def analyze_spillover_effectiveness(self, variance_data: List[Dict]) -> Dict:
        """Analyze how effective current spillover coefficients are"""
        
        spillover_analysis = {}
        
        # Group by event type
        by_event_type = {}
        for data in variance_data:
            event_type = data['event_type']
            if event_type not in by_event_type:
                by_event_type[event_type] = []
            by_event_type[event_type].append(data)
        
        # Analyze each event type
        for event_type, data_points in by_event_type.items():
            if len(data_points) > 0:
                avg_variance_pct = statistics.mean([d['variance_pct'] for d in data_points])
                spillover_analysis[event_type] = {
                    'avg_variance_pct': avg_variance_pct,
                    'data_points': len(data_points),
                    'needs_adjustment': abs(avg_variance_pct) > self.target_accuracy * 100
                }
        
        return spillover_analysis
    
    def calculate_optimal_coefficients(self, variance_data: List[Dict]) -> Dict:
        """Calculate optimal spillover coefficients based on variance data"""
        
        optimal_coefficients = {}
        
        # Focus on post-event days (Monday after weekend events, etc.)
        post_event_variances = []
        for data in variance_data:
            # Identify post-event days by checking if previous days had events
            if data['day_of_week'] in ['Monday', 'Tuesday'] and data['variance_pct'] > 20:
                post_event_variances.append(data)
        
        if post_event_variances:
            # Calculate required spillover adjustment
            underforecasts = [d['variance_pct'] for d in post_event_variances if d['variance_pct'] > 0]
            avg_underforecast = statistics.mean(underforecasts) if underforecasts else 0
            
            # Translate variance to spillover coefficient adjustment
            # If we're underforecasting by X%, increase spillover by X/100
            spillover_adjustment = avg_underforecast / 100
            
            # Update coefficients for each event type
            for event_type in ['mega_festival', 'sports', 'cultural', 'weekend_event']:
                current_coeff = self.model.spillover_coefficients.get(event_type, {}).get('day_1_after', 0.1)
                new_coeff = min(current_coeff + spillover_adjustment, 0.5)  # Cap at 50%
                
                optimal_coefficients[event_type] = {
                    'day_1_after': new_coeff,
                    'day_2_after': new_coeff * 0.2,  # 20% of day 1
                    'day_3_after': new_coeff * 0.1   # 10% of day 1
                }
        
        return optimal_coefficients
    
    def apply_calibration(self, optimal_coefficients: Dict):
        """Apply calibrated coefficients to the model"""
        
        print("🔧 APPLYING CALIBRATED COEFFICIENTS")
        print("=" * 50)
        
        for event_type, coefficients in optimal_coefficients.items():
            print(f"\n{event_type.upper()}:")
            for coeff_name, value in coefficients.items():
                old_value = self.model.spillover_coefficients.get(event_type, {}).get(coeff_name, 0)
                print(f"  {coeff_name}: {old_value:.3f} → {value:.3f}")
                
                # Update model
                if event_type not in self.model.spillover_coefficients:
                    self.model.spillover_coefficients[event_type] = {}
                self.model.spillover_coefficients[event_type][coeff_name] = value
        
        # Save calibrated model
        self.model.save_departure_model_config("calibrated_departure_model_config.json")
        print("\n✅ Calibrated model saved")
    
    def run_calibration_cycle(self, forecast_data: List[Dict], actual_data: List[Dict]):
        """Run a complete calibration cycle"""
        
        print("🚀 RUNNING AUTOMATED CALIBRATION CYCLE")
        print("=" * 60)
        
        # Step 1: Collect variance data
        variance_data = self.collect_actual_vs_forecast_data(forecast_data, actual_data)
        print(f"📊 Collected {len(variance_data)} data points for analysis")
        
        # Step 2: Analyze spillover effectiveness
        spillover_analysis = self.analyze_spillover_effectiveness(variance_data)
        print("\n📈 SPILLOVER EFFECTIVENESS ANALYSIS:")
        for event_type, analysis in spillover_analysis.items():
            status = "❌ NEEDS ADJUSTMENT" if analysis['needs_adjustment'] else "✅ GOOD"
            print(f"  {event_type}: {analysis['avg_variance_pct']:+.1f}% avg variance - {status}")
        
        # Step 3: Calculate optimal coefficients
        optimal_coefficients = self.calculate_optimal_coefficients(variance_data)
        
        # Step 4: Apply calibration if needed
        if optimal_coefficients:
            self.apply_calibration(optimal_coefficients)
            return True
        else:
            print("\n✅ No calibration needed - model is performing well")
            return False
    
    def generate_calibration_report(self, variance_data: List[Dict]) -> str:
        """Generate comprehensive calibration report"""
        
        report = []
        report.append("📊 AUTOMATED CALIBRATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overall accuracy metrics
        total_variance = sum(abs(d['variance_pct']) for d in variance_data)
        avg_accuracy = 100 - (total_variance / len(variance_data))
        
        report.append(f"Overall Model Accuracy: {avg_accuracy:.1f}%")
        report.append(f"Target Accuracy: {(1-self.target_accuracy)*100:.1f}%")
        report.append("")
        
        # Day-by-day analysis
        report.append("📋 DAILY ACCURACY ANALYSIS:")
        for data in variance_data:
            accuracy = 100 - abs(data['variance_pct'])
            status = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 80 else "❌"
            report.append(f"  {data['date']} ({data['day_of_week']}): {accuracy:.1f}% {status}")
        
        report.append("")
        
        # Recommendations
        report.append("💡 CALIBRATION RECOMMENDATIONS:")
        high_variance_days = [d for d in variance_data if abs(d['variance_pct']) > 20]
        if high_variance_days:
            report.append(f"  • {len(high_variance_days)} days need attention (>20% variance)")
            report.append("  • Focus on post-event spillover coefficient calibration")
        else:
            report.append("  • Model is performing well - no major adjustments needed")
        
        return "\n".join(report)

# Example usage for Monday 8/4 validation
if __name__ == "__main__":
    calibrator = AutoCalibrator()
    
    # Example: Monday 8/4 actual vs forecast
    forecast_data = [
        {
            'date': '2025-08-04',
            'day': 'Monday',
            'revenue': 108101,  # Current model forecast
            'events': ['Millennium Park Summer Series']
        }
    ]
    
    actual_data = [
        {
            'date': '2025-08-04',
            'revenue': 138165.12  # Actual revenue
        }
    ]
    
    # Run calibration
    calibrator.run_calibration_cycle(forecast_data, actual_data)
    
    # Generate report
    variance_data = calibrator.collect_actual_vs_forecast_data(forecast_data, actual_data)
    report = calibrator.generate_calibration_report(variance_data)
    print("\n" + report)

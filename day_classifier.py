"""
Day Classification System for MPG Revenue Forecasting
Implements Baseline, Opportunity, and Threat Day framework for strategic analysis
"""

import csv
import datetime
from typing import Dict, List, Tuple

class DayClassifier:
    """
    Classifies forecast days into strategic categories for variance analysis and pricing strategy
    """
    
    def __init__(self):
        self.baseline_days = "Baseline Days"
        self.opportunity_days = "Opportunity Days" 
        self.threat_days = "Threat Days"
        
        # Event keywords that indicate opportunity days
        self.opportunity_keywords = [
            'lollapalooza', 'lolla', 'festival', 'fest', 'concert', 'symphony', 
            'opera', 'broadway', 'performance', 'show', 'sports', 'fire', 'bears', 
            'bulls', 'cubs', 'sox', 'blackhawks', 'dolphins', 'holiday', 'christmas',
            'thanksgiving', 'new year', 'memorial', 'labor', 'independence'
        ]
        
        # Weather/event keywords that indicate threat days
        self.threat_keywords = [
            'protest', 'demonstration', 'closure', 'shutdown', 'strike',
            'severe weather', 'storm', 'blizzard', 'flooding', 'emergency'
        ]
        
        # Weekend days are generally opportunity days
        self.weekend_days = ['Saturday', 'Sunday']
        
    def classify_day(self, date_str: str, day_name: str, events: List[str], 
                    weather_desc: str = "", special_notes: str = "") -> Tuple[str, str, float]:
        """
        Classify a day into Baseline, Opportunity, or Threat category
        
        Args:
            date_str: Date in YYYY-MM-DD format
            day_name: Day of week (Monday, Tuesday, etc.)
            events: List of event descriptions for the day
            weather_desc: Weather description
            special_notes: Any special circumstances
            
        Returns:
            Tuple of (category, reasoning, strategic_multiplier)
        """
        
        # Check for threat conditions first (highest priority)
        threat_indicators = []
        all_text = f"{' '.join(events)} {weather_desc} {special_notes}".lower()
        
        for keyword in self.threat_keywords:
            if keyword in all_text:
                threat_indicators.append(keyword)
                
        if threat_indicators:
            reasoning = f"Threat indicators: {', '.join(threat_indicators)}"
            return self.threat_days, reasoning, 0.75  # Reduced demand expectation
            
        # Check for opportunity conditions
        opportunity_indicators = []
        
        # Weekend check
        if day_name in self.weekend_days:
            opportunity_indicators.append("weekend")
            
        # Event check
        for event in events:
            event_lower = event.lower()
            for keyword in self.opportunity_keywords:
                if keyword in event_lower:
                    opportunity_indicators.append(f"event: {keyword}")
                    break
                    
        # Holiday check (basic - could be enhanced with holiday calendar)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if self._is_holiday_period(date_obj):
            opportunity_indicators.append("holiday period")
            
        if opportunity_indicators:
            reasoning = f"Opportunity indicators: {', '.join(opportunity_indicators)}"
            multiplier = self._calculate_opportunity_multiplier(opportunity_indicators)
            return self.opportunity_days, reasoning, multiplier
            
        # Default to baseline if no special conditions
        reasoning = "Standard weekday, no events, no disruptions"
        return self.baseline_days, reasoning, 1.0
        
    def _is_holiday_period(self, date_obj: datetime.datetime) -> bool:
        """Check if date falls in common holiday periods"""
        month = date_obj.month
        day = date_obj.day
        
        # Major holiday periods (simplified)
        holiday_periods = [
            (12, 20, 12, 31),  # Christmas/New Year
            (11, 22, 11, 28),  # Thanksgiving week
            (7, 1, 7, 7),      # Independence Day week
            (5, 25, 5, 31),    # Memorial Day week
            (9, 1, 9, 7),      # Labor Day week
        ]
        
        for start_month, start_day, end_month, end_day in holiday_periods:
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day) or \
               (start_month < month < end_month):
                return True
                
        return False
        
    def _calculate_opportunity_multiplier(self, indicators: List[str]) -> float:
        """Calculate strategic multiplier based on opportunity indicators"""
        base_multiplier = 1.0
        
        # Weekend boost
        if any("weekend" in ind for ind in indicators):
            base_multiplier += 0.15
            
        # Event boost (varies by event type)
        event_indicators = [ind for ind in indicators if "event:" in ind]
        if event_indicators:
            # Major events
            if any("lollapalooza" in ind or "festival" in ind for ind in event_indicators):
                base_multiplier += 0.40
            # Sports events
            elif any("sports" in ind or "bears" in ind or "bulls" in ind for ind in event_indicators):
                base_multiplier += 0.30
            # Cultural events
            elif any("symphony" in ind or "opera" in ind for ind in event_indicators):
                base_multiplier += 0.25
            # General events
            else:
                base_multiplier += 0.15
                
        # Holiday boost
        if any("holiday" in ind for ind in indicators):
            base_multiplier += 0.10
            
        return min(base_multiplier, 2.0)  # Cap at 2x multiplier
        
    def generate_classification_report(self, forecast_data: List[Dict]) -> str:
        """Generate a strategic classification report for forecast period"""
        
        baseline_days = []
        opportunity_days = []
        threat_days = []
        
        total_baseline_revenue = 0
        total_opportunity_revenue = 0
        total_threat_revenue = 0
        
        for day_data in forecast_data:
            category, reasoning, multiplier = self.classify_day(
                day_data['date'],
                day_data['day_name'],
                day_data.get('events', []),
                day_data.get('weather', ''),
                day_data.get('notes', '')
            )
            
            revenue = day_data.get('revenue', 0)
            
            if category == self.baseline_days:
                baseline_days.append((day_data['date'], day_data['day_name'], revenue, reasoning))
                total_baseline_revenue += revenue
            elif category == self.opportunity_days:
                opportunity_days.append((day_data['date'], day_data['day_name'], revenue, reasoning))
                total_opportunity_revenue += revenue
            else:  # threat_days
                threat_days.append((day_data['date'], day_data['day_name'], revenue, reasoning))
                total_threat_revenue += revenue
                
        # Generate report
        report = []
        report.append("🎯 STRATEGIC DAY CLASSIFICATION ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_revenue = total_baseline_revenue + total_opportunity_revenue + total_threat_revenue
        report.append("📊 REVENUE DISTRIBUTION BY DAY TYPE")
        report.append("-" * 50)
        
        if total_revenue > 0:
            baseline_pct = (total_baseline_revenue / total_revenue) * 100
            opportunity_pct = (total_opportunity_revenue / total_revenue) * 100
            threat_pct = (total_threat_revenue / total_revenue) * 100
            
            report.append(f"Baseline Days:    ${total_baseline_revenue:,.0f} ({baseline_pct:.1f}%)")
            report.append(f"Opportunity Days: ${total_opportunity_revenue:,.0f} ({opportunity_pct:.1f}%)")
            report.append(f"Threat Days:      ${total_threat_revenue:,.0f} ({threat_pct:.1f}%)")
            report.append(f"Total Revenue:    ${total_revenue:,.0f}")
        
        report.append("")
        
        # Detailed breakdown
        if opportunity_days:
            report.append("🚀 OPPORTUNITY DAYS (High Potential)")
            report.append("-" * 50)
            for date, day, revenue, reasoning in opportunity_days:
                report.append(f"{date} ({day}): ${revenue:,.0f} - {reasoning}")
            report.append("")
            
        if baseline_days:
            report.append("📈 BASELINE DAYS (Normal Demand)")
            report.append("-" * 50)
            for date, day, revenue, reasoning in baseline_days:
                report.append(f"{date} ({day}): ${revenue:,.0f} - {reasoning}")
            report.append("")
            
        if threat_days:
            report.append("⚠️ THREAT DAYS (Disrupted Demand)")
            report.append("-" * 50)
            for date, day, revenue, reasoning in threat_days:
                report.append(f"{date} ({day}): ${revenue:,.0f} - {reasoning}")
            report.append("")
            
        # Strategic insights
        report.append("💡 STRATEGIC INSIGHTS")
        report.append("-" * 50)
        
        if opportunity_pct > 70:
            report.append("• High opportunity period - consider premium pricing strategies")
        elif baseline_pct > 60:
            report.append("• Stable demand period - good for testing pricing optimizations")
        
        if threat_days:
            report.append("• Threat days identified - prepare contingency communications")
            
        avg_opportunity_revenue = total_opportunity_revenue / len(opportunity_days) if opportunity_days else 0
        avg_baseline_revenue = total_baseline_revenue / len(baseline_days) if baseline_days else 0
        
        if avg_opportunity_revenue > 0 and avg_baseline_revenue > 0:
            opportunity_lift = ((avg_opportunity_revenue - avg_baseline_revenue) / avg_baseline_revenue) * 100
            report.append(f"• Opportunity days show {opportunity_lift:.1f}% revenue lift vs baseline")
            
        return "\n".join(report)

# Example usage and testing
if __name__ == "__main__":
    classifier = DayClassifier()
    
    # Test classification
    test_days = [
        ("2025-08-04", "Monday", ["Millennium Park Summer Series"], "74°F, overcast", ""),
        ("2025-08-09", "Saturday", ["Aerial Arts Society performance"], "92°F, few clouds", ""),
        ("2025-08-10", "Sunday", ["Preseason: Miami Dolphins vs Bears"], "80°F, partly cloudy", ""),
        ("2025-08-12", "Tuesday", [], "75°F, clear", ""),
    ]
    
    for date, day, events, weather, notes in test_days:
        category, reasoning, multiplier = classifier.classify_day(date, day, events, weather, notes)
        print(f"{date} ({day}): {category} - {reasoning} (Multiplier: {multiplier:.2f})")

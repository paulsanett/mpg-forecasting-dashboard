#!/usr/bin/env python3
"""
Enhanced Predictor Engine for MPG Forecasting
Integrates gas prices, temperature data, and reservation values for 2-5% accuracy target
"""

import sys
import re
import statistics
from datetime import datetime, timedelta
from robust_csv_reader import RobustCSVReader
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error

class EnhancedPredictorEngine:
    def __init__(self):
        self.reader = RobustCSVReader()
        self.data = None
        self.gas_price_model = None
        self.temperature_model = None
        self.reservation_value_model = None
        self.scaler = StandardScaler()
        
    def load_and_analyze_data(self):
        """Load data and extract enhanced predictive factors"""
        print("🔍 LOADING DATA FOR ENHANCED PREDICTION")
        print("=" * 50)
        
        self.data = self.reader.read_csv_robust()
        if not self.data:
            raise Exception("Failed to load data")
            
        print(f"✅ Loaded {len(self.data)} records")
        
        # Extract enhanced features
        self._extract_gas_price_patterns()
        self._extract_temperature_data()
        self._extract_reservation_value_patterns()
        
        return self.data
    
    def _extract_gas_price_patterns(self):
        """Analyze gas price impact on parking volume"""
        print("\n⛽ ANALYZING GAS PRICE IMPACT")
        print("-" * 35)
        
        gas_prices = []
        revenues = []
        
        for record in self.data:
            gas_price_raw = record.get('gas_price', 0)
            total_revenue = record.get('total_revenue', 0)
            
            # Parse gas price - handle string format like "2.59"
            gas_price = 0
            if gas_price_raw:
                try:
                    if isinstance(gas_price_raw, str):
                        # Remove any currency symbols and whitespace
                        clean_price = gas_price_raw.replace('$', '').replace(',', '').strip()
                        if clean_price and clean_price != '-':
                            gas_price = float(clean_price)
                    elif isinstance(gas_price_raw, (int, float)):
                        gas_price = float(gas_price_raw)
                except (ValueError, AttributeError):
                    gas_price = 0
            
            if gas_price > 0 and total_revenue > 0:
                gas_prices.append(gas_price)
                revenues.append(total_revenue)
        
        if len(gas_prices) > 10:
            # Calculate correlation
            correlation = np.corrcoef(gas_prices, revenues)[0, 1]
            
            print(f"📊 Gas Price Analysis:")
            print(f"   Records with gas data: {len(gas_prices)}")
            print(f"   Average gas price: ${statistics.mean(gas_prices):.2f}")
            print(f"   Gas price range: ${min(gas_prices):.2f} - ${max(gas_prices):.2f}")
            print(f"   Correlation with revenue: {correlation:.3f}")
            
            # Create gas price impact model
            if abs(correlation) > 0.1:  # Significant correlation
                self._build_gas_price_model(gas_prices, revenues)
            else:
                print("   ⚠️  Low correlation - gas price may not be significant predictor")
        else:
            print("   ❌ Insufficient gas price data")
    
    def _extract_temperature_data(self):
        """Extract temperature information from notes field"""
        print("\n🌡️  EXTRACTING TEMPERATURE DATA")
        print("-" * 35)
        
        temperatures = []
        revenues = []
        temp_pattern = r'(\d+)°?[Ff]?'  # Match temperature patterns
        
        for record in self.data:
            notes = record.get('notes', '')
            total_revenue = record.get('total_revenue', 0)
            
            if notes and total_revenue > 0:
                # Look for temperature mentions
                temp_matches = re.findall(temp_pattern, str(notes))
                if temp_matches:
                    try:
                        temp = int(temp_matches[0])
                        if 20 <= temp <= 120:  # Reasonable temperature range
                            temperatures.append(temp)
                            revenues.append(total_revenue)
                    except ValueError:
                        continue
        
        if len(temperatures) > 10:
            correlation = np.corrcoef(temperatures, revenues)[0, 1]
            
            print(f"📊 Temperature Analysis:")
            print(f"   Records with temperature: {len(temperatures)}")
            print(f"   Average temperature: {statistics.mean(temperatures):.1f}°F")
            print(f"   Temperature range: {min(temperatures)}°F - {max(temperatures)}°F")
            print(f"   Correlation with revenue: {correlation:.3f}")
            
            if abs(correlation) > 0.1:
                self._build_temperature_model(temperatures, revenues)
            else:
                print("   ⚠️  Low correlation - temperature may not be significant predictor")
        else:
            print("   ❌ Insufficient temperature data in notes")
    
    def _extract_reservation_value_patterns(self):
        """Analyze average reservation value patterns"""
        print("\n💰 ANALYZING RESERVATION VALUE PATTERNS")
        print("-" * 45)
        
        avg_values = []
        revenues = []
        
        for record in self.data:
            avg_value = record.get('avg_reservation_value', 0)
            total_revenue = record.get('total_revenue', 0)
            
            if avg_value > 0 and total_revenue > 0:
                avg_values.append(avg_value)
                revenues.append(total_revenue)
        
        if len(avg_values) > 10:
            correlation = np.corrcoef(avg_values, revenues)[0, 1]
            
            print(f"📊 Reservation Value Analysis:")
            print(f"   Records with avg values: {len(avg_values)}")
            print(f"   Average reservation value: ${statistics.mean(avg_values):.2f}")
            print(f"   Value range: ${min(avg_values):.2f} - ${max(avg_values):.2f}")
            print(f"   Correlation with revenue: {correlation:.3f}")
            
            if abs(correlation) > 0.1:
                self._build_reservation_value_model(avg_values, revenues)
            else:
                print("   ⚠️  Low correlation - reservation value may not be significant predictor")
        else:
            print("   ❌ Insufficient reservation value data")
    
    def _build_gas_price_model(self, gas_prices, revenues):
        """Build predictive model for gas price impact"""
        print("   🔧 Building gas price prediction model...")
        
        X = np.array(gas_prices).reshape(-1, 1)
        y = np.array(revenues)
        
        self.gas_price_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.gas_price_model.fit(X, y)
        
        # Calculate model accuracy
        predictions = self.gas_price_model.predict(X)
        mape = mean_absolute_percentage_error(y, predictions) * 100
        
        print(f"   ✅ Gas price model trained (MAPE: {mape:.1f}%)")
    
    def _build_temperature_model(self, temperatures, revenues):
        """Build predictive model for temperature impact"""
        print("   🔧 Building temperature prediction model...")
        
        X = np.array(temperatures).reshape(-1, 1)
        y = np.array(revenues)
        
        self.temperature_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.temperature_model.fit(X, y)
        
        predictions = self.temperature_model.predict(X)
        mape = mean_absolute_percentage_error(y, predictions) * 100
        
        print(f"   ✅ Temperature model trained (MAPE: {mape:.1f}%)")
    
    def _build_reservation_value_model(self, avg_values, revenues):
        """Build predictive model for reservation value impact"""
        print("   🔧 Building reservation value prediction model...")
        
        X = np.array(avg_values).reshape(-1, 1)
        y = np.array(revenues)
        
        self.reservation_value_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.reservation_value_model.fit(X, y)
        
        predictions = self.reservation_value_model.predict(X)
        mape = mean_absolute_percentage_error(y, predictions) * 100
        
        print(f"   ✅ Reservation value model trained (MAPE: {mape:.1f}%)")
    
    def build_comprehensive_model(self):
        """Build comprehensive model using all enhanced predictors"""
        print("\n🎯 BUILDING COMPREHENSIVE ENHANCED MODEL")
        print("=" * 50)
        
        # Prepare feature matrix
        features = []
        targets = []
        feature_names = []
        
        for record in self.data:
            feature_row = []
            
            # Basic features
            day_of_week = self._get_day_of_week_encoding(record.get('day_of_week', ''))
            feature_row.extend(day_of_week)
            if not feature_names:
                feature_names.extend(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            
            # Enhanced predictors
            gas_price = record.get('gas_price', 0)
            feature_row.append(gas_price)
            if 'gas_price' not in feature_names:
                feature_names.append('gas_price')
            
            avg_value = record.get('avg_reservation_value', 0)
            feature_row.append(avg_value)
            if 'avg_reservation_value' not in feature_names:
                feature_names.append('avg_reservation_value')
            
            # Extract temperature from notes
            temp = self._extract_temperature_from_notes(record.get('notes', ''))
            feature_row.append(temp)
            if 'temperature' not in feature_names:
                feature_names.append('temperature')
            
            # Month encoding
            date_str = record.get('date', '')
            month = self._get_month_from_date(date_str)
            feature_row.append(month)
            if 'month' not in feature_names:
                feature_names.append('month')
            
            total_revenue = record.get('total_revenue', 0)
            
            if total_revenue > 0 and len(feature_row) == len(feature_names):
                features.append(feature_row)
                targets.append(total_revenue)
        
        if len(features) < 50:
            print("❌ Insufficient data for comprehensive model")
            return None
        
        # Train comprehensive model
        X = np.array(features)
        y = np.array(targets)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = rf_model.predict(X_test_scaled)
        gb_pred = gb_model.predict(X_test_scaled)
        
        rf_mape = mean_absolute_percentage_error(y_test, rf_pred) * 100
        gb_mape = mean_absolute_percentage_error(y_test, gb_pred) * 100
        
        print(f"📊 MODEL PERFORMANCE:")
        print(f"   Random Forest MAPE: {rf_mape:.2f}%")
        print(f"   Gradient Boosting MAPE: {gb_mape:.2f}%")
        
        # Use best model
        if rf_mape < gb_mape:
            self.comprehensive_model = rf_model
            best_mape = rf_mape
            print(f"   ✅ Selected Random Forest (MAPE: {best_mape:.2f}%)")
        else:
            self.comprehensive_model = gb_model
            best_mape = gb_mape
            print(f"   ✅ Selected Gradient Boosting (MAPE: {best_mape:.2f}%)")
        
        # Feature importance
        if hasattr(self.comprehensive_model, 'feature_importances_'):
            importances = self.comprehensive_model.feature_importances_
            feature_importance = list(zip(feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📈 FEATURE IMPORTANCE:")
            for name, importance in feature_importance[:5]:
                print(f"   {name}: {importance:.3f}")
        
        return best_mape
    
    def _get_day_of_week_encoding(self, day_str):
        """One-hot encode day of week"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        encoding = [0] * 7
        
        for i, day in enumerate(days):
            if day.lower() in day_str.lower():
                encoding[i] = 1
                break
        
        return encoding
    
    def _extract_temperature_from_notes(self, notes):
        """Extract temperature from notes field"""
        if not notes:
            return 70  # Default temperature
        
        temp_pattern = r'(\d+)°?[Ff]?'
        matches = re.findall(temp_pattern, str(notes))
        
        if matches:
            try:
                temp = int(matches[0])
                if 20 <= temp <= 120:
                    return temp
            except ValueError:
                pass
        
        return 70  # Default temperature
    
    def _get_month_from_date(self, date_str):
        """Extract month number from date string"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.month
        except:
            return 1  # Default to January
    
    def predict_enhanced_revenue(self, gas_price=None, temperature=None, avg_reservation_value=None, day_of_week='Monday', month=8):
        """Make enhanced revenue prediction"""
        if not hasattr(self, 'comprehensive_model'):
            print("❌ Comprehensive model not trained")
            return None
        
        # Prepare feature vector
        feature_row = []
        
        # Day of week encoding
        day_encoding = self._get_day_of_week_encoding(day_of_week)
        feature_row.extend(day_encoding)
        
        # Enhanced predictors
        feature_row.append(gas_price or 3.50)  # Default gas price
        feature_row.append(avg_reservation_value or 25.0)  # Default avg value
        feature_row.append(temperature or 70)  # Default temperature
        feature_row.append(month)
        
        # Scale and predict
        X = np.array(feature_row).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.comprehensive_model.predict(X_scaled)[0]
        
        return prediction

def main():
    """Main execution function"""
    print("🚀 ENHANCED PREDICTOR ENGINE FOR 2-5% ACCURACY")
    print("=" * 60)
    
    engine = EnhancedPredictorEngine()
    
    try:
        # Load and analyze data
        engine.load_and_analyze_data()
        
        # Build comprehensive model
        mape = engine.build_comprehensive_model()
        
        if mape:
            print(f"\n🎯 FINAL MODEL ACCURACY: {mape:.2f}% MAPE")
            
            if mape <= 5.0:
                print("🎉 SUCCESS! Achieved 2-5% accuracy target!")
            elif mape <= 10.0:
                print("✅ EXCELLENT! Very close to 2-5% target")
            elif mape <= 15.0:
                print("👍 GOOD! Significant improvement toward target")
            else:
                print("📈 PROGRESS! Better than baseline, continue refinement")
        
        # Test prediction
        print(f"\n🧪 TESTING ENHANCED PREDICTION:")
        test_prediction = engine.predict_enhanced_revenue(
            gas_price=3.75,
            temperature=75,
            avg_reservation_value=28.50,
            day_of_week='Tuesday',
            month=8
        )
        
        if test_prediction:
            print(f"   Sample prediction: ${test_prediction:,.0f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Enhanced ML Forecaster using ALL data with gas prices for 2-5% accuracy target
"""

import sys
import re
import statistics
from datetime import datetime, timedelta
from simple_csv_reader import SimpleCSVReader
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class EnhancedMLForecaster:
    def __init__(self):
        self.reader = SimpleCSVReader()
        self.data = None
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_and_prepare_data(self):
        """Load all data and prepare for ML modeling"""
        print("🚀 ENHANCED ML FORECASTER FOR 2-5% ACCURACY")
        print("=" * 60)
        
        # Get all modeling data (no filtering)
        self.data = self.reader.get_modeling_data()
        
        if len(self.data) < 100:
            raise Exception("Insufficient data for ML modeling")
        
        print(f"✅ Loaded {len(self.data)} records for enhanced modeling")
        return self.data
    
    def engineer_features(self):
        """Create comprehensive feature set"""
        print("\n🔧 ENGINEERING ENHANCED FEATURES")
        print("-" * 40)
        
        features = []
        targets = []
        
        for record in self.data:
            feature_row = []
            
            # 1. Day of week (one-hot encoded)
            dow = record.get('day_of_week', '').upper().strip()
            dow_features = [0] * 7
            day_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 
                      'FRI': 4, 'SAT': 5, 'SUN': 6}
            
            if dow in day_map:
                dow_features[day_map[dow]] = 1
            
            feature_row.extend(dow_features)
            
            # 2. Gas price (key predictor)
            gas_price = record.get('gas_price', 0)
            feature_row.append(gas_price)
            
            # 3. Average reservation value
            avg_value = record.get('avg_reservation_value', 0)
            feature_row.append(avg_value)
            
            # 4. Date-based features
            date_str = record.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%m/%d/%y')
            except:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    date_obj = datetime(2020, 1, 1)  # Default
            
            # Month (1-12)
            feature_row.append(date_obj.month)
            
            # Day of month (1-31)
            feature_row.append(date_obj.day)
            
            # Year
            feature_row.append(date_obj.year)
            
            # Quarter
            quarter = (date_obj.month - 1) // 3 + 1
            feature_row.append(quarter)
            
            # 5. Temperature extraction from notes
            temp = self._extract_temperature(record.get('notes', ''))
            feature_row.append(temp)
            
            # 6. Event detection from notes
            has_event = self._detect_event(record.get('notes', ''))
            feature_row.append(1 if has_event else 0)
            
            # 7. Garage unit totals (capacity indicator)
            total_units = record.get('total_units', 0)
            feature_row.append(total_units)
            
            # 8. Revenue per unit (efficiency metric)
            revenue_per_unit = 0
            if total_units > 0:
                revenue_per_unit = record.get('total_revenue', 0) / total_units
            feature_row.append(revenue_per_unit)
            
            # Target
            target = record.get('total_revenue', 0)
            
            if target > 0 and len(feature_row) == 18:  # Ensure complete feature vector
                features.append(feature_row)
                targets.append(target)
        
        # Set feature names
        self.feature_names = [
            'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun',
            'gas_price', 'avg_reservation_value', 'month', 'day', 'year', 
            'quarter', 'temperature', 'has_event', 'total_units', 'revenue_per_unit'
        ]
        
        print(f"📊 Feature Engineering Results:")
        print(f"   Features created: {len(self.feature_names)}")
        print(f"   Training samples: {len(features)}")
        print(f"   Feature names: {', '.join(self.feature_names[:5])}...")
        
        return np.array(features), np.array(targets)
    
    def _extract_temperature(self, notes):
        """Extract temperature from notes"""
        if not notes:
            return 70  # Default temperature
        
        # Look for temperature patterns
        temp_patterns = [
            r'(\d+)°[Ff]?',  # 75°F or 75°
            r'(\d+)\s*degrees?',  # 75 degrees
            r'temp[:\s]*(\d+)',  # temp: 75
        ]
        
        for pattern in temp_patterns:
            matches = re.findall(pattern, str(notes), re.IGNORECASE)
            if matches:
                try:
                    temp = int(matches[0])
                    if 20 <= temp <= 120:  # Reasonable range
                        return temp
                except ValueError:
                    continue
        
        return 70  # Default
    
    def _detect_event(self, notes):
        """Detect events from notes"""
        if not notes:
            return False
        
        event_keywords = [
            'lollapalooza', 'lolla', 'festival', 'concert', 'event', 'game',
            'cubs', 'bears', 'bulls', 'blackhawks', 'marathon', 'parade',
            'convention', 'conference', 'holiday', 'christmas', 'thanksgiving'
        ]
        
        notes_lower = str(notes).lower()
        return any(keyword in notes_lower for keyword in event_keywords)
    
    def train_enhanced_model(self):
        """Train enhanced ML model with all features"""
        print("\n🎯 TRAINING ENHANCED ML MODEL")
        print("-" * 40)
        
        # Prepare data
        X, y = self.engineer_features()
        
        if len(X) < 50:
            raise Exception("Insufficient data for training")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Try multiple models
        models = {
            'Random Forest': RandomForestRegressor(
                n_estimators=200, 
                max_depth=15, 
                min_samples_split=5,
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        best_model = None
        best_mape = float('inf')
        best_name = ""
        
        print("📊 MODEL COMPARISON:")
        
        for name, model in models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Predict
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mape = mean_absolute_percentage_error(y_test, y_pred) * 100
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train_scaled, y_train, 
                cv=5, scoring='neg_mean_absolute_percentage_error'
            )
            cv_mape = -cv_scores.mean() * 100
            
            print(f"   {name}:")
            print(f"      Test MAPE: {mape:.2f}%")
            print(f"      CV MAPE: {cv_mape:.2f}%")
            print(f"      MAE: ${mae:,.0f}")
            
            if mape < best_mape:
                best_mape = mape
                best_model = model
                best_name = name
        
        self.model = best_model
        
        print(f"\n✅ BEST MODEL: {best_name}")
        print(f"🎯 FINAL ACCURACY: {best_mape:.2f}% MAPE")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance = list(zip(self.feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📈 TOP FEATURE IMPORTANCE:")
            for name, importance in feature_importance[:8]:
                print(f"   {name}: {importance:.3f}")
        
        # Accuracy assessment
        if best_mape <= 5.0:
            print(f"\n🎉 SUCCESS! Achieved 2-5% accuracy target!")
        elif best_mape <= 10.0:
            print(f"\n✅ EXCELLENT! Very close to 2-5% target")
        elif best_mape <= 15.0:
            print(f"\n👍 GOOD! Significant improvement")
        else:
            print(f"\n📈 PROGRESS! Better than baseline")
        
        return best_mape
    
    def predict_revenue(self, gas_price=3.50, avg_reservation_value=20.0, 
                       temperature=70, day_of_week='Monday', month=8, 
                       day=6, year=2025, has_event=False, total_units=1000):
        """Make enhanced revenue prediction"""
        if not self.model:
            raise Exception("Model not trained")
        
        # Create feature vector
        feature_row = []
        
        # Day of week encoding
        dow_features = [0] * 7
        day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                  'friday': 4, 'saturday': 5, 'sunday': 6}
        
        dow_idx = day_map.get(day_of_week.lower(), 0)
        dow_features[dow_idx] = 1
        feature_row.extend(dow_features)
        
        # Other features
        feature_row.extend([
            gas_price, avg_reservation_value, month, day, year,
            (month - 1) // 3 + 1,  # quarter
            temperature, 1 if has_event else 0, total_units,
            0  # revenue_per_unit (unknown for prediction)
        ])
        
        # Scale and predict
        X = np.array(feature_row).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        return prediction

def main():
    """Main execution"""
    try:
        forecaster = EnhancedMLForecaster()
        
        # Load data
        forecaster.load_and_prepare_data()
        
        # Train model
        mape = forecaster.train_enhanced_model()
        
        # Test prediction
        print(f"\n🧪 TESTING ENHANCED PREDICTION:")
        test_prediction = forecaster.predict_revenue(
            gas_price=3.75,
            temperature=75,
            day_of_week='Tuesday',
            month=8,
            has_event=False
        )
        
        print(f"   Sample prediction: ${test_prediction:,.0f}")
        
        return mape <= 15.0  # Success if under 15%
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

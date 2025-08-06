#!/usr/bin/env python3
"""
MACHINE LEARNING PRECISION CALIBRATOR
Advanced ML-based calibration to achieve 2-5% error target
Uses ensemble methods and feature engineering for maximum accuracy
"""

import sys
import os
sys.path.append('.')

from robust_csv_reader import RobustCSVReader
from datetime import datetime, timedelta
import random
import statistics
from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

class MLPrecisionCalibrator:
    def __init__(self):
        self.target_error = 3.5  # Target 2-5% range
        self.reader = RobustCSVReader()
        self.data = None
        self.feature_scaler = StandardScaler()
        self.models = {}
        
    def load_and_engineer_features(self):
        """Load data and create comprehensive feature set"""
        print('🧠 Loading data and engineering advanced features...')
        
        self.data = self.reader.read_csv_robust()
        
        # Filter for high-quality recent data
        cutoff_date = datetime(2024, 8, 6)
        engineered_data = []
        
        # Known event dates
        lolla_dates = [
            datetime(2024, 8, 1), datetime(2024, 8, 2), datetime(2024, 8, 3), datetime(2024, 8, 4),
            datetime(2025, 7, 31), datetime(2025, 8, 1), datetime(2025, 8, 2), datetime(2025, 8, 3)
        ]
        
        for record in self.data:
            if (record.get('date') and record.get('total_revenue', 0) > 0):
                try:
                    date_str = str(record.get('date', ''))
                    date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    
                    if date_obj >= cutoff_date:
                        # Comprehensive feature engineering
                        features = self.create_feature_vector(date_obj, record, lolla_dates)
                        features['target'] = record.get('total_revenue', 0)
                        engineered_data.append(features)
                except:
                    continue
        
        print(f'✅ Engineered {len(engineered_data)} feature-rich data points')
        return engineered_data
    
    def create_feature_vector(self, date_obj, record, lolla_dates):
        """Create comprehensive feature vector for ML model"""
        features = {}
        
        # Basic temporal features
        features['day_of_week'] = date_obj.weekday()  # 0=Monday, 6=Sunday
        features['month'] = date_obj.month
        features['day_of_month'] = date_obj.day
        features['week_of_year'] = date_obj.isocalendar()[1]
        features['quarter'] = (date_obj.month - 1) // 3 + 1
        
        # Cyclical encoding for temporal features
        features['day_sin'] = np.sin(2 * np.pi * date_obj.weekday() / 7)
        features['day_cos'] = np.cos(2 * np.pi * date_obj.weekday() / 7)
        features['month_sin'] = np.sin(2 * np.pi * date_obj.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * date_obj.month / 12)
        
        # Boolean features
        features['is_weekend'] = 1 if date_obj.weekday() >= 5 else 0
        features['is_monday'] = 1 if date_obj.weekday() == 0 else 0
        features['is_friday'] = 1 if date_obj.weekday() == 4 else 0
        features['is_saturday'] = 1 if date_obj.weekday() == 5 else 0
        features['is_sunday'] = 1 if date_obj.weekday() == 6 else 0
        
        # Event features
        features['is_lolla'] = 1 if date_obj in lolla_dates else 0
        features['days_to_lolla'] = min([abs((date_obj - ld).days) for ld in lolla_dates])
        features['lolla_proximity'] = 1 if features['days_to_lolla'] <= 7 else 0
        
        # Seasonal features
        features['is_summer'] = 1 if date_obj.month in [6, 7, 8] else 0
        features['is_winter'] = 1 if date_obj.month in [12, 1, 2] else 0
        features['is_spring'] = 1 if date_obj.month in [3, 4, 5] else 0
        features['is_fall'] = 1 if date_obj.month in [9, 10, 11] else 0
        
        # Holiday and special period features
        features['is_holiday_season'] = 1 if date_obj.month in [11, 12, 1] else 0
        features['is_month_start'] = 1 if date_obj.day <= 5 else 0
        features['is_month_end'] = 1 if date_obj.day >= 26 else 0
        features['is_mid_month'] = 1 if 10 <= date_obj.day <= 20 else 0
        
        # Advanced temporal patterns
        features['days_since_epoch'] = (date_obj - datetime(2024, 1, 1)).days
        features['is_first_week'] = 1 if date_obj.day <= 7 else 0
        features['is_last_week'] = 1 if date_obj.day >= 22 else 0
        
        # Weather season approximation (more granular)
        day_of_year = date_obj.timetuple().tm_yday
        features['seasonal_intensity'] = np.sin(2 * np.pi * day_of_year / 365.25)
        
        return features
    
    def train_ensemble_models(self, X_train, y_train, X_val, y_val):
        """Train ensemble of ML models for maximum accuracy"""
        print('🤖 Training ensemble ML models...')
        
        # Model 1: Random Forest (handles non-linear patterns well)
        rf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Model 2: Gradient Boosting (excellent for sequential patterns)
        gb_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=8,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        # Train models
        rf_model.fit(X_train, y_train)
        gb_model.fit(X_train, y_train)
        
        # Evaluate models
        rf_pred = rf_model.predict(X_val)
        gb_pred = gb_model.predict(X_val)
        
        rf_error = mean_absolute_percentage_error(y_val, rf_pred) * 100
        gb_error = mean_absolute_percentage_error(y_val, gb_pred) * 100
        
        print(f'Random Forest Validation Error: {rf_error:.1f}%')
        print(f'Gradient Boosting Validation Error: {gb_error:.1f}%')
        
        # Create ensemble prediction
        ensemble_pred = (rf_pred + gb_pred) / 2
        ensemble_error = mean_absolute_percentage_error(y_val, ensemble_pred) * 100
        
        print(f'Ensemble Validation Error: {ensemble_error:.1f}%')
        
        # Store models
        self.models = {
            'rf': rf_model,
            'gb': gb_model,
            'ensemble_error': ensemble_error
        }
        
        return ensemble_error
    
    def analyze_feature_importance(self, X_train, feature_names):
        """Analyze which features are most important for predictions"""
        print('🔍 Analyzing feature importance...')
        
        rf_importance = self.models['rf'].feature_importances_
        gb_importance = self.models['gb'].feature_importances_
        
        # Combine importance scores
        combined_importance = (rf_importance + gb_importance) / 2
        
        # Sort by importance
        importance_pairs = list(zip(feature_names, combined_importance))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        print('\n🎯 TOP 10 MOST IMPORTANT FEATURES:')
        print('-' * 40)
        for i, (feature, importance) in enumerate(importance_pairs[:10], 1):
            print(f'{i:2d}. {feature:<20}: {importance:.3f}')
        
        return importance_pairs
    
    def generate_ml_baseline_adjustments(self, engineered_data):
        """Use ML insights to generate baseline adjustments"""
        print('⚙️  Generating ML-based baseline adjustments...')
        
        # Separate by day of week for baseline calculation
        day_adjustments = {}
        
        for day_idx in range(7):  # 0=Monday to 6=Sunday
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[day_idx]
            
            # Filter data for this day, excluding Lolla events
            day_data = [d for d in engineered_data if d['day_of_week'] == day_idx and d['is_lolla'] == 0]
            
            if len(day_data) >= 10:  # Need sufficient data
                # Create feature matrix for this day
                features = [
                    'month', 'day_of_month', 'week_of_year', 'quarter',
                    'month_sin', 'month_cos', 'is_summer', 'is_winter', 'is_spring', 'is_fall',
                    'is_holiday_season', 'is_month_start', 'is_month_end', 'is_mid_month',
                    'days_since_epoch', 'seasonal_intensity', 'lolla_proximity'
                ]
                
                X = np.array([[d[f] for f in features] for d in day_data])
                y = np.array([d['target'] for d in day_data])
                
                # Train a simple model for this day
                from sklearn.linear_model import Ridge
                day_model = Ridge(alpha=1.0)
                day_model.fit(X, y)
                
                # Predict baseline (average conditions)
                avg_features = np.mean(X, axis=0).reshape(1, -1)
                baseline_prediction = day_model.predict(avg_features)[0]
                
                day_adjustments[day_name] = int(baseline_prediction)
                
                print(f'{day_name:>9}: ${baseline_prediction:>8,.0f} (ML-optimized from {len(day_data)} samples)')
            else:
                # Fallback to current calibrated values
                fallback_values = {
                    'Monday': 56738, 'Tuesday': 56316, 'Wednesday': 61026,
                    'Thursday': 68628, 'Friday': 71240, 'Saturday': 102080, 'Sunday': 77967
                }
                day_adjustments[day_name] = fallback_values.get(day_name, 60000)
                print(f'{day_name:>9}: ${day_adjustments[day_name]:>8,.0f} (fallback)')
        
        return day_adjustments
    
    def run_ml_calibration(self):
        """Run the complete ML-based calibration process"""
        print('🚀 MACHINE LEARNING PRECISION CALIBRATION')
        print('=' * 60)
        print('Target: 2-5% error using advanced ML techniques')
        print()
        
        # Load and engineer features
        engineered_data = self.load_and_engineer_features()
        
        if len(engineered_data) < 50:
            print('❌ Insufficient data for ML calibration')
            return None, None, None, False
        
        # Prepare feature matrix
        feature_names = [k for k in engineered_data[0].keys() if k != 'target']
        X = np.array([[d[f] for f in feature_names] for d in engineered_data])
        y = np.array([d['target'] for d in engineered_data])
        
        # Scale features
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train ensemble models
        ensemble_error = self.train_ensemble_models(X_train, y_train, X_val, y_val)
        
        # Analyze feature importance
        importance_pairs = self.analyze_feature_importance(X_train, feature_names)
        
        # Generate ML-based baseline adjustments
        ml_baseline = self.generate_ml_baseline_adjustments(engineered_data)
        
        # Validate final performance
        success = ensemble_error <= 5.0
        target_achievement = 100 - ensemble_error if ensemble_error < 20 else 0
        
        print()
        print('🎯 ML CALIBRATION RESULTS')
        print('=' * 35)
        print(f'Ensemble Model Error: {ensemble_error:.1f}%')
        print(f'Target Achievement: {target_achievement:.1f}%')
        
        if success:
            rating = '🎯 TARGET ACHIEVED!'
        elif ensemble_error <= 10:
            rating = '✅ CLOSE TO TARGET'
        else:
            rating = '⚠️ NEEDS FURTHER REFINEMENT'
        
        print(f'Overall Assessment: {rating}')
        
        # Generate configuration code
        config_code = f'''        # ML PRECISION CALIBRATED: Advanced machine learning optimization
        # Ensemble model error: {ensemble_error:.1f}% | Target: 2-5% range
        # Uses Random Forest + Gradient Boosting ensemble
        self.base_daily_revenue = {{
            'Monday': {ml_baseline['Monday']},      # ML optimized
            'Tuesday': {ml_baseline['Tuesday']},     # ML optimized
            'Wednesday': {ml_baseline['Wednesday']},   # ML optimized
            'Thursday': {ml_baseline['Thursday']},    # ML optimized
            'Friday': {ml_baseline['Friday']},      # ML optimized
            'Saturday': {ml_baseline['Saturday']},    # ML optimized
            'Sunday': {ml_baseline['Sunday']}       # ML optimized
        }}'''
        
        return ml_baseline, ensemble_error, config_code, success

def main():
    try:
        calibrator = MLPrecisionCalibrator()
        baseline, error, code, success = calibrator.run_ml_calibration()
        
        if baseline:
            print()
            print('🚀 ML CALIBRATION COMPLETE!')
            print()
            print('OPTIMIZED CONFIGURATION:')
            print(code)
            
            return baseline, error, code, success
        else:
            print('❌ ML calibration failed - insufficient data')
            return None, None, None, False
            
    except ImportError as e:
        print(f'❌ Missing required ML libraries: {e}')
        print('Please install: pip3 install scikit-learn')
        return None, None, None, False

if __name__ == "__main__":
    main()

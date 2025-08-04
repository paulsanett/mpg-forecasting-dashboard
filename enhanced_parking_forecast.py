import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

class EnhancedParkingForecast:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.df = None
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.train_data = None
        self.test_data = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.target_column = 'revenue'
        
    def load_data(self, data_path=None):
        """Load parking garage revenue data"""
        if data_path:
            self.data_path = data_path
        if not self.data_path:
            raise ValueError("Please provide a data path")
            
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
            
        # Try different file formats
        try:
            if self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            elif self.data_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.data_path)
            else:
                # Try CSV first, then Excel
                try:
                    self.df = pd.read_csv(self.data_path)
                except:
                    self.df = pd.read_excel(self.data_path)
        except Exception as e:
            raise ValueError(f"Could not read file: {str(e)}")
            
        print(f"Data loaded successfully. Shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        return self.df
        
    def preprocess_data(self, date_column=None, revenue_column=None):
        """Preprocess and clean the data"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        print("Starting data preprocessing...")
        
        # Find date column
        if date_column:
            date_col = date_column
        else:
            date_cols = [col for col in self.df.columns if any(word in col.lower() for word in ['date', 'time', 'day'])]
            if date_cols:
                date_col = date_cols[0]
            else:
                raise ValueError("No date column found. Please specify date_column parameter.")
        
        # Find revenue column
        if revenue_column:
            self.target_column = revenue_column
        else:
            revenue_cols = [col for col in self.df.columns if any(word in col.lower() for word in ['revenue', 'income', 'sales', 'amount'])]
            if revenue_cols:
                self.target_column = revenue_cols[0]
            else:
                raise ValueError("No revenue column found. Please specify revenue_column parameter.")
        
        # Convert date column to datetime
        self.df[date_col] = pd.to_datetime(self.df[date_col])
        self.df.set_index(date_col, inplace=True)
        self.df.sort_index(inplace=True)
        
        # Handle missing values
        print(f"Missing values before cleaning: {self.df.isnull().sum().sum()}")
        self.df.fillna(method='ffill', inplace=True)
        self.df.fillna(method='bfill', inplace=True)
        
        # Create time-based features
        self.df['day_of_week'] = self.df.index.dayofweek
        self.df['month'] = self.df.index.month
        self.df['quarter'] = self.df.index.quarter
        self.df['year'] = self.df.index.year
        self.df['day_of_month'] = self.df.index.day
        self.df['week_of_year'] = self.df.index.isocalendar().week
        
        # Weekend indicator
        self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)
        
        # Holiday indicators (basic US holidays)
        self.df['is_holiday'] = 0
        for year in self.df.index.year.unique():
            holidays = [
                f'{year}-01-01',  # New Year
                f'{year}-07-04',  # Independence Day
                f'{year}-12-25',  # Christmas
            ]
            for holiday in holidays:
                if holiday in self.df.index.strftime('%Y-%m-%d').values:
                    self.df.loc[holiday, 'is_holiday'] = 1
        
        # Lag features for revenue
        if self.target_column in self.df.columns:
            self.df['revenue_lag_1'] = self.df[self.target_column].shift(1)
            self.df['revenue_lag_7'] = self.df[self.target_column].shift(7)
            self.df['revenue_lag_30'] = self.df[self.target_column].shift(30)
            
            # Rolling averages
            self.df['revenue_ma_7'] = self.df[self.target_column].rolling(window=7).mean()
            self.df['revenue_ma_30'] = self.df[self.target_column].rolling(window=30).mean()
        
        # Handle event notes if they exist
        event_cols = [col for col in self.df.columns if 'event' in col.lower() or 'note' in col.lower()]
        if event_cols:
            print(f"Found event columns: {event_cols}")
            self.df['has_event'] = 0
            for col in event_cols:
                self.df['has_event'] += (~self.df[col].isna()).astype(int)
            self.df['has_event'] = (self.df['has_event'] > 0).astype(int)
        
        # Remove rows with NaN values created by lag features
        self.df.dropna(inplace=True)
        
        print(f"Data preprocessing completed. Final shape: {self.df.shape}")
        print(f"Target column: {self.target_column}")
        
        return self.df
        
    def analyze_seasonality(self, plot=True):
        """Analyze seasonal patterns in the data"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        print("Analyzing seasonality patterns...")
        
        # Basic statistics
        print(f"\nRevenue Statistics:")
        print(f"Mean: ${self.df[self.target_column].mean():.2f}")
        print(f"Std: ${self.df[self.target_column].std():.2f}")
        print(f"Min: ${self.df[self.target_column].min():.2f}")
        print(f"Max: ${self.df[self.target_column].max():.2f}")
        
        # Day of week patterns
        dow_avg = self.df.groupby('day_of_week')[self.target_column].mean()
        print(f"\nAverage Revenue by Day of Week:")
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            print(f"{day}: ${dow_avg.iloc[i]:.2f}")
        
        # Monthly patterns
        monthly_avg = self.df.groupby('month')[self.target_column].mean()
        print(f"\nAverage Revenue by Month:")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for i, month in enumerate(months, 1):
            if i in monthly_avg.index:
                print(f"{month}: ${monthly_avg.loc[i]:.2f}")
        
        if plot:
            # Create comprehensive plots
            fig, axes = plt.subplots(2, 2, figsize=(20, 12))
            
            # Time series plot
            axes[0, 0].plot(self.df.index, self.df[self.target_column])
            axes[0, 0].set_title('Revenue Over Time')
            axes[0, 0].set_ylabel('Revenue ($)')
            axes[0, 0].grid(True)
            
            # Day of week pattern
            dow_avg.plot(kind='bar', ax=axes[0, 1])
            axes[0, 1].set_title('Average Revenue by Day of Week')
            axes[0, 1].set_ylabel('Revenue ($)')
            axes[0, 1].set_xticklabels(days, rotation=45)
            
            # Monthly pattern
            monthly_avg.plot(kind='bar', ax=axes[1, 0])
            axes[1, 0].set_title('Average Revenue by Month')
            axes[1, 0].set_ylabel('Revenue ($)')
            axes[1, 0].set_xticklabels([months[i-1] for i in monthly_avg.index], rotation=45)
            
            # Revenue distribution
            axes[1, 1].hist(self.df[self.target_column], bins=50, alpha=0.7)
            axes[1, 1].set_title('Revenue Distribution')
            axes[1, 1].set_xlabel('Revenue ($)')
            axes[1, 1].set_ylabel('Frequency')
            
            plt.tight_layout()
            plt.show()
            
    def train_models(self, test_size=0.2):
        """Train multiple forecasting models and select the best one"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        print("Training multiple forecasting models...")
        
        # Prepare features - only numeric columns
        feature_cols = [col for col in self.df.columns if col != self.target_column and self.df[col].dtype in ['int64', 'float64', 'int32', 'float32']]
        self.feature_columns = feature_cols
        
        print(f"Selected features: {feature_cols}")
        
        # Split data chronologically
        split_idx = int(len(self.df) * (1 - test_size))
        self.train_data = self.df.iloc[:split_idx]
        self.test_data = self.df.iloc[split_idx:]
        
        X_train = self.train_data[feature_cols]
        y_train = self.train_data[self.target_column]
        X_test = self.test_data[feature_cols]
        y_test = self.test_data[self.target_column]
        
        # Scale features for models that benefit from it
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models to try
        models_to_try = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        results = {}
        
        # Train and evaluate each model
        for name, model in models_to_try.items():
            print(f"Training {name}...")
            
            try:
                # Use scaled data for Linear Regression, original for tree-based models
                if 'Linear' in name:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Calculate MAPE (Mean Absolute Percentage Error)
                mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
                
                results[name] = {
                    'model': model,
                    'mse': mse,
                    'rmse': rmse,
                    'mae': mae,
                    'r2': r2,
                    'mape': mape,
                    'predictions': y_pred
                }
                
                print(f"{name} - RMSE: ${rmse:.2f}, R²: {r2:.3f}, MAPE: {mape:.2f}%")
                
            except Exception as e:
                print(f"Error training {name}: {str(e)}")
        
        # Select best model based on RMSE
        if results:
            best_model_name = min(results.keys(), key=lambda x: results[x]['rmse'])
            self.best_model = results[best_model_name]['model']
            self.best_model_name = best_model_name
            self.models = results
            
            print(f"\nBest model: {best_model_name}")
            print(f"Best RMSE: ${results[best_model_name]['rmse']:.2f}")
            print(f"Best MAPE: {results[best_model_name]['mape']:.2f}%")
            
            return results
        else:
            raise ValueError("No models were successfully trained")
            
    def make_forecast(self, n_periods=30, model_name=None):
        """Make future revenue forecasts"""
        if not self.models and not self.best_model:
            raise ValueError("No models trained. Please train models first.")
            
        # Select model to use
        if model_name and model_name in self.models:
            model = self.models[model_name]['model']
            selected_model_name = model_name
        else:
            model = self.best_model
            selected_model_name = self.best_model_name
            
        print(f"Making forecast with {selected_model_name} for {n_periods} periods...")
        
        # Create future dates
        last_date = self.df.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=n_periods, freq='D')
        
        # Create future dataframe with features
        future_df = pd.DataFrame(index=future_dates)
        
        # Add time-based features
        future_df['day_of_week'] = future_df.index.dayofweek
        future_df['month'] = future_df.index.month
        future_df['quarter'] = future_df.index.quarter
        future_df['year'] = future_df.index.year
        future_df['day_of_month'] = future_df.index.day
        future_df['week_of_year'] = future_df.index.isocalendar().week
        future_df['is_weekend'] = (future_df['day_of_week'] >= 5).astype(int)
        future_df['is_holiday'] = 0  # Simplified - could be enhanced
        
        # For lag features, use the last known values and predictions
        last_revenue = self.df[self.target_column].iloc[-1]
        last_7_avg = self.df[self.target_column].tail(7).mean()
        last_30_avg = self.df[self.target_column].tail(30).mean()
        
        future_df['revenue_lag_1'] = last_revenue
        future_df['revenue_lag_7'] = last_7_avg
        future_df['revenue_lag_30'] = last_30_avg
        future_df['revenue_ma_7'] = last_7_avg
        future_df['revenue_ma_30'] = last_30_avg
        
        # Add event indicator (simplified)
        if 'has_event' in self.feature_columns:
            future_df['has_event'] = 0  # Assume no events unless specified
        
        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in future_df.columns:
                future_df[col] = 0  # Default value
        
        # Reorder columns to match training data
        future_df = future_df[self.feature_columns]
        
        # Make predictions
        if 'Linear' in selected_model_name:
            future_scaled = self.scaler.transform(future_df)
            predictions = model.predict(future_scaled)
        else:
            predictions = model.predict(future_df)
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_revenue': predictions,
            'model_used': selected_model_name
        })
        
        # Add confidence intervals (simplified approach)
        if selected_model_name in self.models:
            test_errors = self.models[selected_model_name]['predictions'] - self.test_data[self.target_column]
            error_std = np.std(test_errors)
            forecast_df['lower_bound'] = predictions - 1.96 * error_std
            forecast_df['upper_bound'] = predictions + 1.96 * error_std
        
        print(f"Forecast completed. Average predicted revenue: ${predictions.mean():.2f}")
        return forecast_df
        
    def plot_forecast(self, forecast_df, show_confidence=True):
        """Plot historical and forecasted revenue"""
        plt.figure(figsize=(18, 10))
        
        # Plot historical data
        plt.subplot(2, 1, 1)
        plt.plot(self.df.index, self.df[self.target_column], label='Historical Revenue', color='blue', alpha=0.7)
        plt.plot(forecast_df['date'], forecast_df['predicted_revenue'], 
                label=f'Forecasted Revenue ({forecast_df["model_used"].iloc[0]})', 
                linestyle='--', color='red', linewidth=2)
        
        # Add confidence intervals if available
        if show_confidence and 'lower_bound' in forecast_df.columns:
            plt.fill_between(forecast_df['date'], 
                           forecast_df['lower_bound'], 
                           forecast_df['upper_bound'], 
                           alpha=0.3, color='red', label='95% Confidence Interval')
        
        plt.title('Parking Garage Revenue Forecast', fontsize=16)
        plt.xlabel('Date')
        plt.ylabel('Revenue ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot recent data + forecast for better visibility
        plt.subplot(2, 1, 2)
        recent_data = self.df.tail(60)  # Last 60 days
        plt.plot(recent_data.index, recent_data[self.target_column], 
                label='Recent Historical Revenue', color='blue', alpha=0.7)
        plt.plot(forecast_df['date'], forecast_df['predicted_revenue'], 
                label=f'Forecasted Revenue ({forecast_df["model_used"].iloc[0]})', 
                linestyle='--', color='red', linewidth=2)
        
        if show_confidence and 'lower_bound' in forecast_df.columns:
            plt.fill_between(forecast_df['date'], 
                           forecast_df['lower_bound'], 
                           forecast_df['upper_bound'], 
                           alpha=0.3, color='red', label='95% Confidence Interval')
        
        plt.title('Recent Data + Forecast (Zoomed View)', fontsize=14)
        plt.xlabel('Date')
        plt.ylabel('Revenue ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    def get_model_performance(self):
        """Get performance metrics for all trained models"""
        if not self.models:
            print("No models trained yet.")
            return None
            
        performance_df = pd.DataFrame({
            'Model': list(self.models.keys()),
            'RMSE': [self.models[model]['rmse'] for model in self.models],
            'MAE': [self.models[model]['mae'] for model in self.models],
            'R²': [self.models[model]['r2'] for model in self.models],
            'MAPE (%)': [self.models[model]['mape'] for model in self.models]
        })
        
        performance_df = performance_df.sort_values('RMSE')
        return performance_df

if __name__ == "__main__":
    # Example usage
    print("Enhanced Parking Revenue Forecasting Model")
    print("=" * 50)
    
    # Create instance
    forecast_model = EnhancedParkingForecast()
    
    # Instructions for use
    print("\nTo use this model:")
    print("1. Load your data: forecast_model.load_data('path_to_your_data.csv')")
    print("2. Preprocess data: forecast_model.preprocess_data()")
    print("3. Analyze patterns: forecast_model.analyze_seasonality()")
    print("4. Train models: forecast_model.train_models()")
    print("5. Make forecast: forecast = forecast_model.make_forecast(n_periods=30)")
    print("6. Plot results: forecast_model.plot_forecast(forecast)")
    print("7. Check performance: forecast_model.get_model_performance()")

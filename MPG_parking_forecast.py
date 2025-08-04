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
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

class ParkingGarageForecast:
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
            
        self.df = pd.read_csv(self.data_path)
        return self.df
        
    def preprocess_data(self):
        """Preprocess and clean the data"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        # Convert date column to datetime if it exists
        date_cols = [col for col in self.df.columns if 'date' in col.lower()]
        if date_cols:
            self.df[date_cols[0]] = pd.to_datetime(self.df[date_cols[0]])
            self.df.set_index(date_cols[0], inplace=True)
            
        # Fill missing values
        self.df.fillna(method='ffill', inplace=True)
        
        # Create additional features
        self.df['day_of_week'] = self.df.index.dayofweek
        self.df['month'] = self.df.index.month
        self.df['hour'] = self.df.index.hour
        
        return self.df
        
    def analyze_seasonality(self):
        """Analyze seasonal patterns in the data"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        # Decompose time series to analyze trend and seasonality
        result = seasonal_decompose(self.df['revenue'], model='additive', period=7)
        
        # Plot decomposition
        plt.figure(figsize=(15, 8))
        result.plot()
        plt.title('Seasonal Decomposition of Revenue')
        plt.show()
        
    def train_model(self, test_size=0.2):
        """Train the forecasting model"""
        if self.df is None:
            raise ValueError("Data not loaded. Please load data first.")
            
        # Split data
        self.train_data, self.test_data = train_test_split(self.df, test_size=test_size, shuffle=False)
        
        # Feature engineering
        X_train = self.train_data.drop(['revenue'], axis=1)
        y_train = self.train_data['revenue']
        
        X_test = self.test_data.drop(['revenue'], axis=1)
        y_test = self.test_data['revenue']
        
        # Train model (using a simple linear regression as a baseline)
        from sklearn.linear_model import LinearRegression
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:\nMSE: {mse:.2f}\nR²: {r2:.2f}")
        return self.model
        
    def make_forecast(self, n_periods=30):
        """Make future revenue forecasts"""
        if self.model is None:
            raise ValueError("Model not trained. Please train model first.")
            
        # Create future dates
        last_date = self.df.index[-1]
        future_dates = pd.date_range(start=last_date, periods=n_periods, freq='D')[1:]
        
        # Create future data frame with features
        future_df = pd.DataFrame(index=future_dates)
        future_df['day_of_week'] = future_df.index.dayofweek
        future_df['month'] = future_df.index.month
        future_df['hour'] = future_df.index.hour
        
        # Make predictions
        predictions = self.model.predict(future_df)
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_revenue': predictions
        })
        
        return forecast_df
        
    def plot_forecast(self, forecast_df):
        """Plot historical and forecasted revenue"""
        plt.figure(figsize=(15, 8))
        plt.plot(self.df.index, self.df['revenue'], label='Historical Revenue')
        plt.plot(forecast_df['date'], forecast_df['predicted_revenue'], label='Forecasted Revenue', linestyle='--')
        plt.title('Parking Garage Revenue Forecast')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    # Example usage
    try:
        # Create instance of the forecast model
        forecast_model = ParkingGarageForecast()
        
        # Load your data (replace with your actual data path)
        # forecast_model.load_data('path_to_your_data.csv')
        
        # Preprocess data
        # df = forecast_model.preprocess_data()
        
        # Analyze seasonality
        # forecast_model.analyze_seasonality()
        
        # Train model
        # model = forecast_model.train_model()
        
        # Make forecast
        # forecast = forecast_model.make_forecast(n_periods=30)
        
        # Plot forecast
        # forecast_model.plot_forecast(forecast)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

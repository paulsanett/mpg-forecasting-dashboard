#!/bin/bash

echo "🚗 Setting up Parking Revenue Forecasting Environment"
echo "=" * 60

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "✅ Homebrew already installed"
fi

# Install Python 3.11 via Homebrew (more reliable than system Python)
echo "🐍 Installing Python 3.11..."
brew install python@3.11

# Create a virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv parking_forecast_env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source parking_forecast_env/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "📚 Installing required packages..."
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install scikit-learn>=1.3.0
pip install statsmodels>=0.14.0
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install python-dotenv>=1.0.0

echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "source parking_forecast_env/bin/activate"
echo ""
echo "To run the parking analysis:"
echo "python run_parking_analysis.py"

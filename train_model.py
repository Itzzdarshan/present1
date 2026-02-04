import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

def train_live_model():
    print("🌐 Downloading live Gold data from Yahoo Finance...")
    # GC=F is the ticker for Gold Futures
    df = yf.download("GC=F", period="10y", interval="1d")
    
    # Flatten MultiIndex columns if they exist
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 1. CLEANING: Remove rows where data is missing
    df = df.dropna()

    # Prepare Data
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # Feature Engineering
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    
    # 2. TARGET: Tomorrow's Close
    df['Target'] = df['Close'].shift(-1)
    
    # 3. FINAL CLEAN: Drop the very last row because its 'Target' will be NaN
    # (Since we don't know tomorrow's price yet!)
    df_clean = df.dropna()

    # Select Features
    features = ['Close', 'Volume', 'Open', 'High', 'Low', 'Year', 'Month', 'Day', 'DayOfWeek']
    X = df_clean[features]
    y = df_clean['Target']

    # Train
    print(f"🧠 Training on {len(X)} days of cleaned market data...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save
    with open('gold_model_live.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("✅ Live Model Saved as 'gold_model_live.pkl'")

if __name__ == "__main__":
    train_live_model()
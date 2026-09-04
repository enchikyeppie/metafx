import os
import requests
import pandas as pd
import yfinance as yf

# Load credentials securely from environment variables (GitHub Secrets)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Ticker for Gold on Yahoo Finance
SYMBOL = "GC=F"

def send_telegram_alert(message):
    if not TOKEN or not CHAT_ID:
        print("Error: Telegram TOKEN or CHAT_ID environment variables are missing.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_xauusd_ma5():
    print(f"Checking 15m market data for {SYMBOL}...")
    
    # Fetch intraday data using 15-minute interval
    df = yf.download(tickers=SYMBOL, period="5d", interval="15m", progress=False)
    
    if df.empty:
        print("Failed to fetch data.")
        return

    # Clean up multi-index columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Calculate MA 5 using Close prices
    df['MA5'] = df['Close'].rolling(window=5).mean()
    
    latest_time = df.index[-1]
    current_price = float(df['Close'].iloc[-1])
    current_ma5 = float(df['MA5'].iloc[-1])
    
    print(f"Time: {latest_time} | Price: {current_price:.2f} | MA5: {current_ma5:.2f}")

    # Gold tolerance for a 15m touch
    tolerance = 0.60 

    # Check if price is touching MA5
    if abs(current_price - current_ma5) <= tolerance:
        alert_msg = (
            f"🚨 XAUUSD 15M MA5 TOUCH ALERT! 🚨\n"
            f"Candle Time: {latest_time}\n"
            f"Price: {current_price:.2f}\n"
            f"MA5 Level: {current_ma5:.2f}\n"
            f"Check chart for ReEntry setup!"
        )
        send_telegram_alert(alert_msg)
        print("15m Alert sent to Telegram!")
    else:
        print("Price is outside the touch zone. No alert needed.")

if __name__ == "__main__":
    check_xauusd_ma5()

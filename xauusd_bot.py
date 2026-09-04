import time
import requests
import pandas as pd
import yfinance as yf

# Telegram Configuration
TOKEN = 7998035588:AAEG0PSVLU7QiWO5ApaWRjRO8SmIm8zoZXg
CHAT_ID = 59267319

# Ticker for Gold on Yahoo Finance
SYMBOL = "GC=F"

# Keep track of the last alerted candle timestamp to prevent duplicate pings
last_alerted_time = None

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_xauusd_ma5():
    global last_alerted_time
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
    
    # Get the latest closed or active candle timestamp and values
    latest_time = df.index[-1]
    current_price = float(df['Close'].iloc[-1])
    current_ma5 = float(df['MA5'].iloc[-1])
    
    print(f"Time: {latest_time} | Price: {current_price:.2f} | MA5: {current_ma5:.2f}")

    # Gold tolerance for a 15m touch (around 0.50 to 0.80 dollars)
    tolerance = 0.60 

    # Check if price is touching MA5 and we haven't already alerted for this specific 15m candle
    if abs(current_price - current_ma5) <= tolerance:
        if last_alerted_time != latest_time:
            alert_msg = (
                f"🚨 XAUUSD 15M MA5 TOUCH ALERT! 🚨\n"
                f"Candle Time: {latest_time}\n"
                f"Price: {current_price:.2f}\n"
                f"MA5 Level: {current_ma5:.2f}\n"
                f"Check chart for ReEntry setup!"
            )
            send_telegram_alert(alert_msg)
            print("15m Alert sent to Telegram!")
            
            # Lock this candle timestamp so it doesn't repeat alerts for the same bar
            last_alerted_time = latest_time
        else:
            print("Already alerted for this 15m candle. Waiting for the next one.")

# Main Loop: Runs every 60 seconds to check if price has entered the zone
if __name__ == "__main__":
    print("XAUUSD 15m BBMA MA5 Bot Started...")
    while True:
        try:
            check_xauusd_ma5()
        except Exception as e:
            print(f"Error in loop: {e}")
        
        # Sleep for 60 seconds before re-checking
        time.sleep(60)
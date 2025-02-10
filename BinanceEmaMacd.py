import requests
import pandas as pd
import time
import smtplib
from email.mime.text import MIMEText

# Binance API URL
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# Binance API Key
API_KEY = "Br2WAi6ZFK9czcpCciyz4jCn9Fy0wiAqzL7P0XpB4aTdoPAGXFcjl8tLnIYMm70f"

# Trading Pairs
DEFAULT_PAIRS = ["XRPUSDT", "BTCUSDT", "SUIUSDT"]

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "meetvanodiya18@gmail.com"
EMAIL_PASSWORD = "ksafubvtbkkaaqmk"
EMAIL_RECEIVERS = ["meetvanodiya18@gmail.com", "kalpitcrypto@gmail.com", "tirthpatelhii@gmail.com", "agolavishwa@gmail.com","arthpatel571@gmail.com"]

# Trading Settings
ENTRY_PRICE = None
TRADE_TYPE = None  # 'BUY' or 'SELL'

# Function to send email alerts
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(EMAIL_RECEIVERS)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())
        server.quit()
        print("\U0001F4E7 Email alert sent!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# Fetch historical candle data using API Key
def fetch_candle_data(symbol, interval="15m", limit=500):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    headers = {"X-MBX-APIKEY": API_KEY}  # Added API Key in headers
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if not data or "code" in data:
        print(f"❌ Failed to fetch data for {symbol}")
        return None
    
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "trades", "taker_base", "taker_quote", "ignore"])
    df = df[["time", "open", "high", "low", "close", "volume"]].astype(float)
    return df

# Calculate Moving Averages (MA 9, 21)
def calculate_ma(df, short=9, long=21):
    df['MA9'] = df['close'].rolling(window=short).mean()
    df['MA21'] = df['close'].rolling(window=long).mean()
    return df

# Calculate MACD
def calculate_macd(df):
    short_ema = df['close'].ewm(span=12, adjust=False).mean()
    long_ema = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

# Generate Buy/Sell Signals
def generate_signals(df, pair):
    global ENTRY_PRICE, TRADE_TYPE
    if df is None or df.shape[0] < 21:
        return "WAIT"
    
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    price = latest['close']
    signal = "HOLD"
    email_subject = None
    email_body = None
    
    # Generate BUY signal
    if latest['MA9'] > latest['MA21'] and previous['MA9'] <= previous['MA21'] and latest['MACD'] > latest['Signal']:
        if TRADE_TYPE != "BUY":
            signal = "BUY"
            ENTRY_PRICE = price
            TRADE_TYPE = "BUY"
            email_subject = f"📢 BUY Alert for {pair}!"
            email_body = f"🔹 Pair: {pair}\n📊 Price: {price:.4f} USDT\n📈 MA9: {latest['MA9']:.4f} USDT\n📉 MA21: {latest['MA21']:.4f} USDT\n📊 MACD: {latest['MACD']:.4f}\n📈 Signal Line: {latest['Signal']:.4f}\n🚀 Trade Signal: BUY ✅"
    
    # Generate SELL signal
    elif latest['MA9'] < latest['MA21'] and previous['MA9'] >= previous['MA21'] and latest['MACD'] < latest['Signal']:
        if TRADE_TYPE != "SELL":
            signal = "SELL"
            ENTRY_PRICE = price
            TRADE_TYPE = "SELL"
            email_subject = f"📢 SELL Alert for {pair}!"
            email_body = f"🔹 Pair: {pair}\n📊 Price: {price:.4f} USDT\n📈 MA9: {latest['MA9']:.4f} USDT\n📉 MA21: {latest['MA21']:.4f} USDT\n📊 MACD: {latest['MACD']:.4f}\n📈 Signal Line: {latest['Signal']:.4f}\n❌ Trade Signal: SELL"
    
    if email_subject and email_body:
        send_email(email_subject, email_body)
    
    return signal

# Main loop
def main():
    print("\n🔄 Fetching real-time market data...\n")
    
    while True:
        for pair in DEFAULT_PAIRS:
            df = fetch_candle_data(pair)
            if df is not None:
                df = calculate_ma(df)
                df = calculate_macd(df)
                signal = generate_signals(df, pair)
                print(f"\n📊 {pair} Live Price: {df.iloc[-1]['close']:.4f} USDT")
                print(f"📢 Trade Signal: {signal}")
        time.sleep(1)  # Fetch every minute

if __name__ == "__main__":
    main()

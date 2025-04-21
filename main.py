import yfinance as yf
import pandas as pd
import numpy as np

def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    df['TR'] = df['High'] - df['Low']
    df['Volatility'] = df['TR'].rolling(window=5).mean()
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_suggestion(symbol="BTC-USD", period_days=3):
    df = yf.download(symbol, period=f"{period_days + 30}d")  # buffer ekliyoruz
    df = calculate_indicators(df)

    recent = df.tail(period_days)
    current_price = recent['Close'].iloc[-1]
    rsi = recent['RSI'].iloc[-1]
    ema20 = recent['EMA20'].iloc[-1]
    ema50 = recent['EMA50'].iloc[-1]
    support = recent['Low'].min()

    suggestion = "Hold"
    rationale = []

    if rsi < 35:
        rationale.append("RSI düşük (aşırı satım) → Alım sinyali")
    if current_price < ema20 and current_price < ema50:
        rationale.append("Fiyat EMA'ların altında → Dipte olabilir")
    if current_price <= support * 1.01:
        rationale.append("Fiyat destek seviyesine çok yakın")

    if len(rationale) >= 2:
        suggestion = "Buy"

    return {
        "symbol": symbol,
        "period_days": period_days,
        "current_price": round(current_price, 2),
        "suggested_entry": round(current_price * 0.995, 2),
        "expected_exit": round(current_price * 1.025, 2),
        "estimated_profit_pct": round(2.5, 2),
        "suggestion": suggestion,
        "rationale": rationale
    }

# Kullanım:
print(get_suggestion("BTC-USD", period_days=3))
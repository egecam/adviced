import yfinance as yf
import pandas as pd
import numpy as np

def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    df['TR'] = df['High'] - df['Low']
    df['Volatility'] = df['TR'].rolling(window=5).mean()
    return df

def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain_initial = gain.iloc[1:period+1].mean()
    avg_loss_initial = loss.iloc[1:period+1].mean()

    avg_gain = pd.Series(index=series.index, dtype='float64')
    avg_loss = pd.Series(index=series.index, dtype='float64')

    avg_gain.iloc[period] = avg_gain_initial
    avg_loss.iloc[period] = avg_loss_initial

    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_suggestion(symbol="BTC-USD", period_days=3):
    buffer_days = 100
    total_days = max(period_days, buffer_days)
    df = yf.download(symbol, period=f"{total_days + 50}d")

    if df.empty:
        print(f"Uyarı: {symbol} için veri indirilemedi. Öneri oluşturulamıyor.")
        return {"symbol": symbol, "period_days": period_days, "error": "Veri indirilemedi"}

    df = calculate_indicators(df)

    df.dropna(inplace=True)

    if df.empty:
        print(f"Uyarı: {symbol} için NaN değerleri kaldırıldıktan sonra yeterli veri kalmadı.")
        return {"symbol": symbol, "period_days": period_days, "error": "Göstergeler için yeterli veri yok"}

    actual_period_days = min(period_days, len(df))
    if actual_period_days == 0:
         print(f"Uyarı: {symbol} için NaN temizliği sonrası veri kalmadı.")
         return {"symbol": symbol, "period_days": period_days, "error": "NaN temizliği sonrası veri yok"}

    recent = df.tail(actual_period_days)

    if recent.empty:
         print(f"Uyarı: {symbol} için son periyot verisi bulunamadı.")
         return {"symbol": symbol, "period_days": period_days, "error": "Son periyot verisi yok"}

    current_price = recent['Close'].iloc[-1].item()
    rsi = recent['RSI'].iloc[-1].item()
    ema20 = recent['EMA20'].iloc[-1].item()
    ema50 = recent['EMA50'].iloc[-1].item()
    support = recent['Low'].min().item() if isinstance(recent['Low'].min(), pd.Series) else recent['Low'].min()

    if pd.isna(current_price) or pd.isna(rsi) or pd.isna(ema20) or pd.isna(ema50):
        print(f"Uyarı: {symbol} için son gösterge değerlerinde NaN bulundu.")
        return {"symbol": symbol, "period_days": period_days, "error": "Gösterge değerlerinde NaN var"}

    suggestion = "Hold"
    rationale = []

    if rsi < 35:
        rationale.append(f"RSI düşük ({rsi:.2f}, < 35) → Alım sinyali")
    if current_price < ema20 and current_price < ema50:
        rationale.append(f"Fiyat ({current_price:.2f}) EMA20 ({ema20:.2f}) ve EMA50'nin ({ema50:.2f}) altında → Dipte olabilir")
    if current_price <= support * 1.01:
        rationale.append(f"Fiyat ({current_price:.2f}) destek seviyesine ({support:.2f}) çok yakın")

    if len(rationale) >= 2:
        suggestion = "Buy"

    return {
        "symbol": symbol,
        "period_days": period_days,
        "current_price": round(current_price, 2),
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "support_level": round(support, 2),
        "suggested_entry": round(current_price * 0.995, 2),
        "expected_exit": round(current_price * 1.025, 2),
        "estimated_profit_pct": round(2.5, 2),
        "suggestion": suggestion,
        "rationale": rationale if rationale else ["Belirgin bir sinyal yok."]
    }

# Kullanım:
print(get_suggestion("BTC-USDT", period_days=3))
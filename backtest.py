import yfinance as yf
import pandas as pd
from main import calculate_indicators, compute_rsi  # Mevcut fonksiyonlarını kullanacağız

def backtest_strategy(symbol="BTC-USD", start="2022-01-01", end="2024-04-21", period_days=3):
    df = yf.download(symbol, start=start, end=end)
    df = calculate_indicators(df)
    df = df.dropna()
    
    results = []

    for i in range(len(df) - period_days):
        current_row = df.iloc[i]
        next_rows = df.iloc[i+1:i+1+period_days]

        # Skalar değerlere dönüştür
        current_price = current_row['Close']
        rsi = current_row['RSI']
        ema20 = current_row['EMA20']
        ema50 = current_row['EMA50']
        support = df['Low'].iloc[max(0, i-5):i+1].min()

        # Eğer bunlar hala Series ise, item() ile skalar yap
        if isinstance(current_price, pd.Series): current_price = current_price.item()
        if isinstance(rsi, pd.Series): rsi = rsi.item()
        if isinstance(ema20, pd.Series): ema20 = ema20.item()
        if isinstance(ema50, pd.Series): ema50 = ema50.item()
        if isinstance(support, pd.Series): support = support.item()

        rationale = []
        suggestion = "Hold"

        if rsi < 35:
            rationale.append("RSI düşük")
        if current_price < ema20 and current_price < ema50:
            rationale.append("EMA'ların altında")
        if current_price <= support * 1.01:
            rationale.append("Destek yakin")

        if len(rationale) >= 2:
            suggestion = "Buy"

        # Kar hesaplama - bunları da skalar değerlere dönüştürelim
        max_future_price = next_rows['High'].max()
        min_future_price = next_rows['Low'].min()
        final_price = next_rows['Close'].iloc[-1]

        # Eğer bunlar hala Series ise, item() ile skalar yap
        if isinstance(max_future_price, pd.Series): max_future_price = max_future_price.item()
        if isinstance(min_future_price, pd.Series): min_future_price = min_future_price.item()
        if isinstance(final_price, pd.Series): final_price = final_price.item()

        entry = current_price
        target = entry * 1.025
        stop = entry * 0.98

        pnl = final_price - entry
        hit_tp = max_future_price >= target
        hit_sl = min_future_price <= stop
        outcome = "Neutral"
        if hit_tp:
            outcome = "TP"
        elif hit_sl:
            outcome = "SL"
        elif pnl > 0:
            outcome = "Gain"
        elif pnl < 0:
            outcome = "Loss"

        results.append({
            "date": current_row.name.strftime("%Y-%m-%d"),
            "price": round(entry, 2),
            "suggestion": suggestion,
            "rationale_count": len(rationale),
            "rationale": ", ".join(rationale),
            "final_price": round(final_price, 2),
            "target": round(target, 2),
            "stop": round(stop, 2),
            "outcome": outcome,
            "pnl_pct": round((final_price - entry) / entry * 100, 2)
        })

    df_result = pd.DataFrame(results)
    df_result.to_csv("backtest_results.csv", index=False)
    print("✅ Backtest tamamlandı. Sonuçlar `backtest_results.csv` dosyasına kaydedildi.")


def analyze_backtest(file="backtest_results.csv"):
    df = pd.read_csv(file)
    buy_df = df[df["suggestion"] == "Buy"]

    result = {
        "Total Trades": len(df),
        "Buy Signals": len(buy_df),
        "TP": (buy_df["outcome"] == "TP").sum(),
        "SL": (buy_df["outcome"] == "SL").sum(),
        "Gain": (buy_df["outcome"] == "Gain").sum(),
        "Loss": (buy_df["outcome"] == "Loss").sum(),
        "Avg PnL %": round(buy_df["pnl_pct"].mean(), 2)
    }

    result["Success Rate"] = round((result["TP"] + result["Gain"]) / result["Buy Signals"] * 100, 2)
    result["Fail Rate"] = round((result["SL"] + result["Loss"]) / result["Buy Signals"] * 100, 2)

    return result


if __name__ == "__main__":
    backtest_strategy()
    analyze_backtest()
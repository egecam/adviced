tp_range = [1.5, 2.0, 2.5, 3.0]  # yüzde olarak
sl_range = [1.0, 1.5, 2.0, 2.5]

results = []
for tp in tp_range:
    for sl in sl_range:
        # Her alım sinyali için kar/zarar hesapla
        df = pd.read_csv("backtest_results.csv")
        buy_df = df[df["suggestion"] == "Buy"].copy()
        buy_df["tp_price"] = buy_df["price"] * (1 + tp / 100)
        buy_df["sl_price"] = buy_df["price"] * (1 - sl / 100)

        hits_tp = buy_df["final_price"] >= buy_df["tp_price"]
        hits_sl = buy_df["final_price"] <= buy_df["sl_price"]

        success = hits_tp.sum()
        fail = hits_sl.sum()
        total = len(buy_df)
        avg_pnl = ((buy_df["final_price"] - buy_df["price"]) / buy_df["price"]).mean() * 100

        results.append({
            "tp%": tp,
            "sl%": sl,
            "success_rate": round(success / total * 100, 2),
            "fail_rate": round(fail / total * 100, 2),
            "avg_pnl%": round(avg_pnl, 2)
        })

pd.DataFrame(results).sort_values("success_rate", ascending=False)
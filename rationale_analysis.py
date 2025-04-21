import pandas as pd

df = pd.read_csv("backtest_results.csv")
buy_signals = df[df["suggestion"] == "Buy"].copy()

# Rationale içinden sadece açıklamaları al
buy_signals["rationale_clean"] = buy_signals["rationale"].str.replace(" → .*", "", regex=True).str.strip()

# Grupla ve istatistik çıkar
rationale_stats = (
    buy_signals.groupby(["rationale_clean", "outcome"])
    .size()
    .unstack(fill_value=0)
)

rationale_stats["total"] = rationale_stats.sum(axis=1)
rationale_stats["tp_ratio"] = (rationale_stats.get("TP", 0) / rationale_stats["total"] * 100).round(2)
rationale_stats["success_ratio"] = (
    (rationale_stats.get("TP", 0) + rationale_stats.get("Gain", 0)) / rationale_stats["total"] * 100
).round(2)

print(rationale_stats.sort_values("success_ratio", ascending=False))
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Veriyi yükle
df = pd.read_csv("backtest_results.csv")

# Sadece "Buy" sinyalleri üzerinden ilerleyelim
df = df[df["suggestion"] == "Buy"].copy()

# Hedef (label): TP veya Gain → Başarılı (1), diğerleri → Başarısız (0)
df["label"] = df["outcome"].apply(lambda x: 1 if x in ["TP", "Gain"] else 0)

# Özellikler: Sadece backtest_results.csv'de gerçekten var olanlar
features = df[["price", "rationale_count", "pnl_pct"]]
labels = df["label"]

# Eğitim/test veri bölünmesi
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# XGBoost modeli
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Performans raporu
y_pred = model.predict(X_test)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Modeli kaydet
joblib.dump(model, "ml_trade_model.pkl")
print("\n✅ Model başarıyla eğitildi ve 'ml_trade_model.pkl' olarak kaydedildi.")
import pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("dataset.csv")
cols = ["failed", "success", "n_cmds", "n_unique_cmds", "downloads"]
X, y = df[cols], df["label"]

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
m = RandomForestClassifier(n_estimators=100, random_state=42).fit(Xtr, ytr)
pred = m.predict(Xte)

print(classification_report(yte, pred))
print(confusion_matrix(yte, pred))
print(dict(zip(cols, m.feature_importances_.round(2))))
print("5-fold CV:", cross_val_score(m, X, y, cv=5).mean())
joblib.dump(m, "model.pkl")
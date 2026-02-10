import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("model2_priority_sentiment_dataset_10000.csv")

X = df["text"]

# -----------------------------
# PRIORITY MODEL
# -----------------------------
y_priority = df["priority"]

X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
    X, y_priority, test_size=0.2, random_state=42
)

priority_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english"
    )),
    ("clf", LogisticRegression(max_iter=1000))
])

priority_pipeline.fit(X_train_p, y_train_p)

priority_preds = priority_pipeline.predict(X_test_p)
priority_acc = accuracy_score(y_test_p, priority_preds)

joblib.dump(priority_pipeline, "priority_model.pkl")

print(f"✅ Priority Model Accuracy: {priority_acc * 100:.2f}%")

# -----------------------------
# SENTIMENT MODEL
# -----------------------------
y_sentiment = df["sentiment"]

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X, y_sentiment, test_size=0.2, random_state=42
)

sentiment_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english"
    )),
    ("clf", LogisticRegression(max_iter=1000))
])

sentiment_pipeline.fit(X_train_s, y_train_s)

sentiment_preds = sentiment_pipeline.predict(X_test_s)
sentiment_acc = accuracy_score(y_test_s, sentiment_preds)

joblib.dump(sentiment_pipeline, "sentiment_model.pkl")

print(f"✅ Sentiment Model Accuracy: {sentiment_acc * 100:.2f}%")

print("\n🎉 Model 2 Training Complete!")
print("Files saved:")
print("- priority_model.pkl")
print("- sentiment_model.pkl")

import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer

# Load complaint texts
df = pd.read_csv("model1_category_dataset_10000.csv")
texts = df["text"].astype(str)

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=6000
)

# Vectorize complaints
vectors = vectorizer.fit_transform(texts)

# Save vectorizer and vectors
joblib.dump(vectorizer, "duplicate_vectorizer.pkl")
joblib.dump(vectors, "duplicate_vectors.pkl")

print("✅ Duplicate Detection Model Ready!")
print("Saved:")
print("- duplicate_vectorizer.pkl")
print("- duplicate_vectors.pkl")

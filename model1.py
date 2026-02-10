import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class ComplaintClassifier:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english')),
            ('clf', MultinomialNB()),
        ])

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        y_pred = self.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:\n", classification_report(y_test, y_pred))

def load_data(filepath):
    df = pd.read_csv(filepath)
    # Ensure columns exist
    if 'text' not in df.columns or 'category' not in df.columns:
        raise ValueError("CSV must contain 'text' and 'category' columns")
    return df['text'], df['category']


# Global instance for API usage
_api_classifier = None

def train_and_predict_category(text):
    global _api_classifier
    if _api_classifier is None:
        print("Training Model 1 (Category)...")
        _api_classifier = ComplaintClassifier()
        try:
            X, y = load_data('model1_category_dataset_10000.csv')
            _api_classifier.train(X, y)
        except Exception as e:
            return f"Error training model: {str(e)}"
    
    return _api_classifier.predict([text])[0] if _api_classifier else "Error: Model not trained"

if __name__ == "__main__":
    # Example usage if run directly
    print("This module provides the ComplaintClassifier class.")

from model1 import ComplaintClassifier, load_data
from sklearn.model_selection import train_test_split

def main():
    print("Loading data...")
    try:
        X, y = load_data('model1_category_dataset_10000.csv')
    except FileNotFoundError:
        print("Error: 'model1_category_dataset_10000.csv' not found.")
        return

    print(f"Loaded {len(X)} records.")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training model...")
    classifier = ComplaintClassifier()
    classifier.train(X_train, y_train)

    print("Evaluating model...")
    classifier.evaluate(X_test, y_test)

    # Example predictions
    print("\n--- Example Predictions ---")
    examples = [
        "The food in the canteen is too expensive and tastes bad.",
        "My hostel room fan is not working.",
        "The bus was late again today.",
        "I cannot access the wifi in the library."
    ]
    predictions = classifier.predict(examples)
    for text, pred in zip(examples, predictions):
        print(f"Complaint: '{text}' -> Category: {pred}")

if __name__ == "__main__":
    main()

import joblib
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = joblib.load("duplicate_vectorizer.pkl")
vectors = joblib.load("duplicate_vectors.pkl")

def check_duplicate(new_text, threshold=0.75):
    new_vec = vectorizer.transform([new_text])
    similarities = cosine_similarity(new_vec, vectors)[0]

    max_score = similarities.max()
    idx = similarities.argmax()

    if max_score >= threshold:
        return True, idx, max_score
    else:
        return False, None, max_score

# Test
text = "WiFi is not working in Block C"
is_dup, index, score = check_duplicate(text, threshold=0.75)

print("Text:", text)
print("Duplicate:", is_dup)
print("Similarity Score:", score)

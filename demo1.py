import joblib

model = joblib.load("category_model.pkl")

tests = [
    "WiFi is not working in the library",
    "Bus is late every day",
    "Canteen food is stale",
    "Broken fan in classroom",
    "Ragging near hostel gate"
]

for t in tests:
    print(t, "→", model.predict([t])[0])

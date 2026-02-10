import requests
import json

url = "http://127.0.0.1:5000/create-ticket"
payload = {
    "complaint": "HEYY THERE IS A RAT IN MESS FOOD",
    "affected_student_count": 1,
    "user_uid": "test_rat_user"
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
    
    # Check for NLP fields
    required_fields = ["category", "priority", "sentiment", "escalation_reason", "ticket_id"]
    for field in required_fields:
        if field in data:
            print(f"✅ Found {field}: {data[field]}")
        else:
            print(f"❌ Missing {field}")
            
    # Verify in Firestore
    print("\nVerifying in Firestore...")
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client(database_id="tickets")
    
    ticket_id = data["ticket_id"]
    doc = db.collection("tickets").document(ticket_id).get()
    if doc.exists:
        print(f"✅ Ticket {ticket_id} verified in Firestore!")
        print("Data:", json.dumps(doc.to_dict(), indent=2, default=str))
    else:
        print(f"❌ Ticket {ticket_id} NOT found in Firestore.")
            
except Exception as e:
    print("Error:", str(e))

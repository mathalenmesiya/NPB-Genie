import requests
import time

URL_CREATE = "http://127.0.0.1:5000/create-ticket"

def test_duplication():
    # 1. Create a unique complaint
    unique_issue = f"The water tap in B-Block 3rd floor washroom is leaking heavily {time.time()}"
    print(f"--- Reporting New Issue ---")
    payload1 = {
        "complaint": unique_issue,
        "user_uid": "user_123"
    }
    res1 = requests.post(URL_CREATE, json=payload1).json()
    print(f"Ticket 1 Response: {res1.get('ticket_id')} | Count: {res1.get('affected_student_count')}")
    
    # Wait for Firestore to settle
    time.sleep(2)
    
    # 2. Same issue from different user
    print(f"\n--- Reporting Same Issue (User 456) ---")
    payload2 = {
        "complaint": unique_issue,
        "user_uid": "user_456"
    }
    res2 = requests.post(URL_CREATE, json=payload2).json()
    print(f"Ticket 2 Response: {res2.get('message')}")
    print(f"New Affected Count: {res2.get('new_affected_count')}")

    # 3. Same issue again from User 123 (should NOT increment)
    print(f"\n--- Reporting Same Issue Again (User 123) ---")
    payload3 = {
        "complaint": unique_issue,
        "user_uid": "user_123"
    }
    res3 = requests.post(URL_CREATE, json=payload3).json()
    print(f"Ticket 3 Response: {res3.get('message')}")
    print(f"Count: {res3.get('new_affected_count')}")

if __name__ == "__main__":
    test_duplication()

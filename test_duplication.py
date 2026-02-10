import requests
import time

API_URL = "http://127.0.0.1:5000/create-ticket"

def test_flow():
    complaint = "The hostel wifi is down in Block C"
    
    print(f"--- Posting initial complaint: '{complaint}' ---")
    res1 = requests.post(API_URL, json={"complaint": complaint, "user_uid": "test_user_1"})
    print("Response 1:", res1.json())
    
    ticket_id = res1.json().get("ticket_id")
    
    time.sleep(2)
    
    print(f"\n--- Posting duplicate complaint: '{complaint}' ---")
    res2 = requests.post(API_URL, json={"complaint": complaint, "user_uid": "test_user_2"})
    print("Response 2:", res2.json())
    
    if res2.json().get("duplicate"):
        print("\n✅ Duplicate detected successfully!")
        print(f"Linked to Ticket: {res2.json().get('ticket_id')}")
        print(f"New Affected Count: {res2.json().get('new_affected_count')}")
    else:
        print("\n❌ Duplicate NOT detected.")

if __name__ == "__main__":
    test_flow()

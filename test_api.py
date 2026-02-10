import requests
import json
import time

# Wait a moment for server to start
time.sleep(2)

url = "http://127.0.0.1:5000/create-ticket"

print("\n--- Testing API with Escalation Logic ---")

test_cases = [
    {
        "complaint": "The bus was late again today.",
        "affected_student_count": 1
    },
    {
        "complaint": "WiFi is not working in Block C",  # Duplicate check
        "affected_student_count": 1
    },
    {
        "complaint": "The bus was late and students are stranded.",
        "affected_student_count": 10  # Should escalate
    }
]

for case in test_cases:
    print(f"\nSending complaint: '{case['complaint']}' (Affected: {case['affected_student_count']})")
    try:
        response = requests.post(url, json=case)
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

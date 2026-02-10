import requests
import json

url = "http://127.0.0.1:5000/chat"

print("--- Testing FAQ (Library Timings) ---")
payload_faq = {"message": "What are the library timings?"}
res_faq = requests.post(url, json=payload_faq)
print(f"Response: {res_faq.json()}")

print("\n--- Testing Ticket Escalation (Broken Fan) ---")
payload_ticket = {"message": "The fan in my room is broken."}
res_ticket = requests.post(url, json=payload_ticket)
print(f"Response: {res_ticket.json()}")

print("\n--- Testing Casual Talk (What's up?) ---")
payload_chat = {"message": "what's up"}
res_chat = requests.post(url, json=payload_chat)
print(f"Response: {res_chat.json()}")

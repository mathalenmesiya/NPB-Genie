from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import uuid
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests

from llm_agent import triage_message, analyze_grievance

app = Flask(__name__)
CORS(app)

# ================================
# 🤖 AGENT FLOW ARCHITECTURE
# ================================
# Student Message
#     ↓
# 🧠 AGENT 4: RAG + Gemini (Triage) - /chat endpoint
#     ├── Answer from Knowledge Base → Done
#     └── Needs Ticket → Continue
#             ↓
# 🤖 AGENT 3: Duplicate Detection - check_duplicate_live()
#     ├── Duplicate Found → Increment existing ticket
#     └── New Issue → Continue
#             ↓
# 🤖 AGENTS 1 & 2: Category + Priority/Sentiment - analyze_grievance()
#     ↓
# 🔥 Escalation Logic (if needed)
#     ↓
# 💾 Firebase (Ticket Saved)
# ================================

@app.route("/chat", methods=["POST"])
def chat_triage():
    """
    BhavaniBot Triage Agent: Decides if an issue is a known FAQ or needs a ticket.
    Uses Gemini LLM for RAG.
    """
    data = request.get_json()
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"action": "resolve", "message": "I didn't catch that. How can I help?"}), 200

    # Triage Logic: Use LLM Agent
    result = triage_message(message)
    return jsonify(result)

# ------------------------------
# FIREBASE INITIALIZATION
# ------------------------------
MC_CUSTOMER_ID = "C-7FDB692826454A9"
MC_AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJDLTdGREI2OTI4MjY0NTRBOSIsImlhdCI6MTc3MDY2Mjk4MywiZXhwIjoxOTI4MzQyOTgzfQ.eL_1Q8J5BZZiU9_5iMOX6HbWBcEaSM64GfOakse8sXIEFv1bBMa_0GAULV3YI1W2LF1383pWhrFBD3-SwoH90A"
MC_BASE_URL = "https://cpaas.messagecentral.com"

# ------------------------------
# FIREBASE INITIALIZATION
# ------------------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client(database_id="tickets")

# ------------------------------
# LOAD MODEL 3 (Duplicate Detection)
# ------------------------------
vectorizer = joblib.load("duplicate_vectorizer.pkl")
vectors = joblib.load("duplicate_vectors.pkl")

DUPLICATE_THRESHOLD = 0.75

# ------------------------------
# DYNAMIC DUPLICATE CHECK
# ------------------------------
def check_duplicate_live(text):
    """
    Checks the new complaint against existing tickets in Firestore using the TF-IDF model.
    """
    try:
        # Get last 100 tickets to check against
        tickets_ref = db.collection("tickets").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).get()
        
        if not tickets_ref:
            return False, None, 0.0

        existing_tickets = []
        for t in tickets_ref:
            td = t.to_dict()
            existing_tickets.append({
                "id": t.id,
                "complaint": td.get("complaint", ""),
                "ticket_id": td.get("ticket_id", "")
            })

        if not existing_tickets:
            return False, None, 0.0

        # Create vectors for existing complaints
        texts = [t["complaint"] for t in existing_tickets]
        existing_vectors = vectorizer.transform(texts)
        
        # Vectorize new complaint
        new_vec = vectorizer.transform([text])
        
        # Calculate similarities
        similarities = cosine_similarity(new_vec, existing_vectors)[0]
        max_score = similarities.max()
        idx = similarities.argmax()

        if max_score >= DUPLICATE_THRESHOLD:
            return True, existing_tickets[idx], float(max_score)
        
    except Exception as e:
        print(f"Error in dynamic duplicate check: {str(e)}")
        
    return False, None, 0.0

# ------------------------------
# AUTH ENDPOINTS (Message Central)
# ------------------------------
@app.route("/api/auth/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    phone = data.get("phone")
    
    if not phone:
        return jsonify({"error": "Phone number required"}), 400

    url = f"{MC_BASE_URL}/verification/v3/send"
    headers = {"authToken": MC_AUTH_TOKEN}
    params = {
        "customerId": MC_CUSTOMER_ID,
        "mobileNumber": phone,
        "countryCode": "91",
        "flowType": "SMS",
        "otpLength": 6
    }
    
    try:
        with open("otp_debug.log", "a") as f:
            f.write(f"\n--- SEND OTP --- \nPhone: {phone}\n")
        response = requests.post(url, headers=headers, params=params)
        with open("otp_debug.log", "a") as f:
            f.write(f"Status: {response.status_code}\nBody: {response.text}\n")
        
        try:
            res_data = response.json()
        except:
            return jsonify({"error": f"Invalid response from SMS provider. Check otp_debug.log"}), 500
        
        if response.status_code == 200 and res_data.get("responseCode") == 200:
            return jsonify({
                "message": "OTP sent successfully",
                "verificationId": res_data["data"]["verificationId"]
            })
        else:
            return jsonify({"error": res_data.get("message", "Failed to send OTP")}), 400
    except Exception as e:
        with open("otp_debug.log", "a") as f:
            f.write(f"Exception: {str(e)}\n")
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    phone = data.get("phone")
    otp = data.get("otp")
    verification_id = data.get("verificationId")

    if not all([phone, otp, verification_id]):
        return jsonify({"error": "Missing parameters"}), 400

    url = f"{MC_BASE_URL}/verification/v3/validateOtp"
    headers = {"authToken": MC_AUTH_TOKEN}
    params = {
        "customerId": MC_CUSTOMER_ID,
        "mobileNumber": phone,
        "countryCode": "91",
        "verificationId": verification_id,
        "code": otp,
        "authToken": MC_AUTH_TOKEN
    }

    try:
        with open("otp_debug.log", "a") as f:
            f.write(f"\n--- VERIFY OTP --- \nPhone: {phone}, OTP: {otp}, ID: {verification_id}\n")
        response = requests.get(url, headers=headers, params=params)
        with open("otp_debug.log", "a") as f:
            f.write(f"Status: {response.status_code}\nBody: {response.text}\n")

        try:
            res_data = response.json()
        except:
            return jsonify({"error": f"Invalid response during verification. Check otp_debug.log"}), 500

        if response.status_code == 200 and res_data.get("responseCode") == 200:
            # OTP Verified!
            uid = f"phone_{phone}"
            
            # Check for existing role in Firestore
            user_ref = db.collection("users").document(uid)
            user_snap = user_ref.get()
            
            role = None
            if user_snap.exists:
                role = user_snap.to_dict().get("role")

            with open("otp_debug.log", "a") as f:
                f.write(f"SUCCESS: OTP Verified for {phone}. Role: {role}\n")
            
            return jsonify({
                "message": "Verified",
                "uid": uid,
                "phone": phone,
                "role": role  # FE will check if role is null to show selection
            })
        else:
            error_msg = res_data.get("message", "Invalid OTP or session expired")
            with open("otp_debug.log", "a") as f:
                f.write(f"FAILED: {error_msg}\n")
            return jsonify({"error": error_msg}), 400
    except Exception as e:
        print(f"Exception in verify_otp: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/admin-login", methods=["POST"])
def admin_login():
    """
    Admin login with username and password.
    Dummy credentials for testing: admin/npgenie2024
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not all([username, password]):
        return jsonify({"error": "Username and password required"}), 400
    
    # Dummy credentials for testing
    ADMIN_CREDENTIALS = {
        "admin": "npgenie2024",
        "staff": "npgenie2024"
    }
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        uid = f"admin_{username}"
        
        # Store/update admin in Firestore
        try:
            admin_ref = db.collection("users").document(uid)
            admin_ref.set({
                "username": username,
                "role": "admin",
                "created_at": firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            return jsonify({
                "message": "Login successful",
                "uid": uid,
                "username": username,
                "role": "admin"
            })
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route("/api/auth/complete-profile", methods=["POST"])
def complete_profile():
    data = request.get_json()
    uid = data.get("uid")
    phone = data.get("phone")
    role = data.get("role")

    if not all([uid, phone, role]):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        user_ref = db.collection("users").document(uid)
        user_ref.set({
            "phone": phone if phone.startswith("+") else f"+91{phone}",
            "role": role,
            "createdAt": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"message": "Profile created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------
# MAIN API ENDPOINT
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Smart Ticketing API is running!", "endpoints": ["/create-ticket"]})

@app.route("/create-ticket", methods=["POST"])
def create_ticket():
    data = request.get_json()

    if not data or "complaint" not in data:
        return jsonify({"error": "Complaint text required"}), 400

    complaint = data["complaint"]
    
    # 1️⃣ Live Duplicate Detection
    is_duplicate, original_ticket, score = check_duplicate_live(complaint)

    if is_duplicate:
        orig_id = original_ticket["id"]
        try:
            doc_ref = db.collection("tickets").document(orig_id)
            doc_snap = doc_ref.get()
            if doc_snap.exists:
                ticket_data = doc_snap.to_dict()
                current_count = ticket_data.get("affected_student_count", 1)
                reporters = ticket_data.get("reporters", [])
                user_uid = data.get("user_uid", "anonymous")

                if user_uid not in reporters:
                    reporters.append(user_uid)
                    new_count = current_count + 1
                    doc_ref.update({
                        "affected_student_count": new_count,
                        "reporters": reporters
                    })
                    message = "This issue is already reported. We have linked your grievance to the existing ticket, increasing its priority."
                else:
                    new_count = current_count
                    message = "You have already reported this issue. We are working on it!"

                return jsonify({
                    "duplicate": True,
                    "message": message,
                    "ticket_id": original_ticket["ticket_id"],
                    "original_complaint": original_ticket["complaint"],
                    "new_affected_count": new_count,
                    "similarity_score": round(score, 2)
                })
        except Exception as e:
            print(f"Error updating duplicate: {str(e)}")

    # 2️⃣-4️⃣ Unified Analysis with Gemini LLM
    affected_count = data.get("affected_student_count", 1)
    analysis = analyze_grievance(complaint, affected_count)
    
    category = analysis.get("category", "General")
    priority = analysis.get("priority", "Medium")
    sentiment = analysis.get("sentiment", "Calm")
    escalation_reason = analysis.get("reason", "AI Analysis complete.")

    temp_ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"
    
    # 5️⃣ Ticket Creation (Mock -> Real Firestore)
    ticket = {
        "duplicate": False,
        "ticket_id": temp_ticket_id,
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "affected_student_count": affected_count,
        "escalation_reason": escalation_reason,
        "status": "Ticket Created",
        "user_uid": data.get("user_uid", "anonymous"),
        "reporters": [data.get("user_uid", "anonymous")]
    }

    # Save to Firestore
    try:
        # Create a copy for Firestore with the server timestamp
        firestore_ticket = ticket.copy()
        firestore_ticket["timestamp"] = firestore.SERVER_TIMESTAMP
        
        db.collection("tickets").document(temp_ticket_id).set(firestore_ticket)
        ticket["firebase_status"] = "Saved to Firestore"
    except Exception as e:
        ticket["firebase_status"] = f"Error saving to Firestore: {str(e)}"

    return jsonify(ticket)

# ------------------------------
# RUN SERVER
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

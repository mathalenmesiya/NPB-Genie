import google.generativeai as genai
from dotenv import load_dotenv
import time
import os
import json

"""
🤖 NP GENIE - AGENT ARCHITECTURE
================================

This file implements 2 of the 4 core agents:

🧠 AGENT 4: RAG + Gemini LLM (Triage Only)
   - Function: triage_message()
   - Purpose: Decide if query is FAQ, casual chat, or needs a ticket
   - Output: {"action": "resolve|chat|create_ticket", "message": "..."}
   - Does NOT classify category, priority, or sentiment

🤖 AGENTS 1 & 2: Category + Priority/Sentiment Classification
   - Function: analyze_grievance()
   - Purpose: Classify ticket category, priority, and sentiment
   - Output: {"category": "...", "priority": "...", "sentiment": "..."}
   - Uses Gemini for intelligent classification

🤖 AGENT 3: Duplicate Detection
   - Located in: app.py (check_duplicate_live())
   - Purpose: Prevent duplicate tickets using TF-IDF matching
   - Output: Duplicate ticket ID or None

FLOW:
Student Message → Agent 4 (Triage) → Agent 3 (Duplicate) → 
Agents 1 & 2 (Classify) → Escalation Logic → Firebase
"""

# Suppress low-level warnings
os.environ["GRPC_VERBOSITY"] = "error"
os.environ["GLOG_minloglevel"] = "2"

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def get_knowledge_context():
    KNOWLEDGE_PATH = "college_knowledge.json"
    if os.path.exists(KNOWLEDGE_PATH):
        with open(KNOWLEDGE_PATH, "r") as f:
            data = json.load(f)
            items = data.get("knowledge_items", [])
            context = "College Knowledge Base:\n"
            for item in items:
                context += f"- ID: {item['id']}\n  Keywords: {', '.join(item['keywords'])}\n  Solution: {item['solution']}\n"
            return context
    return "No knowledge base available."

def extract_json(text):
    """
    Extracts JSON from a string that might contain markdown blocks.
    """
    json_text = text.strip()
    if "```json" in json_text:
        json_text = json_text.split("```json")[1].split("```")[0].strip()
    elif "```" in json_text:
        json_text = json_text.split("```")[1].split("```")[0].strip()
    return json_text

def triage_message(user_message):
    """
    🧠 AGENT 4: RAG + Gemini LLM (Triage Only)
    Decides if a message is college-related and whether it needs a ticket.
    """
    knowledge_context = get_knowledge_context()
    
    prompt = f"""
You are **NP GENIE**, an AI chatbot for New Prince Shri Bhavani College complaint management system.

Your primary responsibility is to IDENTIFY and HANDLE COLLEGE-RELATED ISSUES.
You are NOT a general-purpose assistant.

────────────────────────
STRICT RULES — YOU MUST FOLLOW ALL:
────────────────────────

1. ALLOWED TOPICS
   You may ONLY respond to:
   - College infrastructure issues
   - Campus facilities problems
   - Transport, hostel, IT, academic, maintenance, safety-related issues
   - Casual greetings (hello, how are you) with SHORT replies
   
   Examples of allowed issues:
   - "WiFi not working in Block B"
   - "There is a gas leak in the canteen"
   - "Bus is late every morning"
   - "Classroom projector is broken"

2. DISALLOWED TOPICS
   You MUST NOT answer:
   - Programming questions (e.g., Python, Java, ML, coding help)
   - General knowledge or internet facts
   - Personal advice or life questions
   - Non-college topics
   
   For disallowed topics, use action "reject" and politely redirect to campus issues.

3. TICKET CREATION DECISION
   If the message indicates:
   - A real-world problem
   - A safety issue
   - A service failure
   - An operational disruption
   
   → YOU MUST use action "create_ticket"
   
   Critical issues (fire, gas leak, electric shock, safety hazards)
   → IMMEDIATE ticket creation (no extra questions)

4. YOUR ROLE
   You ONLY:
   - Acknowledge the issue
   - Trigger ticket creation
   
   You MUST NOT:
   - Predict category, priority, or sentiment
   - Detect duplicates
   - Perform escalation
   - Make final decisions
   
   These are handled by downstream ML agents.

────────────────────────
KNOWLEDGE CONTEXT:
────────────────────────
{knowledge_context}

────────────────────────
INPUT MESSAGE:
────────────────────────
"{user_message}"

────────────────────────
OUTPUT FORMAT (JSON ONLY):
────────────────────────

A. If casual greeting:
{{
  "action": "chat",
  "message": "Hello! I'm NP Genie, here to help with campus-related issues. How can I assist you?"
}}

B. If non-college / disallowed query:
{{
  "action": "reject",
  "message": "I can only help with college-related issues or campus complaints. For other questions, please consult appropriate resources."
}}

C. If knowledge base can answer:
{{
  "action": "resolve",
  "message": "[Provide the answer from knowledge base naturally]"
}}

D. If issue requires a ticket:
{{
  "action": "create_ticket",
  "message": "I understand the issue. I will raise a ticket for this right away."
}}

────────────────────────
SAFETY & RELIABILITY:
────────────────────────
- Never hallucinate answers
- Never explain technical concepts outside campus scope
- When in doubt → create a ticket
- Your goal: ensure ALL real campus problems are captured efficiently

Respond ONLY with valid JSON.
"""
    last_error = ""
    for attempt in range(3):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            if not response.candidates:
                last_error = "No candidates"
                continue
            
            if response.candidates[0].finish_reason == 3: # SAFETY
                return {"action": "reject", "message": "I can only help with college-related issues or campus complaints. Please keep the conversation appropriate."}

            text = extract_json(response.text)
            return json.loads(text)
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "quota" in last_error.lower():
                print(f"Quota hit, waiting 5s... ({attempt+1}/3)")
                time.sleep(5)
            else:
                break
    
    with open("gemini_errors.log", "a") as f:
        f.write(f"Triage Final Error: {last_error}\n")
    return {"action": "create_ticket", "message": "I'm here to help. Let's look into this further by raising a ticket."}

def analyze_grievance(complaint, affected_count):
    """
    Predicts Category, Priority, and Sentiment for a grievance.
    """
    categories = ["Canteen", "Hostel", "Academic", "Infrastructure", "Admin", "Transport", "Security"]
    
    prompt = f"""
You are the **NPGENIE Analysis Engine**, a high-precision grievance analyst for New Prince Shri Bhavani College.
Analyze this issue and provide structured data.

Input:
Complaint: "{complaint}"
Affected Student Count: {affected_count}

Analysis Rules:
- Category: Pick from {categories}.
- Sentiment: Tone of the student (Calm, Frustrated, Angry).
- Priority: Level (Low, Medium, High, Critical).
  - FORCE High/Critical if the complaint mentioned safety hazards (rats, snakes, fire, electrical issues, danger).
  - Boost if affected count >= 5.
  - Boost if Sentiment is Angry.

Output MUST be a single JSON object.

Output JSON Format:
{{
    "category": "...",
    "sentiment": "...",
    "priority": "...",
    "reason": "Short reason for the priority/escalation"
}}
"""
    last_error = ""
    for attempt in range(3):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            if not response.candidates:
                last_error = "No candidates"
                continue

            if response.candidates[0].finish_reason == 3: # SAFETY
                return {
                    "category": "General", "sentiment": "Calm", "priority": "High",
                    "reason": "Safety block triggered."
                }

            text = extract_json(response.text)
            return json.loads(text)
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "quota" in last_error.lower():
                print(f"Quota hit, waiting 5s... ({attempt+1}/3)")
                time.sleep(5)
            else:
                break

    with open("gemini_errors.log", "a") as f:
        f.write(f"Analysis Final Error: {last_error}\n")
    return {
        "category": "General", "sentiment": "Calm", "priority": "Medium",
        "reason": "AI processing error."
    }

if __name__ == "__main__":
    # Test cases
    print("Test FAQ:", triage_message("What are the canteen hours?"))
    time.sleep(2)
    print("Test Grievance:", analyze_grievance("The hostel washrooms are leaking and it is dangerous", 10))

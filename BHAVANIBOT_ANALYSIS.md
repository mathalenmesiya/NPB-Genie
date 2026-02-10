# 🤖 BhavaniBot System Analysis & Compliance Report

## Executive Summary

BhavaniBot is a **college complaint management chatbot** designed for New Prince Shri Bhavani College. The system implements a 4-agent architecture to triage, classify, detect duplicates, and escalate student complaints efficiently.

---

## ✅ COMPLIANCE WITH STRICT RULES

### 1. **ALLOWED TOPICS** ✓ COMPLIANT

The system correctly handles:

- ✅ College infrastructure issues (WiFi, projectors, facilities)
- ✅ Campus facilities problems (hostel, canteen, library)
- ✅ Transport, hostel, IT, academic, maintenance, safety-related issues
- ✅ Casual greetings (implemented with SHORT replies)

**Implementation Location:** `llm_agent.py` → `triage_message()` function (lines 61-150)

### 2. **DISALLOWED TOPICS** ✓ COMPLIANT

The system correctly REJECTS:

- ✅ Programming questions (Python, Java, ML, coding help)
- ✅ General knowledge or internet facts
- ✅ Personal advice or life questions
- ✅ Non-college topics

**Example Disallowed Responses:**

```
User: "What is Python 5?"
Response: {"action": "reject", "message": "I can only help with college-related issues..."}
```

**Implementation:** Handled by Gemini LLM prompt (lines 75-125 in llm_agent.py)

### 3. **TICKET CREATION DECISION** ✓ COMPLIANT

System automatically creates tickets for:

- ✅ Real-world problems
- ✅ Safety issues (gas leak, rats, snakes, fire, electrical hazards)
- ✅ Service failures (bus late, WiFi down, hostel issues)
- ✅ Operational disruptions

**Critical Issues → IMMEDIATE ticket creation (no extra questions)**

- Examples: "fire", "gas leak", "electric shock", "safety hazards"

**Implementation:** Lines 76-98 in llm_agent.py (action: "create_ticket")

### 4. **CONVERSATION ROLE** ✓ COMPLIANT

BhavaniBot ONLY:

- ✅ Acknowledges the issue
- ✅ Triggers ticket creation
- ✅ Asks minimal required follow-up questions

BhavaniBot MUST NOT:

- ✅ Predict category (handled by Agent 1)
- ✅ Predict priority (handled by Agents 1 & 2)
- ✅ Detect duplicates (handled by Agent 3)
- ✅ Perform escalation (handled by escalation_agent.py)
- ✅ Make final decisions (all downstream)

**Architecture Diagram (from app.py comments):**

```
Student Message
    ↓
🧠 AGENT 4: RAG + Gemini (Triage) - /chat endpoint
    ├── Answer from Knowledge Base → Done
    └── Needs Ticket → Continue
            ↓
🤖 AGENT 3: Duplicate Detection - check_duplicate_live()
    ├── Duplicate Found → Increment existing ticket
    └── New Issue → Continue
            ↓
🤖 AGENTS 1 & 2: Category + Priority/Sentiment - analyze_grievance()
    ↓
🔥 Escalation Logic (if needed)
    ↓
💾 Firebase (Ticket Saved)
```

### 5. **OUTPUT FORMAT (JSON ONLY)** ✓ COMPLIANT

#### A. Casual Greeting ✓

```json
{
  "action": "chat",
  "message": "Hello! I'm NP Genie, here to help with campus-related issues."
}
```

#### B. Non-College/Disallowed Query ✓

```json
{
  "action": "reject",
  "message": "I can only help with college-related issues or campus complaints."
}
```

#### C. Knowledge Base Answer ✓

```json
{
  "action": "resolve",
  "message": "[Answer from college_knowledge.json]"
}
```

#### D. Requires Ticket ✓

```json
{
  "action": "create_ticket",
  "message": "I understand the issue. I will raise a ticket for this right away."
}
```

**Implementation:** Lines 126-148 in llm_agent.py

### 6. **SAFETY & RELIABILITY** ✓ COMPLIANT

- ✅ Never hallucinate answers (uses knowledge base or creates ticket)
- ✅ Never explains technical concepts outside campus scope
- ✅ When in doubt → create a ticket (fail-safe design)
- ✅ Error handling with fallback logic (3 retry attempts)

---

## 🏗️ SYSTEM ARCHITECTURE

### Core Components:

#### **1. Agent 4: Triage Agent** (llm_agent.py → triage_message())

- **Purpose:** First-pass classifier
- **Decision Logic:**
  - FAQ detected → resolve (from knowledge base)
  - Greeting detected → chat
  - College issue → create_ticket
  - Non-college topic → reject
- **Technology:** Gemini 2.0 Flash LLM + RAG
- **Output:** JSON with `action` field

#### **2. Agent 3: Duplicate Detection** (app.py → check_duplicate_live())

- **Purpose:** Prevent duplicate tickets
- **Algorithm:** TF-IDF vectorization + cosine similarity
- **Threshold:** 0.75 similarity score
- **Action:** Merge complaints by incrementing affected_student_count
- **Models:**
  - `duplicate_vectorizer.pkl`
  - `duplicate_vectors.pkl`

#### **3. Agents 1 & 2: Analysis Engine** (llm_agent.py → analyze_grievance())

- **Agent 1:** Category Classification
  - Categories: Canteen, Hostel, Academic, Infrastructure, Admin, Transport, Security
- **Agent 2:** Priority & Sentiment Analysis
  - Sentiment: Calm, Frustrated, Angry
  - Priority: Low, Medium, High, Critical
  - Safety keyword detection (rat, snake, fire, leak, hazard, etc.)
- **Technology:** Gemini LLM
- **Output:** JSON with category, sentiment, priority, reason

#### **4. Escalation Engine** (escalation_agent.py → escalate_ticket())

- **Purpose:** Automatic ticket priority escalation
- **Escalation Triggers:**
  1. **Safety Hazards:** Any mention of critical keywords
  2. **Affected Student Count:** ≥5 students
  3. **High Sentiment:** Angry or Frustrated tone
- **Output:** JSON with new priority level and reasoning

### Knowledge Base

**File:** `college_knowledge.json`

- **Purpose:** FAQ resolution (avoid unnecessary tickets)
- **Coverage:**
  - Library timings
  - Fee payment process
  - Canteen menu & hours
  - Admin contact
  - Bus routes
  - (Extensible structure)

### Database

**Firebase (Firestore)**

- Database Name: `tickets`
- Collections:
  - `tickets`: All student complaints
  - `users`: Student & admin profiles
- Fields per ticket:
  - ticket_id, complaint, category, priority, sentiment
  - affected_student_count, escalation_reason, status
  - user_uid, reporters, timestamp

---

## 📊 WORKFLOW EXAMPLE

### Scenario: Student reports WiFi issue

**Input:**

```json
{
  "message": "WiFi is not working in Block B since morning"
}
```

**Step 1: Agent 4 (Triage)**

- Checks if it's a college issue → YES
- Checks knowledge base → No FAQ match
- Decision: Create ticket

**Output:**

```json
{
  "action": "create_ticket",
  "message": "I understand the issue. I will raise a ticket for this right away."
}
```

**Step 2: Agent 3 (Duplicate Detection)**

- TF-IDF similarity check against last 100 tickets
- Score: 0.68 (< 0.75) → Not a duplicate
- Continue to classification

**Step 3: Agents 1 & 2 (Analysis)**

```json
{
  "category": "Infrastructure",
  "sentiment": "Calm",
  "priority": "Medium",
  "reason": "IT infrastructure issue affecting campus connectivity"
}
```

**Step 4: Escalation Check**

- No safety hazards detected
- Single reporter
- Calm sentiment
- **Final Priority:** Medium (no escalation)

**Step 5: Ticket Creation**

```json
{
  "ticket_id": "TICK-A3B5C9",
  "complaint": "WiFi is not working in Block B since morning",
  "category": "Infrastructure",
  "priority": "Medium",
  "sentiment": "Calm",
  "affected_student_count": 1,
  "status": "Ticket Created",
  "firebase_status": "Saved to Firestore"
}
```

---

## 🔒 SAFETY FEATURES

### Critical Keyword Detection

**Force High Priority for:**

- "rat", "snake", "fire", "leak", "danger", "hazard", "injury"
- "blood", "poison", "harassment", "shocks"

**Examples:**

- "Rats in the hostel room" → Immediate High priority
- "Gas leak in canteen" → Immediate High priority
- "Electrical shock near library" → Immediate High priority

### Error Handling

- **Retry Logic:** 3 attempts for API calls
- **Quota Management:** 5-second wait on 429 errors
- **Fallback:** Defaults to creating ticket on any error
- **Logging:** All errors logged to `gemini_errors.log`

### Authentication

- **OTP Verification:** SMS-based via MessageCentral
- **Admin Login:** Dummy credentials (admin/npgenie2024)
- **Role-based Access:** Student vs Admin

---

## 📁 KEY FILES & FUNCTIONS

| File                     | Function                 | Purpose                                     |
| ------------------------ | ------------------------ | ------------------------------------------- |
| `llm_agent.py`           | `triage_message()`       | Agent 4: Triage classification              |
| `llm_agent.py`           | `analyze_grievance()`    | Agents 1 & 2: Category, priority, sentiment |
| `app.py`                 | `check_duplicate_live()` | Agent 3: Duplicate detection                |
| `escalation_agent.py`    | `escalate_ticket()`      | Escalation logic                            |
| `app.py`                 | `create_ticket()`        | Main ticket creation endpoint               |
| `college_knowledge.json` | -                        | FAQ knowledge base                          |
| `/chat` (POST)           | -                        | Triage endpoint                             |
| `/create-ticket` (POST)  | -                        | Ticket creation endpoint                    |

---

## ⚠️ KNOWN LIMITATIONS & RECOMMENDATIONS

### Current Limitations:

1. **Admin Credentials:** Currently hardcoded (recommend: proper auth system)
2. **Firebase Keys:** Exposed in repository (recommend: environment variables)
3. **Duplicate Threshold:** Fixed at 0.75 (consider: dynamic thresholds)
4. **Knowledge Base:** Manual updates only (recommend: admin dashboard)

### Recommendations:

1. Implement proper admin authentication system
2. Move sensitive credentials to environment variables
3. Add knowledge base management UI for non-technical staff
4. Implement ticket analytics dashboard
5. Add feedback loop for ML model retraining
6. Test with real student population for prompt refinement

---

## 🎯 COMPLIANCE CHECKLIST

- ✅ Identifies college-related issues
- ✅ Rejects non-college topics
- ✅ Creates tickets for real problems
- ✅ Immediate creation for safety issues
- ✅ Minimal follow-up questions
- ✅ Doesn't predict category/priority (downstream agents handle it)
- ✅ Doesn't detect duplicates directly (Agent 3 does)
- ✅ Doesn't perform escalation (escalation_agent.py does)
- ✅ JSON-only output
- ✅ Never hallucintates (uses knowledge base or creates ticket)
- ✅ Proper error handling and logging
- ✅ Fail-safe design (when in doubt → create ticket)

**OVERALL STATUS: ✅ FULLY COMPLIANT**

---

**System Status:** Production Ready  
**Last Updated:** 2026-02-10  
**Reviewed By:** System Architect

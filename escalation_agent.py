import json

PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]

def get_priority_index(priority):
    if priority in PRIORITY_LEVELS:
        return PRIORITY_LEVELS.index(priority)
    return -1

def escalate_ticket(ticket_id, current_priority, affected_student_count, complaint="", sentiment="Calm"):
    """
    Intelligent ticket escalation logic based on student count, safety keywords, and sentiment.
    """
    new_priority = current_priority
    reasons = []

    # 1️⃣ Safety & Hygiene Keyword Detection
    critical_keywords = ["rat", "snake", "fire", "leak", "danger", "hazard", "injury", "blood", "poison", "harassment", "shocks"]
    safety_hazard = any(word in complaint.lower() for word in critical_keywords)
    
    if safety_hazard:
        # Force High if currently Low/Medium
        if get_priority_index(new_priority) < get_priority_index("High"):
            new_priority = "High"
            reasons.append("Safety/Hygiene hazard detected")

    # 2️⃣ Affected Student Count Escalation
    if affected_student_count >= 5:
        idx = get_priority_index(new_priority)
        if idx != -1 and idx < len(PRIORITY_LEVELS) - 1:
            new_priority = PRIORITY_LEVELS[idx + 1]
            reasons.append(f"Affected student count reached {affected_student_count}")

    # 3️⃣ Sentiment-based Boosting
    if sentiment in ["Angry", "Frustrated"]:
        idx = get_priority_index(new_priority)
        if idx != -1 and idx < len(PRIORITY_LEVELS) - 1:
            new_priority = PRIORITY_LEVELS[idx + 1]
            reasons.append(f"High-stress sentiment detected ({sentiment})")

    # Final logic: Ensure no duplicate reasons and clean message
    final_reason = " & ".join(reasons) if reasons else "Escalation criteria not met"
    
    return json.dumps({
        "ticket_id": ticket_id,
        "previous_priority": current_priority,
        "new_priority": new_priority,
        "reason": final_reason
    }, indent=2)

if __name__ == "__main__":
    # Test Cases
    test_cases = [
        ("T101", "Low", 3),   # No change
        ("T102", "Low", 5),   # Escalate to Medium
        ("T103", "Medium", 10), # Escalate to High
        ("T104", "High", 7),    # Escalate to Critical
        ("T105", "Critical", 20) # Stay Critical
    ]

    for tid, prio, count in test_cases:
        print(f"--- Ticket {tid} (Priority: {prio}, Affected: {count}) ---")
        result = escalate_ticket(tid, prio, count)
        print(result)
        print()

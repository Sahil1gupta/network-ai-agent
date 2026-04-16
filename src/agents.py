# src/agents.py
import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from llm_client import get_llm
from rag_pipeline import retrieve_context

# Ek baar LLM object banao — saare agents ye use karenge
llm = get_llm(model="gpt-4o")


def _call_llm(system: str, user: str) -> str:
    """
    LLM ko call karo, raw string response return karo.
    Har agent is helper function ko use karta hai.
    """
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=user)
    ]
    response = llm.invoke(messages)
    return response.content          # LangChain mein .content se text milta hai


def _parse_json(raw: str) -> dict:
    """
    LLM ke response se clean JSON nikalo.
    LLM kabhi kabhi ```json ... ``` wrap karta hai — usse remove karo.
    """
    raw = re.sub(r"```json\n?", "", raw)
    raw = re.sub(r"```\n?",     "", raw)
    return json.loads(raw.strip())


# ── Agent 1 — Fault Classifier ────────────────────────────────────────────────
def classify_fault(alarm: dict) -> dict:
    """
    Alarm dict leke fault classify karo.
    Input : alarm dict
    Output: {"fault_type": "BGP_DOWN", "priority": "P1", ...}
    """
    system = """You are a NOC fault classification expert at STC Saudi Arabia.
Given a network alarm, classify it and return ONLY valid JSON with these keys:
- fault_type: the alarm category
- priority: P1, P2, or P3 (P1=critical, P2=major, P3=minor)
- urgency: immediate, high, medium, or low
- affected_users_estimate: rough number as a string
Return JSON only. No explanation before or after."""

    user = f"""Classify this alarm:
Device:      {alarm['device']}
Type:        {alarm['alarm_type']}
Severity:    {alarm['severity']}
Description: {alarm['description']}
Region:      {alarm['region']}"""

    result = _parse_json(_call_llm(system, user))
    print(f"  [Agent 1] {result['fault_type']} — {result['priority']}")
    return result


# ── Agent 2 — Context Fetcher ─────────────────────────────────────────────────
def fetch_context(alarm: dict, classification: dict) -> str:
    """
    RAG use karke relevant runbook content retrieve karo.
    Input : alarm + classification
    Output: relevant runbook text string
    """
    query   = f"{alarm['alarm_type']} {alarm['description']} {classification['priority']}"
    context = retrieve_context(query, k=2)
    print(f"  [Agent 2] Retrieved {len(context)} chars from runbooks")
    return context


# ── Agent 3 — RCA Generator ───────────────────────────────────────────────────
def generate_rca(alarm: dict, classification: dict, context: str) -> dict:
    """
    Alarm details + runbook context se RCA generate karo.
    Input : alarm, classification, retrieved context
    Output: {"root_cause": "...", "resolution_steps": [...], ...}
    """
    system = """You are a senior network engineer at STC Saudi Arabia performing Root Cause Analysis.
You have access to internal runbooks. Use them to give specific answers.
Return ONLY valid JSON with these keys:
- root_cause: specific root cause in 1-2 sentences
- confidence: high, medium, or low
- resolution_steps: list of 3-5 actionable steps as strings
- escalate: true or false
- estimated_fix_time: e.g. 20 minutes or 4 hours
JSON only. No explanation."""

    user = f"""Perform RCA for this alarm:

ALARM DETAILS:
Device:      {alarm['device']}
Type:        {alarm['alarm_type']}
Description: {alarm['description']}
Priority:    {classification['priority']}

RELEVANT RUNBOOK:
{context}"""

    result = _parse_json(_call_llm(system, user))
    print(f"  [Agent 3] RCA: {result['root_cause'][:70]}...")
    return result


# ── Agent 4 — Ticket Creator ──────────────────────────────────────────────────
def create_ticket(alarm: dict, classification: dict, rca: dict) -> dict:
    """
    Saari information combine karke final incident ticket dict banao.
    Ye agent LLM call nahi karta — pure Python logic hai.
    Input : alarm + classification + rca
    Output: complete ticket dict
    """
    from datetime import datetime

    ticket = {
        "ticket_id":          f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "created_at":         datetime.now().isoformat(),
        "status":             "OPEN",
        "alarm_id":           alarm["alarm_id"],
        "device":             alarm["device"],
        "region":             alarm["region"],
        "alarm_type":         alarm["alarm_type"],
        "description":        alarm["description"],
        "priority":           classification["priority"],
        "urgency":            classification["urgency"],
        "affected_users":     classification["affected_users_estimate"],
        "root_cause":         rca["root_cause"],
        "confidence":         rca["confidence"],
        "resolution_steps":   rca["resolution_steps"],
        "escalate_to_l3":     rca["escalate"],
        "estimated_fix_time": rca["estimated_fix_time"],
        "assigned_team":      "NOC-L2" if classification["priority"] == "P1" else "NOC-L1",
    }
    print(f"  [Agent 4] Ticket created: {ticket['ticket_id']}")
    return ticket
# src/escalation_service.py
import threading
import time
from email_service import send_escalation_email

# ── Global state ───────────────────────────────────────────────────────────────
# Ye dictionary saare active tickets track karti hai
# { "INC-xxx": {"ticket": {...}, "resolved": False, "escalated": False} }
_active = {}

# Thread-safe operations ke liye lock
# Lock kya hai? — ek time pe sirf ek thread dictionary modify kar sake
_lock = threading.Lock()


def _timer_thread(ticket_id: str, minutes: int):
    """
    Background mein chalne wala function.
    
    Kya karta hai:
    1. X minutes sleep karo
    2. Uthke check karo — resolve hua?
    3. Nahi hua → escalation email bhejo
    
    Ye function directly call nahi hota —
    threading.Thread ke through background mein chalta hai.
    """
    time.sleep(minutes * 60)

    with _lock:   # lock lo taaki safe access ho
        if ticket_id not in _active:
            return

        info = _active[ticket_id]

        if not info["resolved"]:
            print(f"\n  [ESCALATION TRIGGERED] {ticket_id}")
            send_escalation_email(info["ticket"])
            info["escalated"] = True
            info["status"]    = "ESCALATED"


def start_timer(ticket: dict, minutes: int = 2):
    """
    Naya ticket aaya — background escalation timer start karo.
    
    threading.Thread explain:
    - target = kaunsa function run karna hai
    - args   = us function ke arguments
    - daemon = True matlab: main app band ho toh ye thread bhi band ho
                            (zombie threads se bachao)
    """
    tid = ticket["ticket_id"]

    with _lock:
        _active[tid] = {
            "ticket":    ticket,
            "resolved":  False,
            "escalated": False,
            "status":    "OPEN",
            "minutes":   minutes
        }

    t = threading.Thread(
        target=_timer_thread,
        args=(tid, minutes),
        daemon=True
    )
    t.start()
    print(f"  [Timer] Started for {tid} — escalates in {minutes} min")


def mark_resolved(ticket_id: str) -> bool:
    """
    User ne 'Mark Resolved' button dabaya.
    Timer cancel nahi hota (thread rok nahi sakte)
    lekin resolved=True karke escalation block kar dete hain.
    """
    with _lock:
        if ticket_id in _active:
            _active[ticket_id]["resolved"] = True
            _active[ticket_id]["status"]   = "RESOLVED"
            print(f"  [Resolved] {ticket_id} — escalation blocked")
            return True
    return False


def get_status(ticket_id: str) -> str:
    """Current status return karo — OPEN, RESOLVED, ya ESCALATED."""
    with _lock:
        if ticket_id in _active:
            return _active[ticket_id]["status"]
    return "UNKNOWN"


def get_all_tickets() -> list:
    """Dashboard ke liye saare active tickets return karo."""
    with _lock:
        return [
            {**info["ticket"], "current_status": info["status"]}
            for info in _active.values()
        ]
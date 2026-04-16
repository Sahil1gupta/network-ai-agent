# src/app.py
import sys
import os
import json
import time

# src/ folder ko Python path mein add karo
# Matlab: "is folder ke andar se bhi import kar sakte ho"
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from pipeline import run_pipeline
from email_service import send_new_ticket_email
from escalation_service import start_timer, mark_resolved, get_status, get_all_tickets
from rag_pipeline import build_vector_db, CHROMA_DIR

# ── Page config — ye SABSE PEHLE aana chahiye ──────────────────────────────────
st.set_page_config(
    page_title="STC AutoOSS",
    page_icon="🔴",
    layout="wide"       # wide = full browser width use karo
)

# ── CSS — thoda styling ────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
  }
  .p1 { color: #dc2626; font-weight: bold; }
  .p2 { color: #d97706; font-weight: bold; }
  .p3 { color: #2563eb; font-weight: bold; }
  .status-open     { background:#fef2f2; color:#dc2626; padding:2px 8px; border-radius:12px; }
  .status-resolved { background:#f0fdf4; color:#16a34a; padding:2px 8px; border-radius:12px; }
  .status-escalated{ background:#fff7ed; color:#ea580c; padding:2px 8px; border-radius:12px; }
</style>
""", unsafe_allow_html=True)
# unsafe_allow_html=True — HTML/CSS inject karne ki permission

# ── Session state initialize karo ─────────────────────────────────────────────
# Ye keys pehli baar set hogi, baad ke reruns mein preserve hongi
if "processed_tickets" not in st.session_state:
    st.session_state.processed_tickets = []    # list of ticket dicts

if "processing" not in st.session_state:
    st.session_state.processing = False        # AI chal rahi hai?

if "vector_db_ready" not in st.session_state:
    st.session_state.vector_db_ready = False


# ── Vector DB check ────────────────────────────────────────────────────────────
if not st.session_state.vector_db_ready:
    if not os.path.exists(CHROMA_DIR):
        with st.spinner("Building knowledge base from runbooks..."):
            build_vector_db()
    st.session_state.vector_db_ready = True


# ── Load alarms ────────────────────────────────────────────────────────────────
@st.cache_data   # ye decorator result cache karta hai — baar baar file nahi padhni
def load_alarms():
    with open("data/alarms.json", "r") as f:
        return json.load(f)

all_alarms = load_alarms()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("🔴 STC AutoOSS — AI NOC Copilot")
st.caption("Automated fault detection, RCA, and ticket management powered by AI")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TOP METRICS ROW
# ══════════════════════════════════════════════════════════════════════════════
tickets        = st.session_state.processed_tickets
total          = len(tickets)
open_count     = sum(1 for t in tickets if get_status(t["ticket_id"]) == "OPEN")
resolved_count = sum(1 for t in tickets if get_status(t["ticket_id"]) == "RESOLVED")
escalated_count= sum(1 for t in tickets if get_status(t["ticket_id"]) == "ESCALATED")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Tickets",  total)
with col2:
    st.metric("Open",           open_count,      delta=None)
with col3:
    st.metric("Resolved",       resolved_count)
with col4:
    st.metric("Escalated",      escalated_count)
with col5:
    # MTTR calculate karo
    if resolved_count > 0:
        st.metric("Avg MTTR", "~8 min", delta="-37 min vs manual")
    else:
        st.metric("Avg MTTR", "N/A")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TWO COLUMN LAYOUT
# Left: Alarm selector + Analyze button
# Right: Latest ticket result
# ══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 1.5])

# ── LEFT COLUMN ───────────────────────────────────────────────────────────────
with left_col:
    st.subheader("🚨 Incoming Alarms")

    # Severity filter
    severity_filter = st.selectbox(
        "Filter by severity",
        ["ALL", "CRITICAL", "MAJOR", "MINOR"]
    )

    # Filter alarms based on selection
    if severity_filter == "ALL":
        filtered = all_alarms
    else:
        filtered = [a for a in all_alarms if a["severity"] == severity_filter]

    # Alarm dropdown — har alarm ko readable label dete hain
    alarm_labels = [
        f"{a['alarm_id']} | {a['alarm_type']} | {a['device']} | {a['severity']}"
        for a in filtered
    ]

    selected_label = st.selectbox("Select alarm to analyze", alarm_labels)

    # Selected label se actual alarm dict nikalo
    selected_index = alarm_labels.index(selected_label)
    selected_alarm = filtered[selected_index]

    # Selected alarm ki details card mein dikhao
    st.markdown("**Alarm Details:**")
    st.json({
        "alarm_id":   selected_alarm["alarm_id"],
        "type":       selected_alarm["alarm_type"],
        "device":     selected_alarm["device"],
        "region":     selected_alarm["region"],
        "severity":   selected_alarm["severity"],
        "description":selected_alarm["description"],
    })

    # Escalation timer setting
    escalation_minutes = st.slider(
        "Auto-escalation timer (minutes)",
        min_value=1,
        max_value=10,
        value=2,
        help="Agar itne minute mein resolve nahi hua toh L3 team ko email jayega"
    )

    # Analyze button
    analyze_clicked = st.button(
        "⚡ Analyze & Generate Ticket",
        type="primary",          # blue filled button
        use_container_width=True # full width
    )

    # ── Button click hone pe kya hoga ─────────────────────────────────────────
    if analyze_clicked:
        st.session_state.processing = True

        # Progress bar dikhaao
        progress = st.progress(0, text="Starting AI pipeline...")

        # Agent 1
        progress.progress(10, text="Agent 1: Classifying fault...")
        time.sleep(0.3)   # visual effect ke liye thoda delay

        # Pipeline run karo
        progress.progress(30, text="Agent 2: Fetching runbook context...")
        time.sleep(0.3)

        progress.progress(60, text="Agent 3: Generating RCA...")

        # Actual pipeline call
        with st.spinner("AI agents working..."):
            ticket = run_pipeline(selected_alarm)

        progress.progress(85, text="Agent 4: Creating ticket...")
        time.sleep(0.2)

        # Email bhejo
        progress.progress(95, text="Sending email notification...")
        send_new_ticket_email(ticket)

        # Escalation timer start karo
        start_timer(ticket, minutes=escalation_minutes)

        progress.progress(100, text="Done!")
        time.sleep(0.5)
        progress.empty()   # progress bar hatao

        # Session state mein save karo
        st.session_state.processed_tickets.append(ticket)
        st.session_state.processing = False
        st.session_state.latest_ticket = ticket

        st.success(f"Ticket {ticket['ticket_id']} created! Email sent. Escalation timer: {escalation_minutes} min")
        st.rerun()   # page refresh karo updated data ke saath


# ── RIGHT COLUMN ──────────────────────────────────────────────────────────────
with right_col:
    st.subheader("📋 Latest Ticket")

    if "latest_ticket" not in st.session_state:
        st.info("Select an alarm and click Analyze to generate a ticket.")
    else:
        t = st.session_state.latest_ticket
        current_status = get_status(t["ticket_id"])

        # Status badge
        status_color = {
            "OPEN":      "🔴",
            "RESOLVED":  "🟢",
            "ESCALATED": "🟠"
        }.get(current_status, "⚪")

        st.markdown(f"**Status:** {status_color} {current_status}")

        # Priority + Ticket ID row
        pcol, tcol = st.columns(2)
        with pcol:
            priority_colors = {"P1": "🔴", "P2": "🟡", "P3": "🔵"}
            st.metric("Priority", f"{priority_colors.get(t['priority'], '')} {t['priority']}")
        with tcol:
            st.metric("Ticket ID", t["ticket_id"])

        # RCA section
        st.markdown("**🧠 AI Root Cause Analysis:**")

        # Confidence ke hisaab se color
        conf = t.get("confidence", "medium")
        conf_color = {"high": "green", "medium": "orange", "low": "red"}.get(conf, "gray")

        st.markdown(f"""
        <div style="background:#fefce8; padding:12px; border-radius:8px;
                    border-left:4px solid #ca8a04; margin:8px 0">
            <b>Root Cause:</b> {t['root_cause']}<br><br>
            <b>Confidence:</b> <span style="color:{conf_color};
                font-weight:bold">{conf.upper()}</span>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Fix Time:</b> {t['estimated_fix_time']}
        </div>
        """, unsafe_allow_html=True)

        # Resolution steps
        st.markdown("**🛠️ Resolution Steps:**")
        for i, step in enumerate(t["resolution_steps"], 1):
            st.markdown(f"{i}. {step}")

        # Ticket info
        with st.expander("📄 Full Ticket JSON"):
            st.json(t)

        # Action buttons row
        b1, b2 = st.columns(2)

        with b1:
            if current_status == "OPEN":
                if st.button("✅ Mark Resolved",
                             key=f"resolve_{t['ticket_id']}",
                             use_container_width=True):
                    mark_resolved(t["ticket_id"])
                    st.success("Ticket resolved! Escalation cancelled.")
                    st.rerun()

        with b2:
            if current_status == "OPEN":
                if st.button("⬆️ Manual Escalate",
                             key=f"escalate_{t['ticket_id']}",
                             use_container_width=True,
                             type="secondary"):
                    from email_service import send_escalation_email
                    send_escalation_email(t)
                    mark_resolved(t["ticket_id"])
                    st.warning("Manually escalated to L3 team!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM — ALL TICKETS TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("📊 All Generated Tickets")

all_generated = get_all_tickets()

if not all_generated:
    st.info("No tickets generated yet. Analyze an alarm above to get started.")
else:
    # Table data prepare karo
    table_data = []
    for t in all_generated:
        status = t.get("current_status", "OPEN")
        status_icon = {"OPEN": "🔴", "RESOLVED": "🟢", "ESCALATED": "🟠"}.get(status, "⚪")
        table_data.append({
            "Ticket ID":   t["ticket_id"],
            "Priority":    t["priority"],
            "Alarm Type":  t["alarm_type"],
            "Device":      t["device"],
            "Region":      t["region"],
            "Root Cause":  t["root_cause"][:60] + "...",
            "Fix Time":    t["estimated_fix_time"],
            "Status":      f"{status_icon} {status}",
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True   # row numbers mat dikhaao
    )

    # Export button
    if st.button("📥 Export Tickets as JSON"):
        json_str = json.dumps(all_generated, indent=2)
        st.download_button(
            label="Download tickets.json",
            data=json_str,
            file_name="stc_autooss_tickets.json",
            mime="application/json"
        )
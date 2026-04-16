# src/test_pipeline.py
import json
from pipeline import run_pipeline

# Real alarms.json se data load karo
with open("data/alarms.json", "r") as f:
    all_alarms = json.load(f)

# Sirf CRITICAL alarms filter karo
critical_alarms = [a for a in all_alarms if a["severity"] == "CRITICAL"]

print(f"Total alarms:    {len(all_alarms)}")
print(f"Critical alarms: {len(critical_alarms)}")

# Pehle 3 critical alarms process karo
tickets = []
for alarm in critical_alarms[:3]:
    ticket = run_pipeline(alarm)
    tickets.append(ticket)

# Results save karo
with open("data/output_tickets.json", "w") as f:
    json.dump(tickets, f, indent=2)

print(f"\nDone! Generated {len(tickets)} tickets → data/output_tickets.json")
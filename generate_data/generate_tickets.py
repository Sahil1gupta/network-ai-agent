# generate_data/generate_tickets.py
import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

ALARM_TYPES = ["BGP_DOWN", "LINK_FAILURE", "HIGH_CPU", "PACKET_LOSS", "POWER_FAULT"]

DEVICES = (
    [f"CoreRouter-Riyadh-{i:02d}" for i in range(1, 6)] +
    [f"CoreRouter-Jeddah-{i:02d}"  for i in range(1, 4)] +
    [f"AccessSwitch-{i:03d}"       for i in range(1, 20)]
)

REGIONS = ["Riyadh", "Jeddah", "Dammam", "Mecca", "Medina", "Khobar"]

RESOLUTIONS = {
    "BGP_DOWN": [
        "Restarted BGP process after identifying peer IP config mismatch.",
        "Replaced failed fiber patch cable between core routers.",
        "Corrected ACL that was blocking BGP port 179.",
    ],
    "LINK_FAILURE": [
        "Replaced faulty SFP module on GigabitEthernet interface.",
        "Repaired physical cable damaged during maintenance window.",
        "Rebooted remote switch after detecting software wedge.",
    ],
    "HIGH_CPU": [
        "Blocked DDoS traffic via ACL. CPU normalized within 5 minutes.",
        "Disabled unnecessary SNMP polling reducing CPU by 40 percent.",
        "Upgraded router IOS to fix memory leak causing high CPU.",
    ],
    "PACKET_LOSS": [
        "Replaced degraded fiber causing intermittent signal loss.",
        "Adjusted QoS policy to prioritize VoIP traffic correctly.",
        "Fixed duplex mismatch on access switch port.",
    ],
    "POWER_FAULT": [
        "Replaced failed PSU-2 with spare unit from warehouse.",
        "Restored commercial power after UPS battery exhaustion.",
    ],
}

SEVERITY_MAP = {
    "BGP_DOWN":    "CRITICAL",
    "LINK_FAILURE": "MAJOR",
    "HIGH_CPU":    "MAJOR",
    "PACKET_LOSS": "MINOR",
    "POWER_FAULT": "CRITICAL",
}


def generate_tickets(count=40):
    tickets = []

    for i in range(count):
        alarm_type = random.choice(ALARM_TYPES)
        device     = random.choice(DEVICES)
        created    = datetime.now() - timedelta(days=random.randint(1, 90))
        resolved   = created + timedelta(minutes=random.randint(15, 180))
        resolution = random.choice(RESOLUTIONS[alarm_type])

        ticket = {
            "ticket_id":    f"INC-2026-{i+1:04d}",
            "alarm_type":   alarm_type,
            "device":       device,
            "region":       random.choice(REGIONS),
            "severity":     SEVERITY_MAP[alarm_type],
            "rca":          f"Root cause identified: {resolution}",
            "resolution":   resolution,
            "created_at":   created.isoformat(),
            "resolved_at":  resolved.isoformat(),
            "mttr_minutes": int((resolved - created).total_seconds() / 60),
            "status":       "RESOLVED",
            "engineer":     fake.name(),
        }
        tickets.append(ticket)

    return tickets


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    tickets = generate_tickets(40)

    with open("data/past_tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)

    print(f"Generated {len(tickets)} tickets → data/past_tickets.json")
    print("\nSample ticket:")
    print(json.dumps(tickets[0], indent=2))
# generate_data/generate_alarms.py
import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

ALARM_TYPES = {
    "BGP_DOWN": {
        "severities":        ["CRITICAL", "CRITICAL", "MAJOR"],
        "description":       "BGP session dropped with peer {peer_ip}",
        "affected_services": ["Internet", "MPLS VPN", "Enterprise Connectivity"]
    },
    "LINK_FAILURE": {
        "severities":        ["CRITICAL", "MAJOR"],
        "description":       "Physical link down on interface {interface}",
        "affected_services": ["Broadband", "Mobile Data", "Enterprise Leased Line"]
    },
    "HIGH_CPU": {
        "severities":        ["MAJOR", "MAJOR", "MINOR"],
        "description":       "CPU utilization at {cpu_pct}% on device {device}",
        "affected_services": ["Routing", "NAT", "Firewall Processing"]
    },
    "PACKET_LOSS": {
        "severities":        ["MAJOR", "MINOR"],
        "description":       "Packet loss {loss_pct}% detected on {interface}",
        "affected_services": ["VoIP", "Video Streaming", "Business Apps"]
    },
    "POWER_FAULT": {
        "severities":        ["CRITICAL"],
        "description":       "Power supply unit failure on {device}",
        "affected_services": ["All Services at Site"]
    },
}

DEVICES = (
    [f"CoreRouter-Riyadh-{i:02d}" for i in range(1, 6)] +
    [f"CoreRouter-Jeddah-{i:02d}"  for i in range(1, 4)] +
    [f"CoreRouter-Dammam-{i:02d}"  for i in range(1, 3)] +
    [f"AccessSwitch-{i:03d}"       for i in range(1, 20)] +
    [f"BTS-Site-{i:04d}"           for i in range(1, 30)]
)

REGIONS = ["Riyadh", "Jeddah", "Dammam", "Mecca", "Medina", "Khobar"]


def random_ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def random_interface():
    return f"GigabitEthernet{random.randint(0,3)}/{random.randint(0,47)}"


def fill_description(template, device):
    """
    Template string mein placeholders ko actual values se replace karo.
    Example:
      template = "CPU at {cpu_pct}% on {device}"
      output   = "CPU at 92% on CoreRouter-01"
    """
    return template.format(
        peer_ip=random_ip(),
        interface=random_interface(),
        device=device,
        cpu_pct=random.randint(85, 99),
        loss_pct=round(random.uniform(5, 40), 1),
    )


def generate_alarms(count=60):
    alarms    = []
    base_time = datetime.now() - timedelta(hours=24)

    for i in range(count):
        alarm_type = random.choice(list(ALARM_TYPES.keys()))
        props      = ALARM_TYPES[alarm_type]
        device     = random.choice(DEVICES)
        timestamp  = base_time + timedelta(minutes=random.randint(0, 1440))

        alarm = {
            "alarm_id":          f"ALM-{i+1:05d}",
            "alarm_type":        alarm_type,
            "device":            device,
            "region":            random.choice(REGIONS),
            "severity":          random.choice(props["severities"]),
            "description":       fill_description(props["description"], device),
            "affected_services": props["affected_services"],
            "timestamp":         timestamp.isoformat(),
            "acknowledged":      random.choice([True, False]),
            "source_ip":         random_ip(),
        }
        alarms.append(alarm)

    alarms.sort(key=lambda x: x["timestamp"])
    return alarms


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    alarms = generate_alarms(60)

    with open("data/alarms.json", "w") as f:
        json.dump(alarms, f, indent=2)

    print(f"Generated {len(alarms)} alarms → data/alarms.json")
    print("\nSample alarm:")
    print(json.dumps(alarms[0], indent=2))
# src/pipeline.py
import json
from agents import classify_fault, fetch_context, generate_rca, create_ticket


def run_pipeline(alarm: dict) -> dict:
    """
    Ek alarm dict leke charon agents sequence mein chalao.
    Input : alarm dict
    Output: complete incident ticket dict
    """
    print(f"\n{'='*55}")
    print(f"  Alarm: {alarm['alarm_id']} | {alarm['alarm_type']} | {alarm['severity']}")
    print(f"  Device: {alarm['device']} | Region: {alarm['region']}")
    print(f"{'='*55}")

    classification = classify_fault(alarm)
    context        = fetch_context(alarm, classification)
    rca            = generate_rca(alarm, classification, context)
    ticket         = create_ticket(alarm, classification, rca)

    return ticket


if __name__ == "__main__":
    # Ek sample alarm manually banao aur test karo
    sample_alarm = {
        "alarm_id":          "ALM-00001",
        "alarm_type":        "BGP_DOWN",
        "device":            "CoreRouter-Riyadh-02",
        "region":            "Riyadh",
        "severity":          "CRITICAL",
        "description":       "BGP session dropped with peer 10.45.2.1",
        "affected_services": ["Internet", "MPLS VPN"],
        "timestamp":         "2026-04-15T09:30:00",
        "acknowledged":      False,
        "source_ip":         "10.10.1.5"
    }

    ticket = run_pipeline(sample_alarm)

    print(f"\n{'='*55}")
    print("FINAL TICKET:")
    print(f"{'='*55}")
    print(json.dumps(ticket, indent=2))
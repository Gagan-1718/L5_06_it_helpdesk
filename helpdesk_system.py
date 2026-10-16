"""IT Helpdesk Ticket Allocation and Management System."""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

# Global state
tickets = {}
TICKET_COUNTER = 100
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "helpdesk@123")

def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Raise a new ticket, assign an ID, and log an audit trail entry."""
    global TICKET_COUNTER
    if audit_trail is None:
        audit_trail = []

    try:
        priority = int(urgency)
    except (ValueError, TypeError):
        priority = 3

    if priority < 1 or priority > 5:
        priority = max(1, min(5, priority))

    TICKET_COUNTER += 1
    tickets[TICKET_COUNTER] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": []
    }
    audit_trail.append(f"{user} raised #{TICKET_COUNTER} at {datetime.now()}")
    return TICKET_COUNTER

def assign_ticket(ticket_id, technician):
    """Assign an existing ticket to a technician."""
    if ticket_id in tickets:
        tickets[ticket_id]["tech"] = technician

def add_note(ticket_id, note):
    """Append a progress note to an existing ticket."""
    if ticket_id in tickets:
        tickets[ticket_id]["notes"].append(note)

def close_ticket(ticket_id, password):
    """Close and remove a ticket if authorized by the admin password."""
    if password == ADMIN_PASSWORD and ticket_id in tickets:
        del tickets[ticket_id]

def unresolved_high_priority():
    """Return a list of IDs for unassigned high-priority tickets."""
    result = []
    for t, ticket in tickets.items():
        if ticket["priority"] >= 4 and ticket["tech"] is None:
            result.append(t)
    return result

def ping_user_machine(hostname):
    """Ping a user machine securely using subprocess without shell."""
    if not isinstance(hostname, str) or not re.match(r"^[a-zA-Z0-9.-]+$", hostname):
        raise ValueError(f"Invalid hostname: {hostname}")

    ping_bin = shutil.which("ping") or "ping"
    count_flag = "-n" if sys.platform.startswith("win") else "-c"
    res = subprocess.run([ping_bin, count_flag, "1", hostname], check=False)
    return res.returncode

def save_tickets(file="tickets.json"):
    """Persist tickets dictionary to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(tickets))

def main():
    """Run the helpdesk ticket management workflow demonstration."""
    t1 = raise_ticket("anil", "printer", "5")
    _ = raise_ticket("meera", "wifi", "4")
    t3 = raise_ticket("joe", "vpn", "-7")
    assign_ticket(t1, "Tech-Kiran")
    add_note(999, "Called user")
    print("Unassigned high priority:", unresolved_high_priority())
    level = input("Urgency for a new laptop ticket (1-5, Enter for 3): ") or "3"
    raise_ticket("sana", "laptop", level)
    close_ticket(t3, ADMIN_PASSWORD)
    save_tickets()
    print("Open tickets:", list(tickets.keys()))

main()

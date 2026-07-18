"""
Static + simulated dynamic data for the StadionAI demo.
In a production deployment these would come from IoT sensors, ticketing APIs,
transit APIs, and a stadium CMS. For this hackathon prototype we simulate
realistic values so the GenAI layer has something meaningful to reason over.
"""

import random
from datetime import datetime, timedelta

STADIUM_NAME = "MetLife Stadium"
MATCH_INFO = {
    "fixture": "Quarter-Final — Match 58",
    "kickoff": "18:00 Local",
    "capacity": 82_500,
}

# ---- Wayfinding knowledge base (used as GenAI context / RAG-lite) ----
LOCATIONS = {
    "Gate 1": "North Plaza entrance, closest to Metro Station A. Bag check + metal detectors.",
    "Gate 2": "North Plaza entrance, express lane for accessible ticket holders.",
    "Gate 3": "East entrance, closest to shuttle bus drop-off zone.",
    "Gate 4": "East entrance, general admission, highest congestion pre-match.",
    "Gate 5": "South Plaza, VIP & hospitality entrance.",
    "Gate 6": "South Plaza, media and staff entrance (credential required).",
    "Gate 7": "West entrance, closest to accessible parking lot P3.",
    "Gate 8": "West entrance, family zone with stroller check.",
    "Section 100-119": "Lower bowl, reached via Gates 1-4, escalators A-D.",
    "Section 200-219": "Club level, reached via Gate 5, elevators E-F (credential/ticket scan).",
    "Section 300-345": "Upper bowl, reached via Gates 3, 4, 7, 8, escalators G-L.",
    "Accessible seating": "Located in Sections 108, 128, 218, 318 — reachable via elevators, staff on standby at each.",
    "First Aid": "Located behind Sections 112, 218, and 335. Marked with red cross signage.",
    "Prayer/Quiet room": "Located near Gate 5 concourse, Level 200.",
    "Nursing room": "Located near Gate 8 family zone.",
    "Lost & Found": "Guest Services desk, North Plaza near Gate 1.",
    "Parking - General": "Lots P1, P2, P6 — shuttle every 8 minutes to Gates 3/4.",
    "Parking - Accessible": "Lot P3, direct path to Gate 7.",
    "Metro/Transit": "Meadowlands Rail Station, 10 min walk to Gate 1, extra trains scheduled post-match.",
}

STAFF_ROLES = ["Steward", "Volunteer Guide", "Medical", "Security", "Transport Coordinator"]

INCIDENT_TEMPLATES = [
    ("Gate 4", "High congestion — queue exceeding 15 min wait"),
    ("Section 300-345", "Escalator G temporarily out of service"),
    ("Metro/Transit", "Rail delay of 6 minutes reported by transit authority"),
    ("Parking - General", "Lot P2 nearing capacity"),
    ("First Aid (Section 218)", "Minor medical assist in progress, cleared in 5 min"),
    ("Gate 1", "Bag check line moving normally"),
    ("Section 200-219", "Concession stand C7 out of stock — water only"),
]


def get_zones():
    """Simulated live crowd density per stadium zone (0-100)."""
    zones = [
        "Gate 1", "Gate 2", "Gate 3", "Gate 4",
        "Gate 5", "Gate 6", "Gate 7", "Gate 8",
        "Lower Bowl", "Club Level", "Upper Bowl",
        "North Concourse", "South Concourse",
    ]
    data = []
    for z in zones:
        density = random.randint(20, 98)
        if density >= 85:
            status = "critical"
        elif density >= 60:
            status = "busy"
        else:
            status = "normal"
        data.append({"zone": z, "density": density, "status": status})
    return data


def get_incidents(n=4):
    random.shuffle(INCIDENT_TEMPLATES)
    now = datetime.now()
    out = []
    for i, (loc, desc) in enumerate(INCIDENT_TEMPLATES[:n]):
        out.append({
            "time": (now - timedelta(minutes=random.randint(1, 40))).strftime("%H:%M"),
            "location": loc,
            "description": desc,
            "severity": random.choice(["low", "medium", "high"]),
        })
    return out


def get_weather():
    return {
        "condition": random.choice(["Clear", "Partly Cloudy", "Light Rain expected 2nd half"]),
        "temp_c": random.randint(22, 31),
        "advisory": random.choice([
            "None",
            "Hydration stations recommended at all gates",
            "Covered concourse areas may see overflow if rain begins",
        ]),
    }


def get_transport_status():
    return [
        {"mode": "Metro Rail", "status": random.choice(["On time", "6 min delay", "Extra service added"])},
        {"mode": "Shuttle Bus", "status": random.choice(["Running every 8 min", "Running every 12 min (high demand)"])},
        {"mode": "Rideshare Zone", "status": random.choice(["Normal wait", "15 min wait — high demand"])},
    ]


def build_context_block():
    """Serializes current simulated state into a compact text block for the LLM prompt."""
    zones = get_zones()
    busy = [z for z in zones if z["status"] in ("busy", "critical")]
    incidents = get_incidents()
    weather = get_weather()
    transport = get_transport_status()

    lines = [f"STADIUM: {STADIUM_NAME} | {MATCH_INFO['fixture']} | Kickoff {MATCH_INFO['kickoff']}"]
    lines.append("LIVE CROWD DENSITY (busy/critical zones):")
    for z in busy:
        lines.append(f"  - {z['zone']}: {z['density']}% ({z['status']})")
    lines.append("ACTIVE INCIDENTS/ADVISORIES:")
    for inc in incidents:
        lines.append(f"  - [{inc['time']}] {inc['location']}: {inc['description']} (severity: {inc['severity']})")
    lines.append(f"WEATHER: {weather['condition']}, {weather['temp_c']}°C. Advisory: {weather['advisory']}")
    lines.append("TRANSPORT:")
    for t in transport:
        lines.append(f"  - {t['mode']}: {t['status']}")
    lines.append("WAYFINDING KNOWLEDGE BASE:")
    for k, v in LOCATIONS.items():
        lines.append(f"  - {k}: {v}")
    return "\n".join(lines)

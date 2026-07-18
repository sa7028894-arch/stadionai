import os
import streamlit as st
from groq import Groq
import stadium_data as sd

st.set_page_config(page_title="StadionAI — Smart Stadium Copilot", page_icon="🏟️", layout="wide")

# ---------------------------------------------------------------------------
# GenAI client setup
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY) if API_KEY else None
MODEL = "llama-3.1-8b-instant"


def ask_ai(system_prompt: str, user_prompt: str, temperature: float = 0.4, max_tokens: int = 500) -> str:
    if client is None:
        return ("⚠️ No GROQ_API_KEY configured. Add your key in Streamlit Cloud → Settings → "
                "Secrets as GROQ_API_KEY = \"your_key\" to enable live AI responses. "
                "(This is a placeholder response so the UI still demos correctly.)")
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI request failed: {e}"


# ---------------------------------------------------------------------------
# Styling — "floodlit night match" design system
# Palette: night-navy pitch, turf green, floodlight amber, chalk white, scoreboard red
# Type: Oswald (scoreboard/signage display), Inter (body), JetBrains Mono (data feed)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --night:      #0B1220;
    --surface:    #121C30;
    --surface-2:  #17233B;
    --line:       #223046;
    --turf:       #1F9D55;
    --turf-glow:  #29C46B;
    --amber:      #F5B942;
    --chalk:      #F3F6F1;
    --slate:      #8291AC;
    --red:        #E8483C;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 900px 500px at 15% -10%, rgba(245,185,66,0.10), transparent 60%),
        radial-gradient(ellipse 900px 500px at 85% -10%, rgba(31,157,85,0.12), transparent 60%),
        var(--night);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--chalk); }
h1, h2, h3, .stadium-display { font-family: 'Oswald', sans-serif; letter-spacing: 0.02em; }
code, .mono { font-family: 'JetBrains Mono', monospace; }

.hero {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
    border: 1px solid var(--line);
    border-top: 3px solid var(--turf);
    border-radius: 10px;
    padding: 22px 28px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}
.hero-title {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 2.1rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--chalk);
    margin: 0;
    line-height: 1.1;
}
.hero-title span { color: var(--turf-glow); }
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    color: var(--slate);
    font-size: 0.85rem;
    margin-top: 6px;
    letter-spacing: 0.03em;
}
.hero-clock { text-align: right; border-left: 1px solid var(--line); padding-left: 20px; }
.hero-clock .label { font-size: 0.7rem; color: var(--slate); letter-spacing: 0.08em; text-transform: uppercase; }
.hero-clock .value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; color: var(--amber); }

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Oswald', sans-serif;
    font-weight: 500;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    color: var(--slate);
    background: transparent;
    border-radius: 6px 6px 0 0;
    padding: 10px 16px;
}
.stTabs [aria-selected="true"] {
    color: var(--chalk) !important;
    background: var(--surface) !important;
    border-bottom: 2px solid var(--turf-glow) !important;
}

.stButton > button {
    background: var(--turf);
    color: var(--night);
    border: none;
    font-weight: 600;
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
    transition: background 0.15s ease, transform 0.1s ease;
}
.stButton > button:hover { background: var(--turf-glow); transform: translateY(-1px); }

.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    color: var(--chalk) !important;
    border-radius: 6px !important;
}

.seat-tile {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 12px;
    margin-bottom: 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.seat-tile.normal   { border-color: var(--turf); box-shadow: inset 0 0 0 1px rgba(31,157,85,0.15); }
.seat-tile.busy     { border-color: var(--amber); box-shadow: 0 0 14px rgba(245,185,66,0.25); }
.seat-tile.critical { border-color: var(--red); box-shadow: 0 0 18px rgba(232,72,60,0.35); animation: pulse-glow 1.8s ease-in-out infinite; }
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 10px rgba(232,72,60,0.25); }
    50%      { box-shadow: 0 0 22px rgba(232,72,60,0.55); }
}
.seat-tile .zone { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--slate); text-transform: uppercase; letter-spacing: 0.05em; }
.seat-tile .density { font-family: 'Oswald', sans-serif; font-size: 1.9rem; font-weight: 700; margin: 4px 0; color: var(--chalk); }
.seat-tile .status-tag { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.seat-tile.normal .status-tag   { color: var(--turf-glow); }
.seat-tile.busy .status-tag     { color: var(--amber); }
.seat-tile.critical .status-tag { color: var(--red); }

.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.68rem; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; font-family:'JetBrains Mono',monospace; }
.pill-high   { background:rgba(232,72,60,0.15); color:#F0796F; border:1px solid rgba(232,72,60,0.4); }
.pill-medium { background:rgba(245,185,66,0.15); color:var(--amber); border:1px solid rgba(245,185,66,0.4); }
.pill-low    { background:rgba(31,157,85,0.15); color:var(--turf-glow); border:1px solid rgba(31,157,85,0.4); }

[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-left: 3px solid var(--turf-glow) !important;
    border-radius: 6px !important;
}

.quickfacts { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }
.quickfacts h4 { font-family:'Oswald',sans-serif; text-transform:uppercase; font-size:0.85rem; letter-spacing:0.06em; color:var(--amber); margin-top:0; }

footer, #MainMenu { visibility: hidden; }
.stadium-footer {
    font-family: 'JetBrains Mono', monospace;
    color: var(--slate);
    font-size: 0.75rem;
    text-align: center;
    border-top: 1px solid var(--line);
    padding-top: 14px;
    margin-top: 30px;
    letter-spacing: 0.03em;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
    <div>
        <div class="hero-title">STADION<span>AI</span></div>
        <div class="hero-sub">GENAI COPILOT · SMART STADIUMS &amp; TOURNAMENT OPS</div>
    </div>
    <div class="hero-clock">
        <div class="label">{sd.MATCH_INFO['fixture']}</div>
        <div class="value">⏱ {sd.MATCH_INFO['kickoff']}</div>
        <div class="label">{sd.STADIUM_NAME} · CAP {sd.MATCH_INFO['capacity']:,}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if client is None:
    st.info("Running in demo mode (no GROQ_API_KEY set) — UI and logic are fully functional, "
            "AI responses are placeholders until a key is added.", icon="ℹ️")

tabs = st.tabs([
    "🧭 Fan Navigator",
    "👥 Crowd & Safety",
    "🌐 Multilingual Assistant",
    "📋 Ops Briefing (Staff)",
    "♿ Accessibility Mode",
])

# ---------------------------------------------------------------------------
# TAB 1 — Fan Navigator
# ---------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Ask for directions, facilities, or anything about the venue")
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input("e.g. \"How do I get to Section 218 from Gate 3?\" or \"Where's the nearest first aid?\"",
                               key="nav_query")
        if st.button("Ask", key="nav_btn") and query:
            context = sd.build_context_block()
            system = ("You are StadionAI, a helpful, concise wayfinding assistant for fans at a FIFA World Cup "
                      "stadium. Use ONLY the venue data provided to answer. Give clear, short, step-by-step "
                      "directions or facts. If something isn't in the data, say you'll connect them to a steward.")
            with st.spinner("Thinking..."):
                answer = ask_ai(system, f"VENUE DATA:\n{context}\n\nFAN QUESTION: {query}")
            st.success(answer)
    with col2:
        facts_html = "<div class='quickfacts'><h4>Quick facts</h4><ul style='padding-left:18px;margin:0'>"
        for k in ["Gate 1", "Accessible seating", "First Aid", "Lost & Found"]:
            facts_html += f"<li style='margin-bottom:8px'><b>{k}</b>: {sd.LOCATIONS[k]}</li>"
        facts_html += "</ul></div>"
        st.markdown(facts_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2 — Crowd & Safety
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Live crowd density (simulated feed)")
    st.caption("Each tile is a stadium zone — glow intensity mirrors real crowd pressure, like floodlit seating blocks at night.")
    zones = sd.get_zones()
    cols = st.columns(4)
    for i, z in enumerate(zones):
        with cols[i % 4]:
            st.markdown(f"""<div class="seat-tile {z['status']}">
                <div class="zone">{z['zone']}</div>
                <div class="density">{z['density']}%</div>
                <div class="status-tag">{z['status']}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:28px'>Active incidents</h3>", unsafe_allow_html=True)
    for inc in sd.get_incidents():
        pill_class = f"pill-{inc['severity']}"
        st.markdown(
            f"<div style='padding:8px 0;border-bottom:1px solid var(--line)'>"
            f"<span class='mono' style='color:var(--slate)'>{inc['time']}</span> "
            f"<b>{inc['location']}</b> — {inc['description']} "
            f"<span class='pill {pill_class}'>{inc['severity']}</span></div>",
            unsafe_allow_html=True)

    if st.button("🤖 Generate AI crowd-safety advisory"):
        context = sd.build_context_block()
        system = ("You are an operations AI for stadium safety. Given live zone density and incidents, "
                  "write a short (4-6 bullet) actionable advisory for the ops control room: which zones need "
                  "attention, suggested crowd redirection, and any escalation recommendation.")
        with st.spinner("Analyzing live feed..."):
            advisory = ask_ai(system, context)
        st.warning(advisory)

# ---------------------------------------------------------------------------
# TAB 3 — Multilingual Assistant
# ---------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Multilingual fan assistant")
    st.caption("Ask in any language — the AI detects it and replies in the same language.")
    lang_query = st.text_area("Type your question in your own language",
                               placeholder="¿Dónde está la puerta 5? / Où sont les toilettes accessibles ? / स्टेडियम में पानी कहाँ मिलेगा?")
    if st.button("Send", key="lang_btn") and lang_query:
        context = sd.build_context_block()
        system = ("You are StadionAI's multilingual assistant. Detect the language of the user's message and "
                  "reply fluently in THAT SAME language, using only the venue data given. Keep it concise and warm.")
        with st.spinner("Translating & thinking..."):
            reply = ask_ai(system, f"VENUE DATA:\n{context}\n\nFAN MESSAGE: {lang_query}")
        st.success(reply)

# ---------------------------------------------------------------------------
# TAB 4 — Ops Briefing for staff/volunteers
# ---------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Auto-generated operational intelligence briefing")
    st.caption("For stewards, volunteers, and venue staff — refresh anytime for a live situational summary.")
    role = st.selectbox("Your role", sd.STAFF_ROLES)
    if st.button("Generate briefing"):
        context = sd.build_context_block()
        system = (f"You are an operations AI generating a shift briefing for a stadium {role}. "
                  "Summarize the current situation in 5-8 crisp bullet points relevant to their role: "
                  "crowd hotspots, incidents needing attention, weather/transport factors, and one "
                  "recommended priority action.")
        with st.spinner("Compiling briefing..."):
            briefing = ask_ai(system, context)
        st.info(briefing)

    with st.expander("Raw live data feed (for reference)"):
        st.text(sd.build_context_block())

# ---------------------------------------------------------------------------
# TAB 5 — Accessibility Mode
# ---------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Accessibility-first guidance")
    need = st.selectbox("I need help with...", [
        "Wheelchair accessible route",
        "Sensory-friendly quiet space",
        "Nursing room",
        "Accessible parking & drop-off",
        "Other accessibility request",
    ])
    extra = st.text_input("Any extra detail? (optional)")
    if st.button("Get guidance"):
        context = sd.build_context_block()
        system = ("You are StadionAI's accessibility assistant. Give warm, plain-language, step-by-step "
                  "guidance using only the venue data provided. Prioritize clarity and reassurance.")
        with st.spinner("Preparing guidance..."):
            answer = ask_ai(system, f"VENUE DATA:\n{context}\n\nACCESSIBILITY NEED: {need}. Extra detail: {extra}")
        st.success(answer)

st.markdown(
    "<div class='stadium-footer'>STADIONAI · GENAI-POWERED STADIUM OPERATIONS COPILOT · "
    "BUILT FOR PROMPTWARS CHALLENGE 4 — SMART STADIUMS &amp; TOURNAMENT OPERATIONS (FIFA WORLD CUP 2026)</div>",
    unsafe_allow_html=True)

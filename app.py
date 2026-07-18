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
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.metric-card {background:#111827;border-radius:12px;padding:16px;color:white;text-align:center;}
.status-critical {color:#ef4444;font-weight:700;}
.status-busy {color:#f59e0b;font-weight:700;}
.status-normal {color:#10b981;font-weight:700;}
.pill {display:inline-block;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:600;}
.pill-high{background:#fee2e2;color:#b91c1c;}
.pill-medium{background:#fef3c7;color:#92400e;}
.pill-low{background:#dcfce7;color:#166534;}
</style>
""", unsafe_allow_html=True)

st.title("🏟️ StadionAI — GenAI Copilot for Smart Stadiums")
st.caption(f"{sd.STADIUM_NAME} · {sd.MATCH_INFO['fixture']} · Kickoff {sd.MATCH_INFO['kickoff']} · Capacity {sd.MATCH_INFO['capacity']:,}")

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
        st.markdown("**Quick facts**")
        for k in ["Gate 1", "Accessible seating", "First Aid", "Lost & Found"]:
            st.markdown(f"- **{k}**: {sd.LOCATIONS[k]}")

# ---------------------------------------------------------------------------
# TAB 2 — Crowd & Safety
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Live crowd density (simulated feed)")
    zones = sd.get_zones()
    cols = st.columns(4)
    for i, z in enumerate(zones):
        with cols[i % 4]:
            css_class = f"status-{z['status']}"
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:0.85rem;opacity:0.8">{z['zone']}</div>
                <div style="font-size:1.6rem;font-weight:700">{z['density']}%</div>
                <div class="{css_class}">{z['status'].upper()}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("### Active incidents")
    for inc in sd.get_incidents():
        pill_class = f"pill-{inc['severity']}"
        st.markdown(f"`{inc['time']}` **{inc['location']}** — {inc['description']} "
                    f"<span class='pill {pill_class}'>{inc['severity']}</span>", unsafe_allow_html=True)

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

st.markdown("---")
st.caption("StadionAI · GenAI-powered stadium operations copilot · Built for PromptWars Challenge 4 — "
           "Smart Stadiums & Tournament Operations (FIFA World Cup 2026)")

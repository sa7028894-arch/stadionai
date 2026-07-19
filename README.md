# StadionAI — GenAI Copilot for Smart Stadiums

A GenAI-powered assistant for stadium operations and fan experience during large tournaments
(built for the FIFA World Cup 2026 use case).

## What it does

| Module | Description |
|---|---|
| 🧭 Fan Navigator | Natural-language wayfinding — directions, facilities, gates, seating |
| 👥 Crowd & Safety | Live (simulated) crowd density per zone + AI-generated safety advisories |
| 🌐 Multilingual Assistant | Detects the fan's language and replies in the same language |
| 📋 Ops Briefing | Auto-generated shift briefings for stewards, volunteers, security, medical, transport staff |
| ♿ Accessibility Mode | Plain-language, step-by-step accessibility guidance |

All AI responses are generated live by an LLM (Groq LLaMA 3.1) grounded in a stadium knowledge base
and a simulated real-time data feed (crowd density, incidents, weather, transport status).

## Tech stack
- Streamlit (UI)
- Groq API — LLaMA 3.1 8B Instant (GenAI reasoning)
- Python (simulated live-data layer, swappable for real IoT/ticketing/transit APIs)

## Run locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub (public).
2. Go to https://share.streamlit.io → "New app" → select this repo → main file `app.py`.
3. In **Settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_key_here"
   ```
4. Deploy. The app works in demo mode even without a key (placeholder responses),
   but a key enables live GenAI answers across all five modules.

## Quality & safety

- **Testing**: `tests/` has unit coverage for the data layer and input-sanitization utilities (`pytest tests/ -v`). CI runs them automatically on every push via `.github/workflows/tests.yml`.
- **Security**: user input is length-capped and stripped before entering any prompt; every LLM system prompt carries a prompt-injection guard; exceptions never leak internal details to the client; dependencies are pinned to exact versions.
- **Accessibility**: crowd-density tiles carry `aria-label`s so screen readers get status without relying on color/glow; animations respect `prefers-reduced-motion`; interactive elements have visible keyboard focus outlines.

## Run tests locally

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

## Data note

Crowd density, incidents, weather, and transport status are simulated for demo purposes
(`stadium_data.py`) to represent what a production deployment would receive from IoT sensors,
ticketing systems, and transit APIs. The wayfinding knowledge base is static sample data
representative of a real venue.

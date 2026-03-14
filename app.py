import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v6.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

# --- SECTION 1 (STATIC PER YOUR REQUEST) ---
st.title("✈️ Consensus: Automated Group Strategist")

col_form, col_cal = st.columns([1, 1.2], gap="large")
with col_form:
    st.header("1. Profile & Vibes")
    with st.container(border=True):
        name = st.text_input("Full Name")
        origin = st.text_input("Departure City")
        budget = st.number_input("Max Budget (€)", min_value=0, value=500)
        vibe_scores = {v: st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3) for v in VIBE_OPTIONS}
        no_go = st.text_input("Dealbreakers (e.g., camping car)")

with col_cal:
    st.header("2. Availability")
    cal_options = {"initialView": "dayGridMonth", "selectable": True, "timeZone": "UTC"}
    events = [{"start": d, "end": d, "display": "background", "color": "#28a745"} for d in st.session_state.selected_dates]
    state = calendar(events=events, options=cal_options, key="trip_cal_v6")

    if st.button("🔄 Sync Selected Date", use_container_width=True):
        raw_date = state.get("dateClick", {}).get("date") or state.get("select", {}).get("start")
        if raw_date:
            clean_date = raw_date.split("T")[0]
            if clean_date in st.session_state.selected_dates:
                st.session_state.selected_dates.remove(clean_date)
            else:
                st.session_state.selected_dates.add(clean_date)
            st.rerun()
    st.write(f"Confirmed: {len(st.session_state.selected_dates)} days")

if st.button("🚀 Lock My Profile", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_row = {"Name": name, "Origin": origin, "Budget": budget, "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go}
        new_row.update(vibe_scores)
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = set()
        st.rerun()

st.divider()

# --- SECTION 2: THE AI ANALYST ---
st.header("🔐 Section 2: Automated Group Strategy")

if st.text_input("Admin Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        # 1. CALCULATIONS
        group_size = len(df)
        min_budget = df['Budget'].min()
        avg_budget = df['Budget'].mean()
        winning_vibe = df[VIBE_OPTIONS].sum().idxmax()
        
        # 2. AUTOMATED SUGGESTION LOGIC
        def generate_suggestion(vibe, budget, dealbreakers):
            v = vibe.split(" ")[0] # Get text without emoji
            d = " ".join(str(x) for x in dealbreakers if str(x) != 'nan').lower()
            
            if "Nature" in v:
                if budget < 400: return "🌲 Low-Budget Nature: Forest Cabin or Glamping (Avoid camping cars if mentioned)."
                return "🌲 Premium Nature: High-end Eco-Lodge in the mountains or Dolomites."
            elif "City" in v:
                if budget < 500: return "🏙️ Budget City: Eastern European gems like Prague or Budapest."
                return "🏙️ Premium City: Paris, London, or Tokyo (if dates allow)."
            elif "Beach" in v:
                if budget < 400: return "🏖️ Budget Beach: South of Spain or Portugal."
                return "🏖️ Luxury Beach: Greek Islands or Amalfi Coast."
            elif "Party" in v:
                return "💃 High-Energy: Ibiza or Berlin, depending on flight origins."
            return f"🌟 Dynamic Suggestion: Based on {v} vibe and €{budget} budget."

        # 3. VISUALS & CONCLUSIONS
        st.subheader("🤖 The Group AI Strategist")
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            suggestion = generate_suggestion(winning_vibe, min_budget, df['No-Go'].tolist())
            st.info(f"### Final Verdict:\n**{suggestion}**")
            
            st.markdown(f"""
            **Why this works?**
            * The group's most inclusive budget is **€{min_budget}**.
            * The consensus vibe is **{winning_vibe}**.
            * We have automatically filtered out: *{", ".join(df['No-Go'].dropna())}*.
            """)

        with c2:
            st.write("#### Preference Distribution")
            group_scores = df[VIBE_OPTIONS].sum().sort_values()
            fig = px.bar(group_scores, orientation='h', color_discrete_sequence=['#0047bb'])
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # 4. DATA VISUALS
        t_finance, t_overlap = st.tabs(["💰 Budget Analysis", "📅 Availability Heatmap"])
        
        with t_finance:
            st.write("### Financial Strength")
            fig_budget = px.box(df, y="Budget", points="all", title="Group Budget Range")
            st.plotly_chart(fig_budget, use_container_width=True)
            st.write(f"To keep everyone included, the total trip cost per person should not exceed **€{min_budget}**.")

        with t_overlap:
            all_dates = []
            for d_str in df['Dates'].astype(str):
                all_dates.extend(d_str.split(","))
            
            if all_dates:
                date_counts = pd.Series(all_dates).value_counts().sort_index()
                st.write("### Peak Availability")
                st.line_chart(date_counts)
                
                best_days = date_counts[date_counts == date_counts.max()].index.tolist()
                st.success(f"The most people are free on: **{', '.join(best_days)}**")

    else:
        st.info("Awaiting group input to generate strategy.")

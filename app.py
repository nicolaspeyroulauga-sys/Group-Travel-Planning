import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v3.csv"

# 7 Expanded Trip Styles
VIBE_OPTIONS = [
    "City Break 🏙️", 
    "Nature & Hiking 🌲", 
    "Luxury & Spa 💎", 
    "Party & Nightlife 💃", 
    "Road Trip 🚗",
    "Ski & Snow ❄️",
    "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

# Initialize Session State
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = []

st.title("✈️ Consensus: The Ultimate Group Architect")

# --- SECTION 1: USER ENTRY ---
st.header("1. Personal Travel Profile")
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    with st.container(border=True):
        name = st.text_input("Full Name")
        origin = st.text_input("Flying From (City)")
        budget = st.number_input("Maximum Budget ($)", min_value=0, value=800)
        
        st.write("### ⭐️ Rate Trip Styles (1-5)")
        vibe_scores = {}
        for v in VIBE_OPTIONS:
            vibe_scores[v] = st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3)
        
        no_go = st.text_input("Any Dealbreakers? (e.g. No tents)")

with col_cal:
    st.write("### 📅 Availability (Click to Toggle)")
    # Using a slightly different calendar config to improve click reliability
    cal_options = {
        "initialView": "dayGridMonth",
        "selectable": True,
        "unselectAuto": False,
    }
    
    # We use 'background' type events to highlight selected dates clearly
    events = [{"start": d, "end": d, "display": "background", "color": "#28a745"} for d in st.session_state.selected_dates]
    
    state = calendar(events=events, options=cal_options, key="trip_cal_v3")

    # Fixed Logic: Capture 'select' and 'dateClick' for better compatibility
    if state.get("dateClick"):
        clicked = state["dateClick"]["date"].split("T")[0]
        if clicked in st.session_state.selected_dates:
            st.session_state.selected_dates.remove(clicked)
        else:
            st.session_state.selected_dates.append(clicked)
        st.rerun()

    if st.session_state.selected_dates:
        st.success(f"Confirmed: {len(st.session_state.selected_dates)} days selected.")
        if st.button("Clear All Dates"):
            st.session_state.selected_dates = []
            st.rerun()

if st.button("🚀 Lock In My Preferences", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_data = {
            "Name": name, "Origin": origin, "Budget": budget, 
            "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go
        }
        new_data.update(vibe_scores)
        pd.DataFrame([new_data]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = [] 
        st.balloons()
        st.success("Added! Check the Results section below.")
    else:
        st.error("Missing Name or Dates!")

st.divider()

# --- SECTION 2: THE BRAIN (ADMIN) ---
st.header("🔐 2. Group Intelligence")
if st.text_input("Enter Group Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        t_vibe, t_dates, t_finance = st.tabs(["🏆 Winning Vibe", "📅 Overlap Analysis", "💰 Group Finance"])
        
        with t_vibe:
            scores = df[VIBE_OPTIONS].sum().sort_values(ascending=False)
            winner = scores.index[0]
            st.write(f"### The Winner: {winner}")
            st.bar_chart(scores, color="#0047bb")

        with t_dates:
            # Finding overlaps
            all_date_sets = [set(str(d).split(",")) for d in df['Dates']]
            common = set.intersection(*all_date_sets)
            
            if common:
                st.success(f"Perfect Overlap: {sorted(list(common))}")
            else:
                # Show heatmap of popular dates
                all_raw = [d for sub in [str(x).split(",") for x in df['Dates']] for d in sub]
                date_counts = pd.Series(all_raw).value_counts().reset_index()
                date_counts.columns = ['Date', 'Votes']
                st.write("### Most Popular Dates")
                st.table(date_counts.head(5))

        with t_finance:
            st.subheader("Accommodation Budget Planner")
            total_house_cost = st.number_input("Total House/Villa Price ($)", value=2000)
            per_person = total_house_cost / len(df)
            
            st.metric("Cost per Person", f"${per_person:,.2f}")
            
            # Check who can't afford it
            broke_members = df[df['Budget'] < per_person]['Name'].tolist()
            if broke_members:
                st.warning(f"⚠️ This exceeds the budget for: {', '.join(broke_members)}")
            else:
                st.success("✅ Everyone can afford this!")

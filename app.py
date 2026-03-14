import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v4.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

# Initialize Session State
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set() # Using a set prevents duplicates automatically

st.title("✈️ Consensus: Group Decision Engine")

# --- SECTION 1: USER ENTRY ---
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    st.header("1. Profile & Vibes")
    with st.container(border=True):
        name = st.text_input("Full Name")
        origin = st.text_input("Flying From")
        budget = st.number_input("Max Budget ($)", min_value=0, value=800)
        
        st.write("---")
        st.write("### ⭐️ Rate Trip Styles")
        vibe_scores = {}
        for v in VIBE_OPTIONS:
            vibe_scores[v] = st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3)
        
        no_go = st.text_input("Any Dealbreakers?")

with col_cal:
    st.header("2. Availability")
    st.info("Step 1: Click all days you are free. \n\nStep 2: Click 'Confirm Selection' below the calendar.")
    
    cal_options = {
        "initialView": "dayGridMonth",
        "selectable": True,
        "selectMirror": True,
        "unselectAuto": False,
    }
    
    # We display the dates as "events" so they turn green once confirmed
    calendar_events = [
        {"start": d, "end": d, "display": "background", "color": "#28a745"} 
        for d in st.session_state.selected_dates
    ]
    
    # Render Calendar
    state = calendar(events=calendar_events, options=cal_options, key="trip_cal_v4")

    # SYNC BUTTON: This is the fix. It forces Streamlit to read the calendar state.
    if st.button("✅ Confirm/Toggle Selected Dates", use_container_width=True):
        # Check both 'dateClick' (single day) and 'select' (ranges)
        new_date = None
        if state.get("dateClick"):
            new_date = state["dateClick"]["date"].split("T")[0]
        elif state.get("select"):
            new_date = state["select"]["start"].split("T")[0]
            
        if new_date:
            if new_date in st.session_state.selected_dates:
                st.session_state.selected_dates.remove(new_date)
            else:
                st.session_state.selected_dates.add(new_date)
            st.rerun()

    # Display confirmed dates
    if st.session_state.selected_dates:
        sorted_dates = sorted(list(st.session_state.selected_dates))
        st.write(f"**Confirmed Dates:** {', '.join(sorted_dates)}")
        if st.button("Clear All"):
            st.session_state.selected_dates = set()
            st.rerun()

st.write("---")
if st.button("🚀 Submit My Full Profile to the Group", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_row = {
            "Name": name, "Origin": origin, "Budget": budget, 
            "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go
        }
        new_row.update(vibe_scores)
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = set()
        st.balloons()
        st.success("Profile Locked! Scroll down for results.")
    else:
        st.error("Please provide your name and confirm at least one date!")

# --- SECTION 2: RESULTS ---
st.header("🔐 Group Results")
if st.text_input("Group Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        t_vibe, t_dates, t_finance = st.tabs(["🏆 Winning Vibe", "📅 Best Dates", "💰 Finance Check"])
        
        with t_vibe:
            group_scores = df[VIBE_OPTIONS].sum().sort_values(ascending=False)
            st.write(f"### Current Group Leader: {group_scores.index[0]}")
            st.bar_chart(group_scores)
            
        with t_dates:
            # Simple list of most popular dates
            all_dates = []
            for d_str in df['Dates'].astype(str):
                all_dates.extend(d_str.split(","))
            
            if all_dates:
                date_counts = pd.Series(all_dates).value_counts().nlargest(5)
                st.write("### Top 5 Most Popular Dates")
                st.table(date_counts)

        with t_finance:
            st.subheader("Total Group Budget: ${:,.2f}".format(df['Budget'].sum()))
            avg_budget = df['Budget'].mean()
            st.write(f"Average Individual Budget: ${avg_budget:,.2f}")

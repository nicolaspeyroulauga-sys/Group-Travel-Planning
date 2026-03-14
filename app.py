import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar
from datetime import datetime

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v5.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

st.title("✈️ Consensus: The Ultimate Group Architect")

# --- SECTION 1: USER ENTRY ---
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    st.header("1. Profile & Vibes")
    with st.container(border=True):
        name = st.text_input("Full Name")
        origin = st.text_input("Departure City")
        budget = st.number_input("Max Budget ($)", min_value=0, value=800)
        
        st.write("### ⭐️ Rate Trip Styles")
        vibe_scores = {}
        for v in VIBE_OPTIONS:
            vibe_scores[v] = st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3)
        
        no_go = st.text_input("Any Dealbreakers?")

with col_cal:
    st.header("2. Availability")
    st.info("Click a date, then click 'Sync' to confirm. (Fixes the 1-day offset bug)")
    
    cal_options = {
        "initialView": "dayGridMonth",
        "selectable": True,
        "timeZone": "UTC", # Force UTC to prevent local shifting
    }
    
    calendar_events = [
        {"start": d, "end": d, "display": "background", "color": "#28a745"} 
        for d in st.session_state.selected_dates
    ]
    
    state = calendar(events=calendar_events, options=cal_options, key="trip_cal_v5")

    # FIXED CALENDAR LOGIC
    if st.button("🔄 Sync/Toggle Selected Date", use_container_width=True):
        raw_date = None
        # Priority 1: DateClick
        if state.get("dateClick"):
            raw_date = state["dateClick"]["date"]
        # Priority 2: Selection
        elif state.get("select"):
            raw_date = state["select"]["start"]
            
        if raw_date:
            # THE FIX: We split the string at 'T' to get ONLY the date (YYYY-MM-DD) 
            # and ignore any time-offset math.
            clean_date = raw_date.split("T")[0]
            
            if clean_date in st.session_state.selected_dates:
                st.session_state.selected_dates.remove(clean_date)
            else:
                st.session_state.selected_dates.add(clean_date)
            st.rerun()

    if st.session_state.selected_dates:
        sorted_dates = sorted(list(st.session_state.selected_dates))
        st.write(f"**Confirmed:** {', '.join(sorted_dates)}")
        if st.button("Clear Selection"):
            st.session_state.selected_dates = set()
            st.rerun()

st.write("---")
if st.button("🚀 Lock My Profile", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_row = {
            "Name": name, "Origin": origin, "Budget": budget, 
            "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go
        }
        new_row.update(vibe_scores)
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = set()
        st.balloons()
        st.success("Profile Saved!")
    else:
        st.error("Missing Name or Dates!")

# --- SECTION 2: THE BRAIN ---
st.header("🔐 Group Insights")
if st.text_input("Group Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        t_vibe, t_dates, t_dest = st.tabs(["🏆 Strategy", "📅 Schedule", "📍 City Poll"])
        
        with t_vibe:
            group_scores = df[VIBE_OPTIONS].sum().sort_values(ascending=False)
            st.subheader(f"Recommended Style: {group_scores.index[0]}")
            st.bar_chart(group_scores)
            
        with t_dates:
            all_dates = []
            for d_str in df['Dates'].astype(str):
                all_dates.extend(d_str.split(","))
            
            if all_dates:
                counts = pd.Series(all_dates).value_counts().nlargest(10).sort_index()
                st.write("### Most Popular Days")
                st.line_chart(counts)
                st.table(counts)

        with t_dest:
            st.subheader("Suggest a Destination")
            new_city = st.text_input("City Name (e.g., Tokyo)")
            if st.button("Add Suggestion"):
                if 'poll' not in st.session_state: st.session_state.poll = {}
                if new_city: st.session_state.poll[new_city] = 0
            
            if 'poll' in st.session_state:
                for city in st.session_state.poll:
                    col_a, col_b = st.columns([3,1])
                    col_a.write(f"**{city}**")
                    if col_b.button("👍", key=city):
                        st.session_state.poll[city] += 1
                        st.rerun()
                st.write(st.session_state.poll)

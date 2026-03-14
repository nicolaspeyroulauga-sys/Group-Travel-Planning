import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# --- CONFIG ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data.csv"

# Initialize file
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Name", "Origin", "Budget", "Vibe", "Dates", "No-Go"]).to_csv(DATA_FILE, index=False)

# Session State for interactive date selection
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = []

st.title("✈️ Consensus: Interactive Planner")

# --- SECTION 1: USER INPUT ---
st.header("1. Your Profile")

with st.container(border=True):
    col_form, col_cal = st.columns([1, 1])
    
    with col_form:
        name = st.text_input("Name")
        origin = st.text_input("Departure City")
        budget = st.number_input("Max Budget ($)", min_value=0, value=500)
        vibe = st.selectbox("Vibe", ["City Break", "Nature", "Luxury", "Party", "Road Trip"])
        no_go = st.text_input("Anything you hate? (e.g. No hiking)")

    with col_cal:
        st.write("📅 **Click dates to toggle availability:**")
        
        # Calendar Configuration
        calendar_options = {
            "initialView": "dayGridMonth",
            "selectable": True,
            "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
        }
        
        # Convert selected dates into "events" to highlight them on the calendar
        calendar_events = [
            {"title": "✅", "start": d, "end": d, "allDay": True, "backgroundColor": "#00FF00"} 
            for d in st.session_state.selected_dates
        ]
        
        state = calendar(events=calendar_events, options=calendar_options, key="trip_cal")
        
        # Logic to add/remove dates when clicked
        if state.get("dateClick"):
            clicked_date = state["dateClick"]["date"].split("T")[0]
            if clicked_date in st.session_state.selected_dates:
                st.session_state.selected_dates.remove(clicked_date)
            else:
                st.session_state.selected_dates.append(clicked_date)
            st.rerun()

        st.write(f"Selected: {', '.join(st.session_state.selected_dates) if st.session_state.selected_dates else 'None'}")

    if st.button("Add me to the Group", type="primary", use_container_width=True):
        if name and st.session_state.selected_dates:
            new_row = pd.DataFrame([[
                name, origin, budget, vibe, 
                ",".join(st.session_state.selected_dates), no_go
            ]], columns=["Name", "Origin", "Budget", "Vibe", "Dates", "No-Go"])
            
            new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.session_state.selected_dates = [] # Clear for next person
            st.success(f"Successfully added {name}!")
            st.rerun()
        else:
            st.warning("Please enter your name and select at least one date on the calendar.")

st.divider()

# --- SECTION 2: ADMIN VIEW ---
st.header("🔐 2. Results (Admin Only)")
admin_key = st.text_input("Password", type="password")

if admin_key == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        st.write("### Current Group Data")
        st.dataframe(df, use_container_width=True)
        
        # Find Overlap
        all_date_sets = [set(str(d).split(",")) for d in df['Dates']]
        common = set.intersection(*all_date_sets)
        
        if common:
            st.balloons()
            st.success(f"🔥 Found {len(common)} common days: {', '.join(sorted(list(common)))}")
        else:
            st.error("No overlap found yet. Everyone is too busy!")

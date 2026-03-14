import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# 1. SETUP & INITIALIZATION (Must be at the very top)
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Name", "Origin", "Budget", "Vibe", "Dates", "No-Go"]).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = []

st.title("✈️ Consensus: Interactive Planner")

# 2. LAYOUT DEFINITION (Define columns early to avoid NameError)
st.header("1. Your Profile")
# Move this outside the 'with' if possible to ensure col_cal is ALWAYS defined
col_form, col_cal = st.columns([1, 1])

# 3. FORM INPUTS
with col_form:
    name = st.text_input("Name")
    origin = st.text_input("Departure City")
    budget = st.number_input("Max Budget ($)", min_value=0, value=500)
    vibe = st.selectbox("Vibe", ["City Break", "Nature", "Luxury", "Party", "Road Trip"])
    no_go = st.text_input("Anything you hate? (e.g. No hiking)")

# 4. CALENDAR LOGIC
with col_cal:
    st.write("📅 **Click dates to toggle availability:**")
    calendar_options = {"initialView": "dayGridMonth", "selectable": True}
    
    # Render the calendar
    state = calendar(options=calendar_options, key="trip_cal")
    
    # Handle the date selection safely
    if state.get("dateClick"):
        clicked = state["dateClick"]["date"].split("T")[0]
        if clicked not in st.session_state.selected_dates:
            st.session_state.selected_dates.append(clicked)
            st.rerun() # Refresh to show selection logic if needed

    st.write(f"Selected: {', '.join(st.session_state.selected_dates)}")

# 5. SUBMISSION
if st.button("Add me to the Group", type="primary"):
    # ... (Your saving logic here)
    st.success("Added!")

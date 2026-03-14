import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from streamlit_calendar import calendar

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v7.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

# --- SECTION 1: PROFILE (STATIC) ---
st.title("🏛️ Consensus: Master Trip Architect")
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    with st.container(border=True):
        name = st.text_input("Name")
        origin = st.text_input("Departure City (e.g. London, Paris)")
        budget = st.number_input("Max Budget (€)", min_value=0, value=500)
        vibe_scores = {v: st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3) for v in VIBE_OPTIONS}
        no_go = st.text_input("Dealbreakers")

with col_cal:
    cal_options = {"initialView": "dayGridMonth", "selectable": True, "timeZone": "UTC"}
    events = [{"start": d, "end": d, "display": "background", "color": "#28a745"} for d in st.session_state.selected_dates]
    state = calendar(events=events, options=cal_options, key="trip_cal_v7")
    if st.button("🔄 Sync Date", use_container_width=True):
        raw_date = state.get("dateClick", {}).get("date") or state.get("select", {}).get("start")
        if raw_date:
            clean = raw_date.split("T")[0]
            if clean in st.session_state.selected_dates: st.session_state.selected_dates.remove(clean)
            else: st.session_state.selected_dates.add(clean)
            st.rerun()

if st.button("🚀 Lock My Profile", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_row = {"Name": name, "Origin": origin, "Budget": budget, "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go}
        new_row.update(vibe_scores)
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = set()
        st.rerun()

st.divider()

# --- SECTION 2: THE ARCHITECT (ADMIN) ---
st.header("🔐 Section 2: The Master Blueprint")

if st.text_input("Admin Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        # 1. CORE BRAIN CALCULATIONS
        winning_vibe = df[VIBE_OPTIONS].sum().idxmax()
        min_budget = df['Budget'].min()
        origins = df['Origin'].unique().tolist()
        
        # 2. THE BLUEPRINT ENGINE
        def get_blueprint(vibe, budget):
            # Logic to generate destination + activities + breakdown
            v = vibe.split(" ")[0]
            if "City" in v:
                dest = "Budapest, Hungary" if budget < 500 else "Tokyo, Japan"
                acts = ["Ruin Bar Crawl", "Thermal Baths", "Parliament Visit"]
                breakdown = {"Flight": 150, "Lodging": 150, "Food/Fun": 150}
            elif "Nature" in v:
                dest = "Zakopane, Poland" if budget < 400 else "Interlaken, Switzerland"
                acts = ["Alpine Hiking", "Lake Kayaking", "Local Cheese Tasting"]
                breakdown = {"Flight": 120, "Lodging": 180, "Food/Fun": 100}
            else:
                dest = "Algarve, Portugal"
                acts = ["Beach Club", "Surfing Lesson", "Seafood Dinner"]
                breakdown = {"Flight": 100, "Lodging": 200, "Food/Fun": 150}
            
            return dest, acts, breakdown

        dest, activities, costs = get_blueprint(winning_vibe, min_budget)
        total_est = sum(costs.values())

        # 3. VISUALS
        col_main, col_map = st.columns([1, 1])
        
        with col_main:
            st.success(f"### 📍 Target Destination: {dest}")
            st.info(f"**Recommended Trip Style:** {winning_vibe}")
            
            st.write("#### 🗓️ The Itinerary Suggestion")
            for a in activities:
                st.write(f"✅ {a}")
            
            st.write("#### 💰 Cost Breakdown (Per Person)")
            cost_df = pd.DataFrame.from_dict(costs, orient='index', columns=['Est. Price (€)'])
            st.table(cost_df)
            st.metric("Total Estimated Cost", f"€{total_est}", delta=f"€{min_budget - total_est} under limit")

        with col_map:
            st.write("#### ✈️ Departure Network")
            # Mock coordinate mapping for common European cities (to avoid heavy Geocoder libs)
            mock_coords = {"London": [51.5, -0.1], "Paris": [48.8, 2.3], "Madrid": [40.4, -3.7], "Berlin": [52.5, 13.4], "Rome": [41.9, 12.4], "Brussels": [50.8, 4.3]}
            map_data = []
            for city in origins:
                coord = mock_coords.get(city, [48.8, 2.3]) # Default to Paris if unknown
                map_data.append({"City": city, "lat": coord[0], "lon": coord[1]})
            
            st.map(pd.DataFrame(map_data))
            st.caption("Map shows current group departure points.")

        # 4. FINAL CONCLUSION
        st.divider()
        st.subheader("💡 Final Conclusion")
        st.write(f"Based on **{len(df)} travelers**, the best move is a **{winning_vibe}** in **{dest}**. "
                 f"This is the most 'inclusive' choice because the total cost (€{total_est}) fits everyone's budget, "
                 f"including those with the €{min_budget} limit. We avoid: {', '.join(df['No-Go'].dropna().unique())}.")

    else:
        st.info("Awaiting group data...")

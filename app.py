import streamlit as st
import pandas as pd
import numpy as np
import os
from streamlit_calendar import calendar

# --- CONFIG ---
st.set_page_config(page_title="Consensus Master", layout="wide")
DATA_FILE = "trip_data_v11.csv"

# Enhanced Coordinate Database
CITY_COORDS = {
    "Toulouse": [43.60, 1.44], "Paris": [48.85, 2.35], "London": [51.50, -0.12],
    "Amsterdam": [52.36, 4.90], "Madrid": [40.41, -3.70], "Berlin": [52.52, 13.40],
    "Brussels": [50.85, 4.35], "Barcelona": [41.38, 2.17], "Rome": [41.90, 12.49],
    "Bordeaux": [44.83, -0.57], "Lyon": [45.76, 4.83]
}

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + [
        "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
        "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
    ]
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

# --- SECTION 1: PROFILE (STAYS AS REQUESTED) ---
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

st.title("🚗 Consensus: Logistics & Logic Engine")
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    with st.container(border=True):
        name = st.text_input("Name")
        origin = st.text_input("Departure City (e.g. Toulouse, Amsterdam)")
        budget = st.number_input("Max Budget (€)", min_value=0, value=600)
        vibe_scores = {v: st.select_slider(v, options=[1, 2, 3, 4, 5], value=3) for v in [
            "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
            "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
        ]}
        no_go = st.text_input("Dealbreakers")

with col_cal:
    state = calendar(options={"initialView": "dayGridMonth", "selectable": True}, key="trip_cal_v11")
    if st.button("🔄 Sync Date"):
        raw_date = state.get("dateClick", {}).get("date") or state.get("select", {}).get("start")
        if raw_date:
            clean = raw_date.split("T")[0]
            if clean in st.session_state.selected_dates: st.session_state.selected_dates.remove(clean)
            else: st.session_state.selected_dates.add(clean)
            st.rerun()
    st.write(f"Confirmed: {sorted(list(st.session_state.selected_dates))}")

if st.button("🚀 Lock My Profile", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_row = {"Name": name, "Origin": origin, "Budget": budget, "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go}
        new_row.update(vibe_scores)
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = set()
        st.toast(f"🔒 Profile locked in for {name}!")
        st.success("Profile locked in!")
    else:
        st.error("Missing Name or Dates!")

st.divider()

# --- SECTION 2: THE BRAIN ---
if st.text_input("Admin Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        # 1. CORE BRAIN: VIBE & DESTINATION
        vibe_cols = [c for c in df.columns if any(emoji in c for emoji in ["🏙️", "🌲", "💎", "💃", "🚗", "❄️", "🏖️"])]
        winning_vibe = df[vibe_cols].sum().idxmax()
        is_road_trip = "Road Trip" in winning_vibe
        
        # Determine logical destination based on vibe
        if "Beach" in winning_vibe: dest_name, dest_coords = "Costa Brava, Spain", [41.9, 3.2]
        elif "Nature" in winning_vibe: dest_name, dest_coords = "Pyrenees National Park", [42.8, -0.1]
        elif "Road Trip" in winning_vibe: dest_name, dest_coords = "The Basque Coast Loop", [43.4, -1.5]
        else: dest_name, dest_coords = "Lyon, France", [45.7, 4.8]

        # 2. LOGISTICS ENGINE
        st.header(f"🏁 Plan: {winning_vibe} in {dest_name}")
        
        itinerary = []
        car_rental_total = 450.0 # SUV/Van for 4 days
        fuel_and_tolls = 200.0
        shared_car_cost = (car_rental_total + fuel_and_tolls) / len(df)
        
        for i, row in df.iterrows():
            orig_name = str(row['Origin']).strip().title()
            orig_coords = CITY_COORDS.get(orig_name, [48.8, 2.3])
            
            # Distance to the destination
            dist = np.sqrt((orig_coords[0]-dest_coords[0])**2 + (orig_coords[1]-dest_coords[1])**2) * 111
            
            if is_road_trip:
                # Logic: If you're close enough (<400km), you drive your own car/join a car.
                # If far, you take a train to the meeting point.
                if dist < 400:
                    mode = "🚗 Personal Car / Join Group Drive"
                    transport_cost = 60.0 # Personal fuel share
                else:
                    mode = "🚆 Train to Meeting Point"
                    transport_cost = 110.0
                
                total = transport_cost + shared_car_cost + (85.0 * 3) # transport + car share + 3 nights stay
            else:
                # Standard flight/train logic
                mode = "✈️ Flight" if dist > 500 else "🚆 Train"
                transport_cost = 220.0 if dist > 500 else 90.0
                total = transport_cost + (90.0 * 3)

            itinerary.append({
                "Traveler": row['Name'], "From": orig_name, "Method": mode,
                "Transport €": transport_cost, "Shared Car €": shared_car_cost if is_road_trip else 0,
                "Stay & Food €": 270.0, "Grand Total €": total,
                "Budget Fit": "✅" if total <= row['Budget'] else "⚠️"
            })

        # 3. OUTPUT
        res_df = pd.DataFrame(itinerary)
        st.table(res_df)

        st.subheader("📍 Personal Instructions & Route")
        # Shared Departure Grouping
        for city in res_df['From'].unique():
            group = res_df[res_df['From'] == city]
            names = " & ".join(group['Traveler'].tolist())
            if is_road_trip:
                if CITY_COORDS.get(city, [0,0])[0] < 45: # Example: If in South
                    st.write(f"🚗 **{names}**: Since you are in **{city}**, you are the 'South Squad'. You should drive directly to the first stop in {dest_name}.")
                else:
                    st.write(f"🚆 **{names}**: From **{city}**, take the 09:00 train. The group will pick you up at the station in a rental van.")
            else:
                st.write(f"✈️ **{names}**: Book the morning flight from **{city}**. Use the shared shuttle to the hotel.")

        # 4. PRICING BREAKDOWN
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            st.write("#### 💰 The Realistic Pot")
            breakdown = {
                "Shared Van Rental (4 Days)": "€450",
                "Fuel & Highway Tolls": "€200",
                "Average Accommodation": "€180/pp",
                "Activities Fund": "€90/pp"
            } if is_road_trip else {"Average Flight": "€220", "Hotel (3 Nights)": "€210", "Activities": "€100"}
            st.json(breakdown)

        with c2:
            st.write("#### 🗺️ The Map of Movements")
            # Map logic showing origins and meeting hub
            st.map(pd.DataFrame([{"lat": CITY_COORDS.get(c, [48,2])[0], "lon": CITY_COORDS.get(c, [48,2])[1]} for c in res_df['From']]))

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from streamlit_calendar import calendar

# --- CONFIG ---
st.set_page_config(page_title="Consensus Global", layout="wide")
DATA_FILE = "trip_data_v10.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

# Coordinate Database for Realistic Logistics
CITY_COORDS = {
    "Toulouse": [43.60, 1.44], "Paris": [48.85, 2.35], "London": [51.50, -0.12],
    "Amsterdam": [52.36, 4.90], "Madrid": [40.41, -3.70], "Berlin": [52.52, 13.40],
    "Brussels": [50.85, 4.35], "Barcelona": [41.38, 2.17], "Rome": [41.90, 12.49],
    "Lisbon": [38.72, -9.13], "Budapest": [47.49, 19.04], "Munich": [48.13, 11.58]
}

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

# --- SECTION 1: PROFILE (STAYS AS REQUESTED) ---
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

st.title("🌍 Consensus: Global Logistics Architect")
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    with st.container(border=True):
        name = st.text_input("Name")
        origin = st.text_input("Departure City (e.g. Amsterdam, Toulouse)")
        budget = st.number_input("Max Budget (€)", min_value=0, value=600)
        vibe_scores = {v: st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3) for v in VIBE_OPTIONS}
        no_go = st.text_input("Dealbreakers")

with col_cal:
    state = calendar(options={"initialView": "dayGridMonth", "selectable": True}, key="trip_cal_v10")
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
        # 1. FIND THE WINNING DESTINATION & DATES
        winning_vibe = df[VIBE_OPTIONS].sum().idxmax()
        lowest_budget = float(df['Budget'].min())
        all_dates = [d for sub in df['Dates'].astype(str) for d in sub.split(",")]
        best_dates = pd.Series(all_dates).value_counts().idxmax()

        # Destination Selection Logic
        v = winning_vibe.lower()
        if "nature" in v: 
            dest_name, dest_coords = "Interlaken, Switzerland", [46.68, 7.85]
            daily_cost = 100
        elif "city" in v: 
            dest_name, dest_coords = "Berlin, Germany", [52.52, 13.40]
            daily_cost = 80
        else: 
            dest_name, dest_coords = "Barcelona, Spain", [41.38, 2.17]
            daily_cost = 70

        # 2. CALCULATION ENGINE: LOGISTICS PER PERSON
        st.header(f"🏁 Final Master Plan: {dest_name}")
        st.info(f"📅 **Group Arrival Date:** {best_dates} | 🎯 **Vibe:** {winning_vibe}")

        itinerary_data = []
        for i, row in df.iterrows():
            orig_name = str(row['Origin']).strip().title()
            orig_coords = CITY_COORDS.get(orig_name, [48.85, 2.35]) # Default Paris
            
            # Distance math (Approximate)
            dist = np.sqrt((orig_coords[0]-dest_coords[0])**2 + (orig_coords[1]-dest_coords[1])**2) * 111
            
            if dist < 500:
                mode = "🚆 High-Speed Train"
                trans_cost = 85.0
            else:
                mode = "✈️ Flight (Direct/Conn)"
                trans_cost = 220.0 # Realistic 2026 Flight Pricing
            
            stay_cost = daily_cost * 3 # 3-night estimate
            total = trans_cost + stay_cost
            
            itinerary_data.append({
                "Traveler": row['Name'],
                "From": orig_name,
                "Mode": mode,
                "Transport €": trans_cost,
                "Total Est €": total,
                "Status": "✅ OK" if total <= row['Budget'] else "❌ Over Budget"
            })

        # 3. DISPLAY RESULTS
        res_df = pd.DataFrame(itinerary_data)
        st.table(res_df)

        st.subheader("📝 Personalized Joining Instructions")
        # Grouping by departure city for shared travel
        origins = res_df.groupby("From")
        for city, group in origins:
            names = ", ".join(group['Traveler'].tolist())
            mode = group['Mode'].iloc[0]
            if len(group) > 1:
                st.write(f"👥 **{names}**: You are both leaving from **{city}**. We suggest booking the **{mode}** together to save on airport transfers!")
            else:
                st.write(f"👤 **{names}**: You are traveling solo from **{city}** via **{mode}**. Meet the group at {dest_name} Central Station/Airport.")

        # 4. MAP & TOTALS
        st.write("---")
        col_map, col_details = st.columns([1.5, 1])
        with col_map:
            # Map showing Origins and the Destination
            map_df = pd.DataFrame([{"lat": CITY_COORDS.get(c, [48,2])[0], "lon": CITY_COORDS.get(c, [48,2])[1], "type": "Origin"} for c in res_df['From']])
            map_df = pd.concat([map_df, pd.DataFrame([{"lat": dest_coords[0], "lon": dest_coords[1], "type": "Destination"}])])
            fig_map = px.scatter_mapbox(map_df, lat="lat", lon="lon", color="type", zoom=3, mapbox_style="carto-positron")
            st.plotly_chart(fig_map)

        with col_details:
            st.write("#### 💰 Activity Breakdown")
            st.write(f"**Activities in {dest_name}:**")
            st.write("- 🎫 Group Museum/Nature Pass: €40")
            st.write("- 🍽️ Shared Welcome Dinner: €45")
            st.write("- 🚶 Professional Guided Tour: €25")
            st.metric("Total Shared Activity Fund", "€110")

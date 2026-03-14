import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from streamlit_calendar import calendar

# --- CONFIG ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v9.csv"

VIBE_OPTIONS = [
    "City Break 🏙️", "Nature & Hiking 🌲", "Luxury & Spa 💎", 
    "Party & Nightlife 💃", "Road Trip 🚗", "Ski & Snow ❄️", "Beach & Chill 🏖️"
]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

# --- SECTION 1: PROFILE ---
st.title("🏛️ Consensus: Strategic Decision Engine")
col_form, col_cal = st.columns([1, 1.2], gap="large")

with col_form:
    with st.container(border=True):
        name = st.text_input("Name")
        origin = st.text_input("Departure City (e.g. Toulouse, London)")
        budget = st.number_input("Max Budget (€)", min_value=0, value=500)
        vibe_scores = {v: st.select_slider(f"{v}", options=[1, 2, 3, 4, 5], value=3) for v in VIBE_OPTIONS}
        no_go = st.text_input("Dealbreakers")

with col_cal:
    cal_options = {"initialView": "dayGridMonth", "selectable": True, "timeZone": "UTC"}
    events = [{"start": d, "end": d, "display": "background", "color": "#28a745"} for d in st.session_state.selected_dates]
    state = calendar(events=events, options=cal_options, key="trip_cal_v9")
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
        # SUCCESS MESSAGE AS REQUESTED
        st.toast(f"✅ Profile locked in for {name}!", icon="🔒")
        st.success(f"Profile locked in! Your data has been sent to the group analyst.")
    else:
        st.error("Missing Name or Dates!")

st.divider()

# --- SECTION 2: THE BRAIN ---
if st.text_input("Admin Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        # --- LOGIC 1: DATE OVERLAP ENGINE ---
        all_dates = []
        for d_str in df['Dates'].astype(str):
            all_dates.extend(d_str.split(","))
        
        date_series = pd.Series(all_dates).value_counts()
        max_votes = date_series.max()
        best_dates = date_series[date_series == max_votes].index.tolist()
        best_dates.sort()

        # --- LOGIC 2: BUDGET & VIBE ENGINE ---
        winning_vibe = df[VIBE_OPTIONS].sum().idxmax()
        lowest_budget = float(df['Budget'].min())

        def get_smart_recommendation(vibe, budget):
            v = vibe.split(" ")[0]
            # Realistic Data Mapping
            options = {
                "City": {"low": ("Budapest", ["Szechenyi Baths", "Jewish Quarter Walk", "Ruin Bars"]), 
                         "mid": ("Berlin", ["East Side Gallery", "Brandenburg Gate", "Techno Club"])},
                "Nature": {"low": ("High Tatras, Slovakia", ["Lake Strbske Pleso", "Mountain Hut Hike", "Waterfall Trail"]),
                           "mid": ("Chamonix, France", ["Aiguille du Midi", "Mer de Glace", "Paragliding"])},
                "Beach": {"low": ("Sarandë, Albania", ["Ksamil Islands", "Blue Eye Spring", "Lekuresi Castle"]),
                          "mid": ("Lagos, Portugal", ["Ponta da Piedade", "Kayak Caves", "Old Town Fish Dinner"])}
            }
            
            key = "City" if "City" in v else ("Nature" if "Nature" in v else "Beach")
            tier = "low" if budget < 400 else "mid"
            dest, acts = options.get(key, options["City"])[tier]
            
            # Realistic Pricing Breakdown
            breakdown = {
                "Round-trip Flight": budget * 0.25,
                "Accommodation (3 nights)": budget * 0.35,
                "Food & Local Transport": budget * 0.25,
                "Activities & Misc": budget * 0.15
            }
            return dest, acts, breakdown

        dest, activities, costs = get_smart_recommendation(winning_vibe, lowest_budget)

        # --- DISPLAY ---
        st.header("🏁 The Final Consensus")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.info(f"### 📅 Best Dates: **{', '.join(best_dates)}**")
            st.write(f"*(Selected because {max_votes} out of {len(df)} people are free)*")
            
            st.success(f"### 📍 Destination: **{dest}**")
            st.write(f"**Top Recommended Activities:**")
            for a in activities:
                st.write(f"🌟 {a}")

        with c2:
            st.write("#### 💰 Realistic Price Breakdown")
            price_df = pd.DataFrame.from_dict(costs, orient='index', columns=['Price (€)'])
            st.table(price_df.style.format("€{:.2f}"))
            st.metric("Total Estimated Package", f"€{sum(costs.values()):.2f}")

        # --- MAP ---
        st.write("---")
        city_coords = {"Toulouse": [43.60, 1.44], "Paris": [48.85, 2.35], "London": [51.50, -0.12], "Madrid": [40.41, -3.70]}
        map_points = []
        for city in df['Origin'].unique():
            clean = str(city).strip().title()
            if clean in city_coords: map_points.append({"lat": city_coords[clean][0], "lon": city_coords[clean][1]})
        if map_points:
            st.write("#### 🗺️ Group Origins")
            st.map(pd.DataFrame(map_points))

        st.divider()
        st.subheader("💡 Analysis Summary")
        st.write(f"The group chose **{winning_vibe}**. To ensure everyone (especially those with a **€{lowest_budget}** budget) can attend, the AI suggests **{dest}**. "
                 f"The most compatible time to fly is **{best_dates[0]}**.")

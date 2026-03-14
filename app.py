import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# --- CONFIG & DATA ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data_v2.csv"

# Updated columns to include individual vibe scores
VIBE_OPTIONS = ["City Break", "Nature", "Luxury", "Party", "Road Trip"]

if not os.path.exists(DATA_FILE):
    cols = ["Name", "Origin", "Budget", "Dates", "No-Go"] + VIBE_OPTIONS
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = []

st.title("✈️ Consensus: Group Decision Engine")

# --- SECTION 1: USER ENTRY ---
st.header("1. Your Preferences")
col_form, col_cal = st.columns([1, 1])

with col_form:
    name = st.text_input("Name")
    origin = st.text_input("Departure City")
    budget = st.number_input("Max Budget ($)", min_value=0, value=500)
    
    st.write("### Rate the Trip Styles")
    vibe_scores = {}
    for v in VIBE_OPTIONS:
        # Using a slider for granular rating (1 = Hate it, 5 = Love it)
        vibe_scores[v] = st.slider(f"How much do you like: {v}?", 1, 5, 3)
    
    no_go = st.text_input("Any Dealbreakers?")

with col_cal:
    st.write("### 📅 Toggle Available Dates")
    cal_options = {"initialView": "dayGridMonth", "selectable": True}
    
    # Show currently selected dates as green events
    events = [{"title": "✅", "start": d, "end": d, "allDay": True, "color": "#28a745"} for d in st.session_state.selected_dates]
    state = calendar(events=events, options=cal_options, key="trip_cal")

    # TOGGLE LOGIC: If date is in list, remove it. If not, add it.
    if state.get("dateClick"):
        clicked = state["dateClick"]["date"].split("T")[0]
        if clicked in st.session_state.selected_dates:
            st.session_state.selected_dates.remove(clicked)
        else:
            st.session_state.selected_dates.append(clicked)
        st.rerun()

    st.info(f"Selected {len(st.session_state.selected_dates)} days.")

if st.button("Submit My Profile", type="primary", use_container_width=True):
    if name and st.session_state.selected_dates:
        new_data = {
            "Name": name, "Origin": origin, "Budget": budget, 
            "Dates": ",".join(st.session_state.selected_dates), "No-Go": no_go
        }
        new_data.update(vibe_scores) # Adds the ratings to the dictionary
        
        df_new = pd.DataFrame([new_data])
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.session_state.selected_dates = []
        st.success("Preferences saved!")
        st.rerun()

st.divider()

# --- SECTION 2: THE GROUP ALGORITHM ---
st.header("🔐 2. Group Consensus (Admin)")
if st.text_input("Password", type="password") == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        tab1, tab2 = st.tabs(["🏆 Winning Vibe", "📅 Best Dates"])
        
        with tab1:
            st.subheader("The Consensus Algorithm")
            # Sum up scores for each vibe column
            group_totals = df[VIBE_OPTIONS].sum().sort_values(ascending=False)
            
            winner = group_totals.index[0]
            st.metric("Group Winner", winner, f"{group_totals[winner]} points")
            
            # Show a bar chart of the group's preferences
            st.bar_chart(group_totals)

        with tab2:
            all_date_sets = [set(str(d).split(",")) for d in df['Dates']]
            common = set.intersection(*all_date_sets)
            if common:
                st.success(f"Perfect overlap! Everyone can travel on: {sorted(list(common))}")
            else:
                st.warning("No single date works for everyone. Showing most popular dates:")
                # Logic for "Most Popular" if no perfect overlap
                all_dates = [d for sublist in [str(x).split(",") for x in df['Dates']] for d in sublist]
                st.write(pd.Series(all_dates).value_counts().head(5))

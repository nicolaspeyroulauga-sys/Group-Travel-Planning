import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Consensus Travel Hub", page_icon="✈️", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'group_data' not in st.session_state:
    st.session_state.group_data = []

# --- HEADER ---
st.title("🌍 Consensus: Group Trip Architecture")
st.info("Friends: Fill out your profile below. Nicolas: Use the Admin Key at the bottom to generate the trip.")

# --- STEP 1: THE INPUT FORM (FULL WIDTH) ---
st.header("📝 1. Your Travel Profile")
with st.container():
    with st.form("traveler_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name")
            origin = st.text_input("Departure City", placeholder="e.g. London")
        with col2:
            budget = st.number_input("Max Budget ($)", min_value=100, value=500, step=50)
            vibe = st.selectbox("Preferred Style", ["City Break", "Nature/Camping", "Road Trip", "Exotic/Luxury", "Party"])
        with col3:
            # Generate 90 days of dates
            base = datetime.today()
            date_opts = [(base + timedelta(days=x)).strftime("%a, %d %b") for x in range(90)]
            available_dates = st.multiselect("Select ALL Available Days", options=date_opts)
        
        no_go = st.text_input("Dealbreakers (What do you NOT want?)", placeholder="e.g. No cold weather, No hostels")
        
        submit_btn = st.form_submit_button("Lock in my Profile")
        
        if submit_btn:
            if name and available_dates:
                st.session_state.group_data.append({
                    "Name": name,
                    "Origin": origin,
                    "Budget": budget,
                    "Vibe": vibe,
                    "Dates": set(available_dates),
                    "No-Go": no_go
                })
                st.balloons()
                st.success(f"Cheers {name}! Your data is saved.")
            else:
                st.error("Please provide at least your Name and some Dates!")

st.divider()

# --- STEP 2: ADMIN PANEL (THE SECRET KEY) ---
st.header("🔐 2. Decision Engine (Admin Only)")
admin_key = st.text_input("Enter Admin Key to Run Analysis", type="password")

# --- THE RESULTS (ONLY SHOW IF KEY IS CORRECT) ---
if admin_key == "nicolas2026": # Change this to your secret key
    if not st.session_state.group_data:
        st.warning("No data submitted yet! Get your friends to fill the form above.")
    else:
        df = pd.DataFrame(st.session_state.group_data)
        
        # --- VISUALS SECTION ---
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("📊 Group Vibe Preferences")
            fig = px.pie(df, names='Vibe', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("💰 Budget & Constraints")
            min_budget = df['Budget'].min()
            st.metric("Group Spending Limit", f"${min_budget}")
            st.write("**The 'No-Go' List:**")
            for n in df['No-Go']:
                if n: st.write(f"- {n}")

        # --- THE OVERLAP CALENDAR ---
        st.divider()
        st.subheader("📅 The Green Zone (Shared Availability)")
        
        all_dates = [person['Dates'] for person in st.session_state.group_data]
        overlap = set.intersection(*all_dates) if all_dates else set()
        
        if overlap:
            # Sort dates chronologically
            sorted_overlap = sorted(list(overlap), key=lambda x: datetime.strptime(x, "%a, %d %b"))
            st.success(f"Everyone is free on these {len(sorted_overlap)} days:")
            st.write(" | ".join(sorted_overlap))
            
            # Suggestion Logic
            top_vibe = df['Vibe'].mode()[0]
            st.info(f"💡 Based on the group's **{top_vibe}** preference, you should look at flights for the dates above.")
        else:
            st.error("No dates work for everyone. Check the raw data below to find a near-miss.")
            
        # --- RAW DATA TABLE ---
        with st.expander("View Raw Data Table"):
            st.dataframe(df[["Name", "Origin", "Budget", "Vibe", "No-Go"]])
            if st.button("Clear Everything"):
                st.session_state.group_data = []
                st.rerun()

elif admin_key != "":
    st.error("Incorrect Admin Key.")

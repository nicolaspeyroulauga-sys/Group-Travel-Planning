import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Consensus Travel", page_icon="✈️", layout="wide")

def create_google_flights_link(origin, dest, start_date, end_date):
    """Generates a functional Google Flights URL"""
    # Format: YYYY-MM-DD
    start = start_date.strftime('%Y-%m-%d')
    end = end_date.strftime('%Y-%m-%d')
    # Google's deep link structure
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{start}%20through%20{end}"
    return url

# --- UI ---
st.title("🌍 Consensus: The Group Trip Decider")
st.markdown("Find the overlap, lock the dates, and get everyone booked.")

# 1. THE SHARED CONSTRAINTS
st.header("1. Trip Essentials")
col1, col2 = st.columns(2)
with col1:
    destination_city = st.text_input("Where are we going?", value="Lisbon")
with col2:
    # Default to a Friday-Monday trip 3 months from now
    default_start = datetime.now() + timedelta(days=90)
    trip_dates = st.date_input("When is the trip?", [default_start, default_start + timedelta(days=3)])

# 2. THE GROUP DATA
st.header("2. Who's Coming?")
if 'travelers' not in st.session_state:
    st.session_state.travelers = []

with st.form("add_traveler"):
    t_name = st.text_input("Name")
    t_origin = st.text_input("Flying From (City or Airport Code)")
    t_budget = st.number_input("Max Budget ($)", value=500)
    add_btn = st.form_submit_button("Add to Group")
    
    if add_btn and t_name and t_origin:
        st.session_state.travelers.append({"name": t_name, "origin": t_origin, "budget": t_budget})

# 3. THE GENERATOR
if st.session_state.travelers:
    st.divider()
    st.header("3. The Booking Hub")
    st.info(f"Targeting {destination_city} from {trip_dates[0]} to {trip_dates[1]}")
    
    # Display individual booking buttons
    for traveler in st.session_state.travelers:
        c_name, c_link = st.columns([1, 2])
        
        with c_name:
            st.write(f"**{traveler['name']}** ({traveler['origin']})")
        
        with c_link:
            # Generate the personalized link
            flight_url = create_google_flights_link(
                traveler['origin'], 
                destination_city, 
                trip_dates[0], 
                trip_dates[1]
            )
            st.link_button(f"Book Flight for {traveler['name']}", flight_url)
            
    # Clear group button
    if st.button("Reset Group"):
        st.session_state.travelers = []
        st.rerun()
else:
    st.write("Add travelers above to generate the booking dashboard.")

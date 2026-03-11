import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_title_config = st.set_page_config(page_title="Consensus Travel", page_icon="✈️", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'group_data' not in st.session_state:
    st.session_state.group_data = []

# --- HEADER ---
st.title("🌍 Consensus: The Group Trip Decider")
st.markdown("Add your profile and dates. The app finds the 'Sweet Spot' for the group.")

# --- SIDEBAR: YOUR INDIVIDUAL PROFILE ---
with st.sidebar:
    st.header("👤 Your Profile")
    with st.form("user_form", clear_on_submit=True):
        name = st.text_input("What's your name?")
        origin = st.text_input("Departure City (e.g., London)", value="London")
        budget = st.slider("Max Budget ($)", 100, 2000, 500)
        
        vibe = st.selectbox("Your preferred trip style:", 
                            ["Camping/Nature", "Road Trip", "Exotic/Luxury", "City Break", "Party/Nightlife"])
        
        # --- INTERACTIVE CALENDAR SELECTION ---
        # We generate dates for the next 3 months
        start_search = datetime.now()
        date_options = [(start_search + timedelta(days=x)) for x in range(90)]
        date_strings = [d.strftime("%a, %d %b %Y") for d in date_options]
        
        st.write("**Select ALL dates you are free:**")
        my_dates = st.multiselect("Pick days from the list:", options=date_strings)
        
        no_go = st.text_input("Anything you DON'T want to do?", placeholder="e.g. No hiking")
        
        submit = st.form_submit_button("Add to Group")
        
        if submit:
            if name and my_dates:
                st.session_state.group_data.append({
                    "Name": name,
                    "Origin": origin,
                    "Budget": budget,
                    "Vibe": vibe,
                    "Dates": set(my_dates),
                    "No-Go": no_go
                })
                st.success(f"Added {name}!")
            else:
                st.error("Please provide a name and select at least one date.")

# --- MAIN DASHBOARD ---
if not st.session_state.group_data:
    st.info("👈 Use the sidebar to add yourself and your friends to the trip!")
else:
    df = pd.DataFrame(st.session_state.group_data)
    
    tab1, tab2 = st.tabs(["📊 Group Overview", "🎯 The Final Suggestion"])
    
    with tab1:
        st.subheader("Who's in so far?")
        # Displaying a clean table (excluding the raw date sets for readability)
        st.table(df[["Name", "Origin", "Budget", "Vibe", "No-Go"]])
        
        if st.button("Clear All Data"):
            st.session_state.group_data = []
            st.rerun()

    with tab2:
        st.subheader("The Result")
        
        # 1. FINDING THE DATE OVERLAP
        all_date_sets = [person['Dates'] for person in st.session_state.group_data]
        common_dates = set.intersection(*all_date_sets) if all_date_sets else set()
        
        if common_dates:
            sorted_dates = sorted(list(common_dates), key=lambda x: datetime.strptime(x, "%a, %d %b %Y"))
            st.success(f"✅ Found **{len(sorted_dates)}** days where EVERYONE is free!")
            st.write("### Your Green Zone:")
            st.write(", ".join(sorted_dates))
            
            # 2. BUDGET CAP
            min_budget = df["Budget"].min()
            st.warning(f"💰 **Group Budget Cap:** ${min_budget} (We must stick to this for the group).")
            
            # 3. DESTINATION IDEAS BASED ON VIBE
            st.write("### 🏝️ Suggested Destinations")
            # Simple logic: pick a destination based on the most popular vibe
            top_vibe = df["Vibe"].mode()[0]
            
            suggestions = {
                "Camping/Nature": ["Slovenia (Lake Bled)", "Norway Fjords", "Scottish Highlands"],
                "Road Trip": ["Portugal Coast", "Tuscany, Italy", "Garden Route, South Africa"],
                "Exotic/Luxury": ["Bali, Indonesia", "Amalfi Coast, Italy", "Santorini, Greece"],
                "City Break": ["Budapest, Hungary", "Prague, Czech Republic", "Lisbon, Portugal"],
                "Party/Nightlife": ["Ibiza, Spain", "Berlin, Germany", "Mykonos, Greece"]
            }
            
            picks = suggestions.get(top_vibe, ["Europe Explorer"])
            st.write(f"Since the group prefers **{top_vibe}**, you should look at:")
            for p in picks:
                st.markdown(f"- **{p}**")
                
            # 4. QUICK BOOKING LINK
            st.divider()
            st.write("#### 🔗 Quick Flight Check")
            # Use the first common date as a sample
            sample_date = datetime.strptime(sorted_dates[0], "%a, %d %b %Y").strftime("%Y-%m-%d")
            
            for _, row in df.iterrows():
                google_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{picks[0]}%20from%20{row['Origin']}%20on%20{sample_date}"
                st.link_button(f"Check Flights for {row['Name']}", google_link)

        else:
            st.error("❌ No overlapping dates found. Someone needs to be more flexible!")
            # Show a heatmap-style table of who is free when (Simplified)
            st.write("Try to find a compromise based on the individual dates in the Overview tab.")

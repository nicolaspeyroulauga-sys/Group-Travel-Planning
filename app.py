import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- FILE SETUP ---
DATA_FILE = "group_data.csv"

# Create file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Name", "Origin", "Budget", "Start", "End", "Style", "No_Go"])
    df.to_csv(DATA_FILE, index=False)

st.title("🏝️ The Consensus Hub")

# --- STEP 1: INDIVIDUAL INPUT ---
with st.expander("📝 Step 1: Fill Your Travel Profile", expanded=True):
    with st.form("friend_form", clear_on_submit=True):
        name = st.text_input("Your Name")
        origin = st.text_input("Departure City (e.g. LHR)")
        budget = st.slider("Max Budget ($)", 200, 2000, 500)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Earliest Departure")
        with col2:
            end_date = st.date_input("Latest Return")
            
        style = st.multiselect("What's your vibe?", 
                              ["Exotic/Luxury", "Camping/Nature", "Road Trip", "City Break", "Party/Nightlife"])
        
        no_go = st.text_area("What do you NOT want to do? (e.g. 'No hiking', 'No cold weather')")
        
        submitted = st.form_submit_button("Submit to Group")
        
        if submitted:
            # Append data to CSV
            new_data = pd.DataFrame([[name, origin, budget, start_date, end_date, ", ".join(style), no_go]], 
                                    columns=["Name", "Origin", "Budget", "Start", "End", "Style", "No_Go"])
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success(f"Got it, {name}! Your preferences are locked in.")

# --- STEP 2: THE SUMMARY (FOR YOU) ---
st.divider()
if st.checkbox("Show Group Status (Admin Only)"):
    df_group = pd.read_csv(DATA_FILE)
    st.write(f"### Current RSVPs: {len(df_group)}")
    st.dataframe(df_group)
    
    # Simple Analysis: Budget Cap
    if not df_group.empty:
        cap = df_group["Budget"].min()
        st.warning(f"⚠️ Group Budget Limit: ${cap} (Based on {df_group.loc[df_group['Budget'].idxmin(), 'Name']}'s limit)")

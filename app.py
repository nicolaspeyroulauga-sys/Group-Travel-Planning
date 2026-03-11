import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Consensus Travel", layout="wide")
DATA_FILE = "trip_data.csv"

# Initialize the CSV file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Name", "Origin", "Budget", "Vibe", "Dates", "No-Go"])
    df_init.to_csv(DATA_FILE, index=False)

# --- APP INTERFACE ---
st.title("✈️ Consensus: The All-In-One Planner")
st.markdown("Enter your details below. No external accounts required.")

# --- SECTION 1: USER INPUT ---
with st.container():
    st.header("1. Your Profile")
    with st.form("travel_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            origin = st.text_input("Departure City")
            budget = st.number_input("Max Budget ($)", min_value=0, value=500)
        with col2:
            vibe = st.selectbox("Vibe", ["City Break", "Nature", "Luxury", "Party", "Road Trip"])
            # Calendar Logic
            base = datetime.today()
            date_opts = [(base + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(60)]
            available_dates = st.multiselect("Days you are free", options=date_opts)
            
        no_go = st.text_input("Anything you hate? (e.g. No hiking)")
        submit = st.form_submit_button("Add me to the Group")

        if submit:
            if name and available_dates:
                # Save to Local CSV
                new_row = pd.DataFrame([[name, origin, budget, vibe, ",".join(available_dates), no_go]], 
                                        columns=["Name", "Origin", "Budget", "Vibe", "Dates", "No-Go"])
                new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success(f"Added {name}! The file '{DATA_FILE}' has been updated.")
            else:
                st.error("Name and Dates are required!")

st.divider()

# --- SECTION 2: ADMIN VIEW ---
st.header("🔐 2. Results (Admin Only)")
admin_key = st.text_input("Password", type="password")

if admin_key == "nicolas2026":
    df = pd.read_csv(DATA_FILE)
    
    if len(df) > 0:
        tab1, tab2 = st.tabs(["📊 Analytics", "📅 Common Dates"])
        
        with tab1:
            # Vibe Chart
            fig = px.pie(df, names='Vibe', title="Group Vibe", hole=0.3)
            st.plotly_chart(fig)
            
            # Constraints
            st.metric("Group Budget Cap", f"${df['Budget'].min()}")
            st.write("**Group Dealbreakers:**")
            for ng in df['No-Go'].dropna():
                if ng: st.write(f"• {ng}")

        with tab2:
            # Find the Overlap
            # Convert strings back to sets of dates
            all_date_sets = [set(str(d).split(",")) for d in df['Dates']]
            common = set.intersection(*all_date_sets)
            
            if common:
                st.success(f"Found {len(common)} overlapping days!")
                st.write(sorted(list(common)))
                
                # Dynamic Link Generator
                top_vibe = df['Vibe'].mode()[0]
                sample_date = sorted(list(common))[0]
                st.write("### Quick Flight Check")
                for i, row in df.iterrows():
                    link = f"https://www.google.com/search?q=flights+from+{row['Origin']}+on+{sample_date}"
                    st.link_button(f"Search for {row['Name']}", link)
            else:
                st.error("No dates overlap for everyone yet.")
        
        if st.button("Reset Everything (Delete Data)"):
            os.remove(DATA_FILE)
            st.rerun()
    else:
        st.info("No data yet. Fill out the form above.")

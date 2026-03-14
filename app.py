# --- STABLE CALENDAR BLOCK ---
with col_cal:
    st.write("📅 **Select your dates below:**")
    
    calendar_options = {
        "initialView": "dayGridMonth",
        "selectable": True,
    }
    
    # Use a simpler key and check if state actually changes
    state = calendar(options=calendar_options, key="trip_planner_cal")
    
    if state.get("select"):
        start = state["select"]["start"].split("T")[0]
        # FullCalendar 'end' is exclusive, so we treat it as a range or single day
        if start not in st.session_state.selected_dates:
            st.session_state.selected_dates.append(start)
            st.toast(f"Added {start}") # Small popup instead of full rerun
    
    # Display picked dates clearly
    st.info(f"Confirmed Dates: {', '.join(sorted(st.session_state.selected_dates))}")
    
    if st.button("Clear Selected Dates"):
        st.session_state.selected_dates = []
        st.rerun()

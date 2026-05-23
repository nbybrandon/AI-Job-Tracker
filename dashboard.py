# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from tracker import generate_interview_questions

st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")

st.title("My Application Tracker")
st.markdown("An interactive overview of my internship hunt.")

FILE_NAME = "my_applications.csv"

if not os.path.exists(FILE_NAME):
    st.warning("No data found! Please run tracker.py to add some applications first.")
else:
    # on_bad_lines='skip' acts as a defensive guardrail to prevent malformed rows from crashing the app
    df = pd.read_csv(FILE_NAME, on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # --- SIDEBAR: INTERVIEW PREP ---
    st.sidebar.header("🎯 AI Interview Prep")
    if not df.empty:
        app_list = [f"{row['Company']} - {row['Role']}" for _, row in df.iterrows()]
        selected_app = st.sidebar.selectbox("Select Application", app_list)
        
        if st.sidebar.button("Generate Prep Guide"):
            # Find the selected row
            idx = app_list.index(selected_app)
            target_row = df.iloc[idx]
            
            with st.spinner(f"Consulting AI coach for {target_row['Company']}..."):
                prep_guide = generate_interview_questions(
                    target_row['Company'], 
                    target_row['Role'], 
                    target_row['Notes']
                )
                st.sidebar.markdown("---")
                st.sidebar.markdown(prep_guide)
    else:
        st.sidebar.info("Add applications to enable Interview Prep.")

    # --- AUTOMATED AGING CALCULATIONS ---
    try:
        df['Date Applied'] = pd.to_datetime(df['Date Applied'], errors='coerce')
        today = pd.Timestamp(datetime.now().date())
        df['Days Elapsed'] = (today - df['Date Applied']).dt.days
        
        # Stagnant warnings are for applications that need attention
        pending_statuses = ['Applied', 'Waiting on Reply', 'Follow Up', 'No Response']
        stagnant_df = df[
            (df['Days Elapsed'] >= 7) & 
            (df['Status'].str.strip().isin(pending_statuses))
        ]
    except Exception as e:
        stagnant_df = pd.DataFrame()
        st.sidebar.error(f"Error calculating aging engine: {e}")

    # --- PROACTIVE AGING ALERT DISPLAY ---
    if not stagnant_df.empty:
        st.error(f"⚠️ PROACTIVE ALERT: {len(stagnant_df)} Stagnant Applications Detected (>7 Days Without Touchpoints)")
        with st.expander("Click to view companies requiring follow-up action sequences", expanded=True):
            display_stagnant = stagnant_df[['Company', 'Role', 'Date Applied', 'Days Elapsed', 'Notes']].copy()
            display_stagnant['Date Applied'] = display_stagnant['Date Applied'].dt.strftime('%Y-%m-%d').fillna('N/A')
            st.dataframe(display_stagnant, use_container_width=True, hide_index=True)
        st.markdown("---")

    # --- TOP METRICS ROW ---
    st.subheader("Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    total_apps = len(df)
    interviewing = len(df[df['Status'].str.contains('Interview', case=False, na=False)])
    waiting = len(df[df['Status'].str.strip().isin(['Applied', 'Waiting on Reply', 'Follow Up', 'Followed Up'])])
    no_response = len(df[df['Status'].str.strip() == 'No Response'])
    
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviewing", interviewing)
    col3.metric("Active Pipelines (Waiting/Follow-Up)", waiting)
    col4.metric("Unresolved (No Response)", no_response)

    st.divider()

    # --- MASTER INTERACTIVE DATA TABLE ---
    st.subheader("Master Job List")
    st.markdown("Edit your application details directly in the table below and click 'Save Changes'.")
    
    # We use a copy for display to avoid messing with types before editing
    display_df = df.copy()
    if 'Date Applied' in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df['Date Applied']):
        display_df['Date Applied'] = display_df['Date Applied'].dt.strftime('%Y-%m-%d').fillna('N/A')
        
    if 'Days Elapsed' in display_df.columns:
        display_df = display_df.drop(columns=['Days Elapsed'])

    # Data Editor
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        height=500
    )

    if st.button("💾 Save Changes to CSV"):
        try:
            # We save the edited_df back to the file.
            # Note: If date formatting was changed for display, it might be saved as string.
            # But the user can also edit the date.
            edited_df.to_csv(FILE_NAME, index=False, encoding='utf-8')
            st.success("State Storage Synchronized! Database updated successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save changes: {e}")
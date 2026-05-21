# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set up the webpage layout
st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")

st.title("My Application Tracker")
st.markdown("An interactive overview of my internship hunt.")

FILE_NAME = "my_applications.csv"

if not os.path.exists(FILE_NAME):
    st.warning("No data found! Please run tracker.py to add some applications first.")
else:
    # Read the data
    df = pd.read_csv(FILE_NAME)
    df.columns = df.columns.str.strip()
    
    # --- AUTOMATED AGING CALCULATIONS ---
    try:
        df['Date Applied'] = pd.to_datetime(df['Date Applied'], errors='coerce')
        today = pd.Timestamp(datetime.now().date())
        df['Days Elapsed'] = (today - df['Date Applied']).dt.days
        
        pending_statuses = ['Applied', 'Waiting on Reply']
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
        
        # Display the specific items requiring tactical follow-ups in a clean warning expander
        with st.expander("Click to view companies requiring follow-up action sequences", expanded=True):
            display_stagnant = stagnant_df[['Company', 'Role', 'Date Applied', 'Days Elapsed', 'Notes']].copy()
            display_stagnant['Date Applied'] = display_stagnant['Date Applied'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_stagnant, use_container_width=True, hide_index=True)
        st.markdown("---")

    # --- TOP METRICS ROW ---
    st.subheader("Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    total_apps = len(df)
    interviewing = len(df[df['Status'].str.contains('Interview', case=False, na=False)])
    waiting = len(df[df['Status'].str.strip().isin(pending_statuses)])
    no_response = len(df[df['Status'] == 'No Response'])
    
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviewing", interviewing)
    col3.metric("Waiting (Pending)", waiting)
    col4.metric("No Response", no_response)

    st.divider()

    # --- MASTER INTERACTIVE DATA TABLE ---
    st.subheader("Master Job List")
    st.markdown("Click column headers to sort, or use the search icon in the top right of the table to isolate specific records.")
    
    # Format dates back to clean strings for display layout
    display_df = df.copy()
    if 'Date Applied' in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df['Date Applied']):
        display_df['Date Applied'] = display_df['Date Applied'].dt.strftime('%Y-%m-%d')
        
    # Drop the internal calculations column from the clean master grid overview
    if 'Days Elapsed' in display_df.columns:
        display_df = display_df.drop(columns=['Days Elapsed'])

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )
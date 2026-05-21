# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# Set up the webpage layout
st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")

st.title("My Application Tracker")
st.markdown("An interactive overview of my internship hunt.")

FILE_NAME = "my_applications.csv"

if not os.path.exists(FILE_NAME):
    st.warning("No data found! Please run `tracker.py` to add some applications first.")
else:
    # Read the data
    df = pd.read_csv(FILE_NAME)
    
    # --- TOP METRICS ROW ---
    st.subheader("Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    total_apps = len(df)
    interviewing = len(df[df['Status'].str.contains('Interview', case=False, na=False)])
    waiting = len(df[df['Status'] == 'Applied'])
    no_response = len(df[df['Status'] == 'No Response'])
    
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviewing", interviewing)
    col3.metric("Waiting (Applied)", waiting)
    col4.metric("No Response", no_response)

    st.divider()

    # --- INTERACTIVE DATA TABLE ---
    st.subheader("Master Job List")
    st.markdown("You can click on the column headers to sort, or use the search icon in the top right of the table to filter specific companies!")
    
    # Display the dataframe as an interactive, scrollable web table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=600 # Makes the table nice and tall
    )
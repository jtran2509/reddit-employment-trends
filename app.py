""""
How to run: open Terminal & run `streamlit run app.py`
Visualization purpose as well. 
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


#1. Set page layout 
st.set_page_config(page_title="Reddit Immigration Insights", layout="wide")

#2. Set title
st.title("Analysis on job market and Immigrations (Reddit Data)")
st.markdown("Project of Analysing the pain of job seekers and skills trend in Canada")

# 3. Sidebar to choose Tab
menu = ['Market Pulse', 'Technical Skills', 'Immigration Insights']
choice = st.sidebar.selectbox("Chose one field to get analysis", menu)

if choice == "Technical Skills":
    st.header("Skills & Emotions")
    st.write("Top Key Words that are debated the most (after filtered)")
    # Bar Chart using st.pyplot(fig)

    #
elif choice == "Immigration Insights":
    st.header("LMIA issues & Legal Aspects")
    st.write("Keywords Analysis and Emotions related to LMIA")
    # Show bigrams (LMIA scam, support, etc.)

# 4. Load dataset for analysis
clean_df = pd.read_csv("./data/processed/reddit_master.csv")
clean_df['date'] = pd.to_datetime(clean_df['created_utc']).dt.date # Make sure the date is formatted correctly

min_date = clean_df['date'].min()
max_date = clean_df['date'].max()

# 5 Create Slider to choose Date Range
start_date, end_date = st.sidebar.slider(
    "Choose date Range for Analysis",
    min_value = min_date,
    max_value = max_date,
    value = (max_date - timedelta(days=7), max_date), # Auto the closest 7 days
    format="DD/MM/YY")

# Filter dataframe according to chosen date
mask = (clean_df['date'] >= start_date) & (clean_df['date'] <= end_date)
df_filtered = clean_df.loc[mask]
# Show the results
st.subheader(f"Results from {start_date.strftime("%d/%m/%y")} to {end_date.strftime("%d/%m/%y")}")
st.write(f"Found **{len(df_filtered)}** posts during this time.")

# Use df_filtered to plot the chart
# Top 20 keywords for this week 

# Top professional keywords mentioned in total post
st.subheader("Industry & Occupation Insights")
st.plotly_chart(fig, use_container_width=True)

""""
How to run: open Terminal & run `streamlit run app.py`
Visualization purpose as well. 
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from datetime import datetime, timedelta

#1. Set title
##. Set page layout 
st.set_page_config(page_title="Reddit's Canada Immigration & Job Market Insights", layout="wide", page_icon="🇨🇦")

# --LOAD DATA--
@st.cache_data
def load_data():
    df = pd.read_csv("data\processed\reddit_master.csv")
    df['date'] = pd.to_datetime(df['created_utc']).dt.date # Make sure the date is formatted correctly
    # Classify sentiments for users
    def label_vibe(pol):
        if pol > 0.1: return "Positive 😊"
        elif pol < -0.1: return "Worried/Cautious 😟"
        return "Neutral 😐"
        
    df['sentiment_vibe'] = df['polarity'].apply(label_vibe)
    return df
    
# 2. Sidebar to choose Tab
st.sidebar.title("🔍Filter Data")

## Slider to let the user choose date
df['created_at'] = pd.to_datetime(df['created_at'], unit="s").dt.date
min_date = df['created_utc'].min()
max_date = df['ceated_utc'].max()

## Create Slider to choose Date Range
if min_date == max_date:
    st.sidebar.warning("At the moment, data is only available on: " +str(min_date))
else:
    start_date, end_date = st.sidebar.slider(
    "Choose date Range for Analysis",
    min_value = min_date,
    max_value = max_date,
    value = (max_date - timedelta(days=7), max_date), # Auto the closest 7 days
    format="DD/MM/YY")
    # Filter dataframe according to chosen date
    mask = (df['created_at'] >= start_date) & (df['created_at'] <= end_date)
    df_filtered = df.loc[mask]

# 3. Sidebar menu
menu = ['Market Pulse', 'Technical Skills', 'Immigration Insights']
choice = st.sidebar.selectbox("Chose one field to get analysis", menu)

### Main inference
st.title("Analysis on Canadian job market and Immigrations")
st.markdown(f"Analysis from **{len(df)}** posts on Reddit!")

# ---TAB 1: MARKET PULSE ---
if choice == "Market Pulse":
    st.header("📊 Market Pulse")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Top Occupations Mentioned")
        # Plot regarding top occupations mentioned
        if "Occupation" in df.columns:
            occ_counts = df['Occupations'].value_counts.head(10).reset_index()
            fig_occ = px.bar(occ_counts, x = "Count", y="Occupation", orientation="h",
                             color="Count", color_continuous_scale="Blues")
            st.plotly_chart(fig_occ, use_container_width=True)

    with col2:
        st.subheader("Community's behaviour")
        sent_counts = df['sentiment_vibe'].value_counts()
        fig_pie = px.pie(values=sent_counts.values, names=sent_counts.index,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(sent_counts, use_container_width=True)

#--TAB 2: TECHNICAL SKILLS ----
if choice == "Technical Skills":
    st.header("🧠 Skills & Keywords")
    st.write("Top Key Words that appear the most in job's discussion")
    # Word Cloud images
    try:
        st.image("foo.png", caption="WordCloud from Reddit Discussion", use_container_width=True)
    except:
        st.info("Run wordcloud function in notebook to create file first!")

# --- TAB 3: IMMIGRATION INSIGHTS
elif choice == "Immigration Insights":
    st.header("🛡️ LMIA issues & Immigrations-related")
    # Show bigrams (LMIA scam, support, etc.)
    st.subheader("Keywords that caught attention")
    # Show examples of SCAM posts
    scam_keywords = ['scam', 'fake', 'loophole', 'fraud', 'illegal', 'pay']
    lm_scam_pattern = "|".join(scam_keywords)
    lm_scam_posts = df[df['final_en_text'].str.contains('lmia', case=False) &
                  df['final_en_text'].str.contains(lm_scam_pattern, case=False)]

    for i, row in lm_scam_posts.head(3).iterrows():
        print(f"Subreddit: {row['subreddit']}")
        print(f"Title: {row['final_en_text']}")

    sentiment_val = df['vader_score'].mean()
    if sentiment_val > 0.2:
        st.success(f"Reddit users is feeling **positive** ({sentiment_val:.2f})")
    elif sentiment_val < -0.2:
        st.success(f"Reddit users is feeling **worried** ({sentiment_val:.2f})")
    else:
        st.warning(f"Reddit users is feeling **neutral** ({sentiment_val:.2f})")



# Show the results
st.subheader(f"Results from {start_date.strftime("%d/%m/%y")} to {end_date.strftime("%d/%m/%y")}")
st.write(f"Found **{len(df_filtered)}** posts during this time.")

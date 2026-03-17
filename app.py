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
    path = "data/processed/reddit_master.csv"
    df = pd.read_csv(path)

    df['date'] = pd.to_datetime(df['created_utc']).dt.date
    # Delete all of the Unnamed columns that are created when we save CSVs with pandas
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    return df

# Load dataset
df = load_data()
st.write("The columns that we're having in the dataset: ", df.columns.tolist())


# 2. Sidebar to choose Tab
st.sidebar.title("🔍Filter Data")

## Slider to let the user choose date
min_date = df['date'].min()
max_date = df['date'].max()

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
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
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
        if "occupation" in df.columns:
            occ_counts = df['occupation'].value_counts().head(10).reset_index()
            fig_occ = px.bar(occ_counts, x = "count", y="occupation", orientation="h",
                             color="count", color_continuous_scale="Blues")
            st.plotly_chart(fig_occ, use_container_width=True)

    with col2:
        st.subheader("Community's behaviour")
        vibe_counts = df['attitude'].value_counts().reset_index()
        if not vibe_counts.empty:
            fig_vibe = px.pie(vibe_counts, 
                              values="count", names="attitude",
                              title="Distribution of Community's Attitude",
                              color="attitude",
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_vibe, use_container_width=True)

#--TAB 2: TECHNICAL SKILLS ----
if choice == "Technical Skills":
    st.header("🧠 Skills & Keywords")
    st.write("Top Key Words that appear the most in job's discussion")
    # Word Cloud images
    try:
        st.image(r"./notebooks/foo.png", caption="WordCloud from Reddit Discussion", use_container_width=True)
    except:
        st.info("Run wordcloud function in notebook to create file first!")

# --- TAB 3: IMMIGRATION INSIGHTS
elif choice == "Immigration Insights":
    st.header("🛡️ LMIA issues & Immigrations-related")
    sentiment_val = df_filtered['vader_score'].dropna().mean()
    st.write("---")
    st.subheader("Community Sentiment Analysis")
    if sentiment_val > 0.2:
        st.success(f"Overall, Reddit users is feeling **positive** ({sentiment_val:.2f})")
    elif sentiment_val < -0.2:
        st.success(f"Overall, Reddit users is feeling **worried** ({sentiment_val:.2f})")
    else:
        st.warning(f"Overall, Reddit users is feeling **neutral** ({sentiment_val:.2f})")
    # Show bigrams (LMIA scam, support, etc.)
    st.subheader("Keywords that caught attention")
    # Show examples of SCAM posts
    st.subheader("Posts that are flagged as potential scams")
    scam_keywords = ['scam', 'fake', 'loophole', 'fraud', 'illegal', 'pay']
    lm_scam_pattern = "|".join(scam_keywords)
    lm_scam_posts = df_filtered[df_filtered['final_en_text'].str.contains('lmia', case=False) &
                  df_filtered['final_en_text'].str.contains(lm_scam_pattern, case=False)]

    if not lm_scam_posts.empty:
        st.write("Below are a few examples: ")
        for i, row in lm_scam_posts.head(3).iterrows():
            st.warning(f"**Subreddit**: r/{row['subreddit']}\n\n**Content**: {row['final_en_text']}")
    




# Show the results
st.subheader(f"Results from {start_date.strftime("%d/%m/%y")} to {end_date.strftime("%d/%m/%y")}")
st.write(f"Found **{len(df_filtered)}** posts during this time.")


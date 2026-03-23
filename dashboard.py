""""
How to run: open Terminal & run `streamlit run app.py`
Visualization purpose as well. 
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from datetime import datetime, timedelta
import warnings 

warnings.filterwarnings('ignore', category=UserWarning)

#1. Set title
##. Set page layout 
st.set_page_config(page_title="Reddit's Canada Immigration & Job Market Insights", layout="wide", page_icon="🇨🇦")

# --LOAD DATA--
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/raw/reddit_employment.db")
    df = pd.read_sql_query("SELECT * FROM processed_posts", conn)
    conn.close()
    # Tackle `created_utc` 
    df['date'] = pd.to_datetime(df['created_utc']).dt.date
    # Remove any rows with N/A datetime
    df = df.dropna(subset=['date'])
    return df

# Load dataset
df = load_data()

# Sidebar to choose Tab
st.sidebar.title("🔍Filter Data")

## Slider to let the user choose date
min_date = df['date'].min()
max_date = df['date'].max()

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
    value = (max_date - timedelta(days=30), max_date), # Auto the closest 7 days
    format="DD/MM/YY")
    # Filter dataframe according to chosen date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df.loc[mask]

# 3. Sidebar menu
menu = ['Market Pulse', 'Technical Skills', 'Immigration Insights']
choice = st.sidebar.selectbox("Chose one field to get analysis", menu)

### Filter based on Subreddit
subreddits = ['All'] + list(df['subreddit'].unique())
selected_sub = st.sidebar.selectbox("Select Community (Subreddit):", subreddits)

# Apply the filter to dataframe
filtered_df = df.copy()
if selected_sub != "All":
    filtered_df = filtered_df[filtered_df['subreddit'] == selected_sub]

### Main inference
st.title(" 🍁 Analysis on Canadian job market and Immigrations")
st.markdown("----")

# ---TAB 1: MARKET PULSE ---
if choice == "Market Pulse":
    st.header("📊 Market Pulse")

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.subheader("Top Occupations Mentioned")
        # Plot regarding top occupations mentioned
        if "bert_topic" in df_filtered.columns:
            topic_counts = df_filtered['bert_topic'].value_counts().reset_index()
            topic_counts.columns = ['Topic', 'Count']
            fig_topic = px.bar(topic_counts, x = "Count", y="Topic", orientation="h",
                             color="Count", color_continuous_scale="Blues")
            fig_topic.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_topic, use_container_width=True)

    with col2:
        st.subheader("Community's Attitude")
        vibe_counts = df_filtered['attitude'].value_counts().reset_index()
        # vibe_counts.columns = ['Attitude', 'Count']
        if not vibe_counts.empty:
            fig_vibe = px.pie(vibe_counts, 
                              values="count", names="attitude",
                              title="Distribution of Community's Attitude",
                              color="attitude",
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_vibe, use_container_width=True)

    st.markdown("---")

    st.subheader("Percentage of Positive/Negative in terms of Topics")
    if not filtered_df.empty:
        fig2 = px.histogram(filtered_df, x='bert_topic', color="attitude", barmode='group')
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

        

#--TAB 2: TECHNICAL SKILLS ----
elif choice == "Technical Skills":
    st.header("🧠 Dynamic Keywords (WordCloud)")
    st.write("Top Key Words that appear the most in job's discussion")
    if not df_filtered.empty:
        with st.spinner("Generating fast Wordcloud"):
            custom_stopwords = set(STOPWORDS)
            reddit_noises = {'will', 'now', 'one', 'people', 'know', 'think', 'canada', 'work',
                'just', 'don', 'really', 'even', 'much', 'time', 'well', 'going', 'right', 'year',
                'see', 'want', 'make', 'got', 'something', 'anything', 'way', 'question', 'hours',
                'look', 'say', 'said', 'still', 'someone', 'everyone', 'everything', 'might',
                'take', 'need', 'back', 'good', 'find', 'feel', 'maybe', 'post', 'reddit', 'etc',
                'thank', 'thanks', 'help', 'please', 'anyone', 'many', 'much', 'lot', 'also'
            }
            custom_stopwords.update(reddit_noises)
            all_text = " ".join(str(text) for text in df_filtered['final_en_text'] if pd.notna(text))
            wordcloud = WordCloud(width=1000, height=500, random_state=42, 
                                background_color="white",
                                stopwords=custom_stopwords,
                                colormap="magma").generate(all_text)
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title("What are Canadians & Immigrants talking about on Reddit",
                    fontsize=16, fontweight="bold")
            st.pyplot(plt.gcf())

# --- TAB 3: IMMIGRATION INSIGHTS
elif choice == "Immigration Insights":
    st.header("🛡️ LMIA issues & Immigrations-related")
    # Show examples of SCAM posts
    st.subheader("🚨 Posts that are flagged as potential scams")

    scam_keywords = ['scam', 'fake', 'loophole', 'fraud', 'illegal', 'pay']
        
    lm_scam_pattern = "|".join(scam_keywords)
    lm_scam_posts = df_filtered[df_filtered['final_en_text'].str.contains('lmia', case=False) &
                    df_filtered['final_en_text'].str.contains(lm_scam_pattern, case=False)]

    if not lm_scam_posts.empty:
        st.write(f"Found **{len(lm_scam_posts)}** high-risk posts. Below are a few recent examples:")
        for i, row in lm_scam_posts.sort_values(by="date", ascending=False).head(5).iterrows():
            with st.expander(f"r/{row['subreddit']} | {row['date']} | VADER: {row['vader_score']:.2f}"):
                st.markdown(f"**Title:** {row['title']}")
                st.write(row['final_en_text'][:500] + "..." if len(str(row['final_en_text'])) > 500 else row['final_en_text'])
                st.markdown(f"[Link to post]({row['url']})")

    if "vader_score" in df_filtered.columns:
        sentiment_val = df_filtered['vader_score'].dropna().mean()
        st.write("---")
        st.subheader("Community Sentiment Analysis")
        if sentiment_val > 0.2:
            st.success(f"Overall, Reddit users is feeling **positive** ({sentiment_val:.2f})")
        elif sentiment_val < -0.2:
            st.success(f"Overall, Reddit users is feeling **worried** ({sentiment_val:.2f})")
        else:
            st.warning(f"Overall, Reddit users is feeling **neutral** ({sentiment_val:.2f})")

    ### --- FINDING PAIN POINTS----###
    st.subheader("🕵️‍♂️ Deep Dive into Pain Points")
    st.markdown("Analysis from real Reddit data to find out **Pain Points** in the job market.")
    # Only show important columns
    mask_pain = df_filtered['attitude'].str.contains("Negative|Worries", case=False, na=False)
    pain_points_df = df_filtered[mask_pain]

    #Sorting based on VADER score, the more negative, more depressed/disappointed/frustrated
    if "vader_score" in pain_points_df.columns:
        pain_points_df = pain_points_df.sort_values(by="vader_score", ascending=True)

    # Display table
    display_cols= ['title', 'subreddit', 'bert_topic', 'attitude', 'vader_score']
    if not pain_points_df.empty:
        st.dataframe(pain_points_df[display_cols], use_container_width=True, height=300)
    else:
        st.success("Cannot find any pain points!")
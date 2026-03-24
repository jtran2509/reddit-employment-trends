""""
How to run: open Terminal & run `streamlit run app.py`
Visualization purpose as well. 
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from datetime import datetime, timedelta
import warnings 
from scripts.chart_processor import get_profession_count, get_cities_count, generate_wordcloud, plot_bar_chart

warnings.filterwarnings('ignore', category=UserWarning)

professions_keywords = {
    'IT/Tech': ['it', 'tech', 'software', 'developer', 'engineer', 'data scientist', 'programmer', 'cybersecurity', 'ai', 'devops', 'web development', 'frontend', 'backend', 'fullstack'],
    'Marketing': ['marketing', 'digital marketing', 'seo', 'sem', 'social media', 'content creator', 'advertising', 'brand', 'campaign'],
    'Cook/Chef': ['cook', 'chef', 'kitchen', 'restaurant', 'food service', 'hospitality'],
    'Healthcare': ['nurse', 'doctor', 'physician', 'healthcare', 'medical', 'hospital', 'caregiver', 'pharmacist'],
    'Trades': ['carpenter', 'electrician', 'plumber', 'welder', 'mechanic', 'construction'],
    'Admin/Office': ['admin', 'administrative', 'assistant', 'office manager', 'receptionist'],
    'Retail': ['retail', 'sales associate', 'cashier', 'store manager'],
    'Logistics': ['driver', 'logistics', 'warehouse', 'supply chain', 'trucker'],
    'Education': ['teacher', 'educator', 'professor', 'school', 'tutor'] }

## Lists of big cities in Canada
cities = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Edmonton', 'Ottawa', 'Winnipeg',
          'Quebec City', 'Hamilton', 'Kitchener', 'London', 'Victoria', 'Halifax',
          'Brossard', 'Brampton', 'Missisauga']

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

## SIDEBAR
# Sidebar to choose Tab
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
if selected_sub != "All":
    df_filtered = df_filtered[df_filtered['subreddit'] == selected_sub]

### Get citites and professions counts
profession_df = get_profession_count(df_filtered, professions_keywords)
city_df = get_cities_count(df_filtered, cities)

### Main inference
st.title(" 🍁 Analysis on Canadian job market and Immigrations")
st.markdown(f"Analysis from **{len(df_filtered)}** posts on Reddit! Change the time you want to see with Slider on the left!")

# ---TAB 1: MARKET PULSE ---
if choice == "Market Pulse":
    st.header("📊 Market Pulse")
    ## Assess community's overall attitude
    if "vader_score" in df_filtered.columns:
        sentiment_val = df_filtered['vader_score'].dropna().mean()
        st.write("---")
        st.subheader("Community Sentiment Analysis")
        if sentiment_val > 0.2:
            st.success(f"Overall, Reddit users is feeling **positive** during this time!")
        elif sentiment_val < -0.2:
            st.success(f"Overall, Reddit users is feeling **worried** during this time!")
        else:
            st.warning(f"Overall, Reddit users is feeling **neutral** during this time!")

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        # Charts of top occupations mentioned
        st.subheader("Top Occupation Most Mentioned in Reddit")
        fig_occ = plot_bar_chart(profession_df, "Count", "Profession",
                                 "Top Occupations")
        st.plotly_chart(fig_occ, use_container_width=True)

    with col2:
        st.subheader("Community's Attitude")
        vibe_counts = df_filtered['attitude'].value_counts().reset_index()
        if not vibe_counts.empty:
            fig_vibe = px.pie(vibe_counts, 
                              values="count", names="attitude",
                              title="Distribution of Community's Attitude",
                              color="attitude",
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_vibe, use_container_width=True)

    st.markdown("---")

    st.subheader("Percentage of Positive/Negative in terms of Topics")
    if not df_filtered.empty:
        fig2 = px.histogram(df_filtered, x='bert_topic', color="attitude", barmode='group')
        fig2.update_layout(xaxis_tickangle=-45, xaxis_title="Discussion Topics")
        st.plotly_chart(fig2, use_container_width=True)
    

#--TAB 2: TECHNICAL SKILLS ----
elif choice == "Technical Skills":
    st.header("🧠 Dynamic Keywords (WordCloud)")
    st.write(f"📊 Top Key Words that appear the most in subreddit {selected_sub}!")
    if not df_filtered.empty:
        with st.spinner("Generating fast Wordcloud"):
            custom_stopwords = set(STOPWORDS)
            reddit_noises = {'will', 'now', 'one', 'people', 'know', 'think', 'canada', 'work',
                'just', 'don', 'really', 'even', 'much', 'time', 'well', 'going', 'right', 'year', 'years'
                'see', 'want', 'make', 'got', 'something', 'anything', 'way', 'question', 'hours',
                'look', 'say', 'said', 'still', 'someone', 'everyone', 'everything', 'might', 'option'
                'take', 'need', 'back', 'good', 'find', 'feel', 'maybe', 'post', 'reddit', 'etc',
                'thank', 'thanks', 'help', 'please', 'anyone', 'many', 'much', 'lot', 'also', 'day',
                'week', 'go', 'ask', 'used', 'first', 'hello', 'today', 'show'
            }
            custom_stopwords.update(reddit_noises)
            if selected_sub == "All":
                wc_fig = generate_wordcloud(df_filtered['final_en_text'], custom_stopwords)
            else:
            ## Filter data to generate specific WordCloud
                wc_fig = generate_wordcloud(df_filtered[df_filtered['subreddit'] == selected_sub]['final_en_text'], custom_stopwords)
                
            plt.title("What are Canadians & Immigrants talking about on Reddit",
                        fontsize=16, fontweight="bold")
            st.pyplot(wc_fig, use_container_width=True)
        
        # Bar plot showing Canadian cities that are mentioned the most
    fig_cities = plot_bar_chart(city_df, "Count", "City",
                                 "Top Canadian Cities Mentioned in Reddit Posts")
    st.plotly_chart(fig_cities, use_container_width=True)
   


# --- TAB 3: IMMIGRATION INSIGHTS
elif choice == "Immigration Insights":
    st.header("🛡️ LMIA issues & Immigrations-related")
    # Show examples of SCAM posts
    st.subheader("🚨 LMIA issues and job-related concern arising!")

    scam_keywords = ['scam', 'fake', 'loophole', 'fraud', 'illegal', 'pay']
        
    lm_scam_pattern = "|".join(scam_keywords)
    lm_scam_posts = df_filtered[df_filtered['final_en_text'].str.contains('lmia', case=False) &
                    df_filtered['final_en_text'].str.contains(lm_scam_pattern, case=False)]

    if not lm_scam_posts.empty:
        st.write(f"Found **{len(lm_scam_posts)}** posts about risks related to LMIA & SCAMs. Below are a few recent examples:")
        for i, row in lm_scam_posts.sort_values(by="date", ascending=False).head(5).iterrows():
            with st.expander(f"r/{row['subreddit']} | {row['date']} | VADER: {row['vader_score']:.2f}"):
                st.markdown(f"**Title:** {row['title']}")
                st.write(row['final_en_text'][:500] + "..." if len(str(row['final_en_text'])) > 500 else row['final_en_text'])
                st.markdown(f"[Link to post]({row['url']})")

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
    display_cols= ['title', 'subreddit', 'bert_topic', 'attitude']
    friendly_names = {
        "title": "Post Title",
        "subreddit": "Community (Subreddit)",
        "bert_topic": "Discussion Topic",
        "attitude": "Community Sentiment"
    }
    # Filter dataframe and rename the columns simultaneously
    display_df = pain_points_df[display_cols].rename(columns=friendly_names)
    if not pain_points_df.empty:
        st.dataframe(display_df, use_container_width=True, height=300)
    else:
        st.success("Cannot find any pain points!")


# # Plot regarding top occupations mentioned
        # if "bert_topic" in df_filtered.columns:
        #     topic_counts = df_filtered['bert_topic'].value_counts().reset_index()
        #     topic_counts.columns = ['Topic', 'Count']
        #     fig_topic = px.bar(topic_counts, x = "Count", y="Topic", orientation="h",
        #                      color="Count", color_continuous_scale="Blues")
        #     fig_topic.update_layout(yaxis={"categoryorder": "total ascending"})
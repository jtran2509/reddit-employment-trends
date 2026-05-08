from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import pandas as pd
import streamlit as st
import sqlite3
#============================
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

#===============================
@st.cache_data
def load_raw_data():
    """
    Load Raw data from SQLite database.
    """
    conn = sqlite3.connect("data/raw/reddit_employment.db")
    df = pd.read_sql_query("SELECT * FROM processed_posts", conn)
    conn.close()

    # Parse datetime from `created_utc` 
    df['date'] = pd.to_datetime(df['created_utc']).dt.date
    # Remove any rows with N/A datetime
    df = df.dropna(subset=['date'])

    return df
#======== OCCUPATION DATA =========
@st.cache_data
def load_occupation_data(df):
    """
    Count profession mentions in text.
    Each post counts max 1 per profession
    Return Dataframe with columns: ['Occupation', 'Mentions']
    """
    profession_counts = {profession: 0 for profession in professions_keywords.keys()}

    for text in df['final_en_text']:
        if pd.isna(text):
            continue
        text_lower = text.lower()

        for profession, keywords in professions_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    profession_counts[profession] +=1
                    break # only count once per profession per post, some post might contains more keyword

    # Convert to Dataframe for plotting
    profession_df = pd.DataFrame(profession_counts.items(), 
                                 columns=["Occupation", "Mentions"])
    # Sort for better visualization
    return profession_df.sort_values(by="Mentions", ascending=True)

#========= CITIES DATA ===============
@st.cache_data
def load_cities_data(df):
    """
    Count city mentions in text.
    Returns Dataframe with columns: ['City', 'Mentions']
    """
    ## Initialize a dictionary to store the list of city_mentioned
    def find_city(text):
        if pd.isna(text):
            return "Unknown"
        text_lower = text.lower()
        for city in cities:
            if city.lower() in text_lower:
                return city
        return "Not Mentioned"
    
    df_temp = df.copy()
    df_temp['city_mentioned']= df_temp['final_en_text'].apply(find_city)

    # Filter rows where a city was found
    city_counts = df_temp[df_temp['city_mentioned'] != 'Not Mentioned']['city_mentioned'].value_counts()
    
    city_df = pd.DataFrame(city_counts.items(), columns=["City", "Mentions"])
    # Sort for better visualization
    return city_df.sort_values(by="Mentions", ascending=True)

#========== SENTIMENT DATA ===========
@st.cache_data
def load_sentiment_data(df):
    """
    Process sentiment using Textblob for attitude classification and AVDER for compound score
    Returns:
        sentiment_counts: Dataframe with columns ['Sentiment', 'Count']
        avg_vader: float - average VADER score
        avg_textblob: float - average Textblob polarity
        sentiment_message: str - summary message
    """
    # Download VADER lexicon
    if "attitude" not in df.columns:
        return None, 0, "No sentiment data available"

    sentiment_counts = df['attitude'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    # Average Vader score
    avg_vader = 0
    sentiment_message = ""

    if "vader_score" in df.columns:
        avg_vader = df['vader_score'].dropna().mean()

    # Tính TextBlob polarity (chỉ tính 1 lần, cache lại)
    avg_textblob = 0
    if 'final_en_text' in df.columns:
        from textblob import TextBlob
        @st.cache_data
        def _calculate_textblob_avg(texts):
            """Hàm nội bộ để cache kết quả TextBlob"""
            scores = texts.dropna().apply(
                lambda x: TextBlob(str(x)).sentiment.polarity
            )
            return scores.mean()
        
        avg_textblob = _calculate_textblob_avg(df['final_en_text'])

    if avg_vader > 0.2:
        sentiment_message = "Overall, Reddit users is feeling **positive** during this time!"
    elif avg_vader < -0.2:
        sentiment_message = "Overall, Reddit users is feeling **worried** during this time!"
    else:
        sentiment_message = "Overall, Reddit users is feeling **neutral** during this time!" 
    return sentiment_counts, avg_vader, avg_textblob, sentiment_message

# ======= TIME-SERIES TREND DATA ==========            
@st.cache_data
def load_trend_data(df):
    """
    Create daily sentiment trend data
    Return Dataframe with columns : ['date', 'Positive', 'Negative', 'Total_posts', 'avg_vader']
    """
    if "attitude" not in df.columns or "date" not in df.columns:
        return None
    
    # Group by date and attitude
    trend = df.groupby(['date', 'attitude']).size().unstack(fill_value=0)

    # Ensure all sentiment columns exists
    for col in ['Positive', 'Neutral', 'Negative']:
        if col not in trend.columns:
            trend[col] = 0
        
    # Add total posts and avg VADER per day
    trend['total_posts'] = trend.sum(axis = 1)

    if "vader_score" in df.columns:
        trend['avg_vader'] = df.groupby('date')['vader_score'].mean()

    trend = trend.reset_index()
    return trend

# ================
# PAIN POINT DATA
# ================
@st.cache_data
def load_pain_points(df):
    """
    Extract negative/worried posts sorted by VADER score
    """
    mask_pain = df['attitude'].str.contains("Negative|Worried", case=False, na=False)
    pain_df = df[mask_pain].copy()

    if "vader_score" in pain_df.columns:
        pain_df = pain_df.sort_values(by='vader_score', ascending =True)

    return pain_df

# ================
# LMIA SCAM POSTS
# ================
@st.cache_data
def load_lmia_scam_posts(df):
    """
    Find posts about LMIA scams/fraud
    """
    scam_keywords = ['scam', 'fake', 'loophole', 'fraud', 'illegal', 'pay']
    lm_scam_pattern = "|".join(scam_keywords)
    lm_scam_posts = df[df['final_en_text'].str.contains('lmia', case=False) &
                    df['final_en_text'].str.contains(lm_scam_pattern, case=False)]
    
    return lm_scam_posts

# ====== HELPER FUNCTION ========
# Calculate Sentiment once and for all
# ====== HELPER FUNCTION ========
def calculate_sentiment_stats(data):
    """
    Return dictionary including pos_val, neu_val, neg_val, pos_pct, neg_pct, total.
    Handles attitude values with emojis (e.g., 'Positive 😊', 'Worried/Negative 😟').
    """
    if data.empty or "attitude" not in data.columns:
        return {
            'pos_val': 0, 'neu_val': 0, 'neg_val': 0,
            'pos_pct': 0, 'neu_pct': 0, 'neg_pct': 0,
            'total': 0
        }
    
    total = len(data)
    
    # ★★★ DÙNG str.contains ĐỂ TÌM SUBSTRING ★★★
    pos_val = data['attitude'].str.contains('Positive', case=False, na=False).sum()
    neu_val = data['attitude'].str.contains('Neutral', case=False, na=False).sum()
    neg_val = data['attitude'].str.contains('Negative|Worried', case=False, na=False).sum()
    
    result = {
        'pos_val': pos_val,
        'neu_val': neu_val,
        'neg_val': neg_val,
        'pos_pct': round(pos_val / total * 100, 1) if total > 0 else 0,
        'neu_pct': round(neu_val / total * 100, 1) if total > 0 else 0,
        'neg_pct': round(neg_val / total * 100, 1) if total > 0 else 0,
        'total': total
    }
    
    return result

# ==========
def compute_trend_from_filtered(df_filtered):
    """
    Create trend from already-filtered dataframe with handling attitude columns with emojis
    """
    if df_filtered.empty or "date" not in df_filtered.columns or 'attitude' not in df_filtered.columns:
        return None
    
    df_temp = df_filtered.copy()
    df_temp['date'] = pd.to_datetime(df_temp['date']).dt.date

    def map_sentiment(att):
        if pd.isna(att):
            return "Neutral"
        att= str(att)
        if "Positive" in att:
            return "Positive"
        elif "Negative" in att or "Worried" in att:
            return "Negative"
        else:
            return "Neutral"

    df_temp['sentiment_clean'] = df_temp['attitude'].apply(map_sentiment)

    # Group by date and sentiment_clean
    trend = df_temp.groupby(['date', 'sentiment_clean']).size().unstack(fill_value=0)

    for col in ['Positive', 'Neutral', 'Negative']:
        if col not in trend.columns:
            trend[col] = 0

    trend['total_posts'] = trend.sum(axis=0)

    if "vader_score" in df_temp.columns:
        trend['avg_vader'] = df_temp.groupby('date')['vader_score'].mean()

    trend= trend.reset_index()
    return trend
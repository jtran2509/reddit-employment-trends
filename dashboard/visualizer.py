import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import streamlit as st
import pandas as pd

# CUSTOM STOPWORDS 
CUSTOM_STOPWORDS = {'will', 'now', 'one', 'people', 'know', 'think', 'canada', 'work',
                'just', 'don', 'really', 'even', 'much', 'time', 'well', 'going', 'right', 'year', 'years'
                'see', 'want', 'make', 'got', 'something', 'anything', 'way', 'question', 'hours',
                'look', 'say', 'said', 'still', 'someone', 'everyone', 'everything', 'might', 'option'
                'take', 'need', 'back', 'good', 'find', 'feel', 'maybe', 'post', 'reddit', 'etc',
                'thank', 'thanks', 'help', 'please', 'anyone', 'many', 'much', 'lot', 'also', 'day',
                'week', 'go', 'ask', 'used', 'first', 'hello', 'today', 'show'
            }

PROFESSIONS_KEYWORDS = {
    'IT/Tech': ['it', 'tech', 'software', 'developer', 'engineer', 'data scientist', 'programmer', 'cybersecurity', 'ai', 'devops', 'web development', 'frontend', 'backend', 'fullstack'],
    'Marketing': ['marketing', 'digital marketing', 'seo', 'sem', 'social media', 'content creator', 'advertising', 'brand', 'campaign'],
    'Cook/Chef': ['cook', 'chef', 'kitchen', 'restaurant', 'food service', 'hospitality'],
    'Healthcare': ['nurse', 'doctor', 'physician', 'healthcare', 'medical', 'hospital', 'caregiver', 'pharmacist'],
    'Trades': ['carpenter', 'electrician', 'plumber', 'welder', 'mechanic', 'construction'],
    'Admin/Office': ['admin', 'administrative', 'assistant', 'office manager', 'receptionist'],
    'Retail': ['retail', 'sales associate', 'cashier', 'store manager'],
    'Logistics': ['driver', 'logistics', 'warehouse', 'supply chain', 'trucker'],
    'Education': ['teacher', 'educator', 'professor', 'school', 'tutor']
}

def generate_wordcloud(text_series, title="Word Cloud"):
    """
    Generate WordCloud from a Pandas Series of text.
    Returns matplotlib figure
    """
    # Combine all text
    all_text = " ".join(text for text in text_series if pd.notna(text))

    if not all_text.strip():
        return None
    
    # Setup stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(CUSTOM_STOPWORDS)

    # Generate WordCloud
    wc = WordCloud(
        width=800,
        height=400,
        background_color='#1a1a2e',
        colormap='viridis',
        stopwords=stopwords,
        max_words=50,
        collocations=False
    ).generate(all_text)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10,5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title, fontsize=14, fontweight = "bold", color="white")
    fig.patch.set_facecolor("#1a1a2e")

    return fig

def filter_posts_by_occupation(df, occupation):
    """
    Filter posts the mention a specific occupation
    """
    if occupation not in PROFESSIONS_KEYWORDS:
        return df.iloc[:0] 
    
    keywords = PROFESSIONS_KEYWORDS[occupation]
    pattern = "|".join(keywords)
    return df[df['final_en_text'].str.contains(pattern, case=False, na=False)]
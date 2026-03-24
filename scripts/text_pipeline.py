# Plot Wordcloud to get an intuition of the dataset
import os
import pandas as pd
import langdetect
from langdetect import detect, DetectorFactory
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator
from wordcloud import WordCloud, STOPWORDS
import re
import sqlite3


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

DetectorFactory.seed = 0

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Delete link
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Delete space redundant words
    text = re.sub(r"\n+", " ", text)
    return text.strip()

def translated_mixed_text(text):
    #Hybrid translation
    if pd.isna(text) or text.strip() == "":
        return ""
        
    sentences = text.split(".")
    translated_sentences = []

    translator = GoogleTranslator(source="auto", target='en')
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 3: 
            return text
        try:
            lang = detect(sent)
            if lang== "vi": # if the sentence is in Vietnamese => translate
                translated_sentences.append(translator.translate(sent))
            else: # is the sentence is in English => keep
                translated_sentences.append(sent)

        except: # If unable to detect any language, keep the same
            translated_sentences.append(sent)
    return ". ".join(translated_sentences)

# Extra function for processing new data (posts) coming after scraping
def get_new_unprocessed_data(db_path):
    conn = sqlite3.connect(db_path)

    # Take posts from reddit_posts that are not YET present in the processed_posts table
    query = """ SELECT r.* FROM reddit_posts r
    LEFT JOIN processed_posts p on r.title = p.title
    WHERE p.title IS NULL
    """
    new_df = pd.read_sql_query(query, conn)
    conn.close()
    return new_df
# -----------

def process_data_from_db(db_path):
    # print(f"🚀 Is pulling data from SQLite....")
    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query("SELECT * FROM reddit_posts", conn)
    conn.close()
    # 1. Combine title and selftext columns and clean
    print(f"🧹 Is cleaning the text (delete link and remove redundant words...)")
    df['full_text'] = df['title'].fillna("") + ". "+ df['selftext'].fillna("")
    df['full_text'] = df['full_text'].apply(clean_text)
    
    # 2. Drop duplicates
    df = df.drop_duplicates(subset=['full_text'], keep = "first")
    print(f"✅ Done Processing! Total number of clean posts {len(df)}")

    # 3. Translate to English
    ## Only translate the ones that are not translated
    if "final_en_text" not in df.columns:
        df['final_en_text'] = pd.NA

    needs_translation = df['final_en_text'].isna() | (df['final_en_text'] == "")
    if needs_translation.any():
        df.loc[needs_translation, "final_en_text"] = df.loc[needs_translation, 'full_text'].apply(translated_mixed_text)
    return df

def plot_wordcloud(text_series):
    print(f"☁️ Is drawing WordCloud...")
    # Get default stopwords and add extra words
    custom_stopwords = set(STOPWORDS)
    reddit_noises = {'will', 'now', 'one', 'people', 'know', 'think', 'canada', 'work',
        'just', 'don', 'really', 'even', 'much', 'time', 'well', 'going', 'right', 'year',
        'see', 'want', 'make', 'got', 'something', 'anything', 'way', 'question', 'hours',
        'look', 'say', 'said', 'still', 'someone', 'everyone', 'everything', 'might',
        'take', 'need', 'back', 'good', 'find', 'feel', 'maybe', 'post', 'reddit', 'etc',
        'thank', 'thanks', 'help', 'please', 'anyone', 'many', 'much', 'lot', 'also'
    }
    custom_stopwords.update(reddit_noises)
    all_text = " ".join(text for text in text_series)
    wordcloud = WordCloud(width=1000, height=500, random_state=42, 
                          background_color="white",
                          stopwords=custom_stopwords,
                          colormap="magma").generate(all_text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("What are Canadians & Immigrants talking about on Reddit",
               fontsize=16, fontweight="bold")
    plt.show()

print(f"📊 Is analyzing users' emotions...")

def label_vibe(score):
    if pd.isna(score): return "Neutral 😐"
    if score > 0.15: return "Positive 😊"
    elif score < -0.15: return "Worried/Negative 😟"
    return "Neutral 😐"

# Save newly clean dataset into a new table called "processed_posts"
print("Is saving clean dataset into Database")

if __name__ == "__main__":
    db_path = "data/raw/reddit_employment.db"
    analyzer = SentimentIntensityAnalyzer()

    conn = sqlite3.connect(db_path)

    # ## Select all of the data
    # df = pd.read_sql_query("SELECT * FROM reddit_posts", conn)

    print("⚡ Starting the pipeline...")
    print("🔍 Is checking the new dataset...")
    # 1. Load and clean the dataset
    # df = process_data_from_db(db_path) # for the 1st time scraping and processed >8000 posts
    df_new = get_new_unprocessed_data(db_path)

    if df_new.empty:
        print("✅ No new posts to process. Stop the app!")
        exit()
    print(f"Found {len(df_new)} new posts to process. Start cleaning...")

    # 2. Translating text
    print("🌎 Translating new posts in Vietnamese to English...")
    df_new['final_en_text'] = df_new['full_text'].apply(translated_mixed_text)

    # 3. Calculate sentiments on the translated columns
    print("📊 Analyzing sentiments (VADER & TextBlob)...")
    df_new['vader_score'] = df_new['final_en_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df_new['sentiment_score'] = df_new['final_en_text'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df_new['attitude'] = df_new['sentiment_score'].apply(label_vibe)

    #Check the overall results
    print("💾 Is updating the new dataset with `sentiment_score` & `attitude` scores...")
    print("Is printing the result of Emotion Analysis")
    print(df_new['attitude'].value_counts(normalize=True) *100)

    # 4. Saving the results
    print("💾 Saving processed texts...")
    df_new.to_csv("data/processed/reddit_master.csv", index=False)
    conn = sqlite3.connect(db_path)
    try:
        df_new.to_sql('processed_posts', conn, if_exists="append", index=False)
        print("✅ Incremental update successful!!")
    except Exception as e:
        print(f"Error while saving {e}")
    finally:
        conn.close()

    # # Plot wordcloud
    # plot_wordcloud(df['full_text'])


import os
import pandas as pd
import langdetect
from langdetect import detect, DetectorFactory
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from deep_translator import GoogleTranslator
import re

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


#Load NLP
analyzer = SentimentIntensityAnalyzer()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Delete link component
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

def label_vibe(score):
    if pd.isna(score): return "Neutral 😐"
    if score > 0.1: return "Positive 😊"
    elif score < -0.1: return "Worried/Cautious 😟"
    return "Neutral 😐"

def get_occ(text):
    if pd.isna(text): return "Other/Not Specified"
    text = text.lower()
    for category, keywords in professions_keywords.items():
        for word in keywords:
            if re.search(rf"\b{word}\b", text):
                return category
    return "Other"
      

def process_data(input_path, output_path):
    print("🚀 Starting to process new data...")

    if os.path.exists(output_path):
        master_df = pd.read_csv(output_path)
    else:
        master_df = pd.DataFrame()

    # Read the new 2nd file
    new_df = pd.read_csv(input_path)

    # Combine
    df = pd.concat([master_df, new_df], ignore_index=True)
    
    # 1. Combine title and selftext columns and clean
    df['full_text'] = df['title'].fillna("") + ". "+ df['selftext'].fillna("")
    df['full_text'] = df['full_text'].apply(clean_text)

    # 2. Drop duplicates
    df = df.drop_duplicates(subset=['full_text'], keep = "first")

    # 3. Translate to English
    print("Translating posts in Vietnamese to English & vice versa...")
    ## Only translate the ones that are not translated
    if "final_en_text" not in df.columns:
        df['final_en_text'] = pd.NA

    needs_translation = df['final_en_text'].isna() | (df['final_en_text'] == "")
    if needs_translation.any():
        df.loc[needs_translation, "final_en_text"] = df.loc[needs_translation, 'full_text'].apply(translated_mixed_text)

    #4. Sentimental Analysis
    # For the new posts whose attitude is missing, define label_vibe
    df['final_en_text'] = df['final_en_text'].fillna("").astype(str)
    print("🧠 Analyzing Sentiment...")

    df['vader_score'] = df['final_en_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df['sentiment_score'] = df['final_en_text'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['attitude'] = df['sentiment_score'].apply(label_vibe)
        
   # 5. Extracting Occupation
    df['occupation'] = df['final_en_text'].apply(get_occ)

    #6. Extracting columns and save!
    cols_to_keep = ['final_en_text', 'language', 'subreddit', 'created_utc', 'occupation', 
                    'score', 'city_mentioned', 'sentiment_score', 'attitude', 'vader_score']
    for c in cols_to_keep:
        if c not in df.columns:
            df[c] ="Not Specified" if c == "city_mentioned" else pd.NA

    final_df= df[cols_to_keep]
    final_df.to_csv(output_path, index=False)
    print(f"✅ Saved processed data in {output_path}")

if __name__ == "__main__":
    input_path = r"data/raw/new_scrape_monday.csv"
    output_path = r"data/processed/reddit_master.csv"
    process_data(input_path, output_path)   



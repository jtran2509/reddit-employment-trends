import pandas as pd
import spacy
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
nlp = spacy.load("en_core_web_sm")
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
       continue
    try:
      lang = detect(sent)
      if lang== "vi": # if the sentence is in Vietnamese => translate
        translated_sentences.append(translator.translate(sent))
      else: # is the sentence is in English => keep
        translated_sentences.append(sent)

    except: # If unable to detect any language, keep the same
        translated_sentences.append(sent)
    return ". ".join(translated_sentences)

def process_data(input_path, output_path):
    print("🚀 Starting to process new data...")
    df = pd.read_csv(input_path)

    # 1. Combine title and selftext columns and clean
    df['full_text'] = df['title'].fillna("") + ". "+ df['selftext'].fillna("")
    df['full_text'] = df['full_text'].apply(clean_text)

    # 2. Drop duplicates
    df = df['full_text'].drop_duplicates(subset='full_text')

    # 3. Translate to English
    print("Translating posts in Vietnamese to English & vice versa...")
    df['final_en_text'] = df['full_text'].apply(translated_mixed_text)

    #4. Sentimental Analysis
    print("🧠 Analyzing Sentiment...")
    df['vader_score'] = df['final_en_text'].apply(lambda x: analyzer.polarity_score(x)['compoung'])
    df['polarity'] = df['polarity'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['subjectivity'] = df['subjectivity'].apply(lambda x:TextBlob(x).sentiment.subjectivity)

   # 5. Extracting Occupation
    def get_occ(text):
      text = text.lower()
      for occ in professions_keywords:
        if occ in text:
            return occ.capitalize()
        return "Other"
      
    df['Occupation'] = df['final_en_text'].apply(get_occ)

    # 6. Save file
    df.to_csv(output_path, index=False)
    print(f"✅ Saved processed data in {output_path}")

if __name__ == "__main__":
    process_data("data/raw/new_scrape.csv", "data/processed/reddit_master.csv")
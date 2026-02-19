"""
Will run every Monday morning at 8AM to scrape new dataset for up-to-date results 
"""

import os
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime
import spacy
#1. Scrape raw data from Reddit
subreddits =[
    "VietNam", "Calgary", "askTO", "asianamerican",            
    "CanadaJobs", "povertyfinancecanada", "Layoffs", "antiwork", # General Market
    "ImmigrationCanada", "LMIASCAMS", "OntarioColleges",        # Immigration
    "cscareerquestionsCAD", "VancouverJobs", "canadahousing" #Niche/Regional
]
from scrape_reddit import scrape_reddit_json

def scrape_reddit():
    master_data =[]
    for sub in subreddits:
        sub_data = scrape_reddit_json(sub, post_limit=200) # grab 2 pages per sub
        master_data.extend(sub_data)
        time.sleep(5)

    return master_data

#2. Save raw dataset
def save_raw(master_data):
    df = pd.DataFrame(master_data)
    #Save as CSV for easy viewing
    df.to_csv('data/raw/reddit_employment_master.csv', index=False)
    # Save as JSON for "Data Science" style processing later
    df.to_json('data/raw/reddit_employment_json', orient='records', indent=4)

    return df

# 3. Load dataset, tackle null values

def clean_data(df, file_path):
    reddit_df = pd.read_csv(file_path)

    # 1. Handle the `selftext` & `title` columns
    df['title'] = df['title'].fillna("")
    df['selftext'] = df['selftext'].fillna("")

    # 2. Create `full_text` column
    df['full_text'] = df['title'] + " " +df['selftext']

    # 3. Check after combining 2 columns: any column that is null will be deleted
    df = df[df['full_text'].str.strip() != ""] # Remove "ghost" posts that are not informative

    # 4. Handle `score` columns
    df['score'] = df['score'].fillna(0)
    df['num_comments'] = df['num_comments'].fillna(0)

    #5. If there's no URL or subreddits (VERY RARE!), we'll delete it
    critial_cols = ['subreddit', 'url', 'created_utc']
    df = df.dropna(subset=critial_cols)

    return df

def add_nlp_features(df):
    """
    Use `Spacy` for tokenization, lemmatization, etc.
    
    :param df: dataset to pass in
    """
    df['date'] = pd.to_datetime(df['created_utc'], unit="s")
    # 1. Divide the dataset into English and Vietnamese datasets
    df['lang']

    # 2. Use spacy for English and Underthesea for Vietnamese

    # Sentimental Analysis

    return df

def save_processed(df_new, folder='processed', filename="reddit_master_cleaned.csv"):
    """
    Docstring for save_processed
    
    :param df_new: 
    """
    # Create a proper file path
    file_path = os.path.join(folder, filename)

    # Check directory, if non-existent, create a new one
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    if os.path.exists(file_path):
        # Read the old dataset
        df_old = pd.read_csv(file_path)
        # Chain the old df with the new df
        df_final = pd.concat([df_old, df_new], ignore_index=True)
        # Delete duplicate dataset based on URL (important for scraping every Monday)
        df_final = df_final.drop_duplicates(subset=['url'], keep='last') # help to keep the lastest, up-to-date version (in terms of # of cmt, score, etc.)

    else:
        df_final = df_new

    # Save the new pdf
    df_final = pd.to_datetime(df_final['created_utc'], unit="s").dt.date
    df_final.to_csv(file_path, index= False)
    print(f"Updated dataset {file_path}. Total lines: {len(df_final)}")

# if __name__== "__main__":
#     data = load_data("data.csv")
#     clean_data = preprocess_text(data)
#     data['sentiment_score'] = data['full_text'].apply(get_sentiment_score)

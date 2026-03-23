# Scrape dataset on every Monday
# Avoid scraping the duplicate files
import requests
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime
import sqlite3

#1. Target Subreddits
subreddits =[
    "VietNam", "Calgary", "askTO", "asianamerican",            
    "CanadaJobs", "povertyfinancecanada", "Layoffs", "antiwork", # General Market
    "ImmigrationCanada", "LMIASCAMS", "OntarioColleges",        # Immigration
    "cscareerquestionsCAD", "VancouverJobs", "canadahousing" #Niche/Regional
]

# Connect to SQLite database
db_path = "data/raw/reddit_employment.db"

def get_existing_titles():
    """Get the existing posts from database to compare
    """
    try:
        conn = sqlite3.connect(db_path)
        # Only get the `title` column
        df_old = pd.read_sql_query("SELECT title FROM reddit_posts", conn)
        conn.close()
        # Turned into set to find duplicate faster
        return set(df_old['title'].to_list())
    except Exception as e:
        print("No existing DB, will create new...")
        return set()
    

def scrape_reddit_json(subreddit, post_limit=100):
    """
    Fetch posts from a subreddit using the .json with pagination
    """
    new_sub_posts = []
    after = None
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PortfolioProject/1.0'}
    print(f'--- Starting to scrape for r/{subreddit}')

    # We loop to handle pagination (100 posts per 'page')
    for i in range(0, post_limit, 100):
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"
        if after:
            url+= f"&after={after}"

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']

                for post in posts:
                    post_data = post['data']
                    title = post_data.get("title")

                    # Prevent scraping duplicate posts
                    if title not in existing_titles:
                        new_sub_posts.append({
                        'subreddit': subreddit,
                        'title': post_data.get('title'),
                        'selftext': post_data.get('selftext'),
                        'score': post_data.get('score'),
                        'num_comments': post_data.get('num_comments'),
                        'created_utc': datetime.fromtimestamp(post_data.get('created_utc')).strftime("%Y-%m-%d %H:%M:%S"),
                        'url': f"https://www.reddit.com{post_data.get('permalink')}"
                        })
                        existing_titles.add(title)

                # Update 'after' to the ID of the last post to get the next page
                after = data['data'].get('after')
                if not after:
                    break # No more post availables
                print(f'   > Collected {len(new_sub_posts)} posts so far') 
                time.sleep(2)
            
            elif response.status_code == 429:
                print('!! Rate limit (429). Sleeping for 60 seconds...')
                time.sleep(60)
            else:
                print(f'!! Error {response.status_code} for r/{subreddit}')
                break
        except Exception as e:
            print(f'!! Request failed: {e}')
            break
    return new_sub_posts

if __name__=="__main__":
    existing_titles = get_existing_titles()
    print(f"🛡️ Got {len(existing_titles)} old posts to compare!")

    # 2. run the loop
    master_data =[]
    for sub in subreddits:
        sub_data = scrape_reddit_json(sub, existing_titles, post_limit=300)
        master_data.extend(sub_data)
        time.sleep(5)

    # 3. Save the results
    if len(master_data) > 0:
        df = pd.DataFrame(master_data)

        ## Drop 'author' column (if existing) to protect privacy.
        if "author" in df.columns:
            df = df.drop(columns=['author'])

        # Add scrape_date column
        df['scrape_date'] = datetime.now().strftime("%Y-%m-%d")

        # Save file CSV for backup with datetime for easy recognition
        today = datetime.now().strftime("%Y_%m_%d")
        filename = f"data/raw/new_scrape_{today}.csv"
        df.to_csv(filename, index=False)
        print(f"📁Saved {len(df)} new posts and a backup-CSV safely at {filename}")

        # Save in SQLite databse
        conn = sqlite3.connect(db_path)

        # Use append instead of replace to append new posts to existing database
        df.to_sql("reddit_posts", conn, if_exists="append", index=False)
        conn.close()
        print(f"✅ Successfully saved {len(df)} lines to database 'reddit_posts'.")
    else:
        print("💤 Nothing new is happening in Reddit. Data is still updating...")
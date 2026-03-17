import requests
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime
# Scrape dataset on every Monday

#1. Target Subreddits
subreddits =[
    "VietNam", "Calgary", "askTO", "asianamerican",            
    "CanadaJobs", "povertyfinancecanada", "Layoffs", "antiwork", # General Market
    "ImmigrationCanada", "LMIASCAMS", "OntarioColleges",        # Immigration
    "cscareerquestionsCAD", "VancouverJobs", "canadahousing" #Niche/Regional
]

def scrape_reddit_json(subreddit, post_limit=100):
    """
    Fetch posts from a subreddit using the .json with pagination
    """
    all_posts = []
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
                children = data['data']['children']

                for post in children:
                    p = post['data']
                    all_posts.append({
                        'subreddit': subreddit,
                        'title': p.get('title'),
                        'selftext': p.get('selftext'),
                        'author': p.get('author'),
                        'score': p.get('score'),
                        'num_comments': p.get('num_comments'),
                        'created_utc': datetime.fromtimestamp(p.get('created_utc')).strftime("%Y-%m-%d %H:%M:%S")
                    })
                # Update 'after' to the ID of the last post to get the next page
                after = data['data'].get('after')
                if not after:
                    break # No more post availables

                print(f'   > Collected {len(all_posts)} posts so far') 
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
    return all_posts

# 2. Run the loop
master_data =[]
for sub in subreddits:
    sub_data = scrape_reddit_json(sub, post_limit=200) # grab 2 pages per sub
    master_data.extend(sub_data)
    time.sleep(5)

# 3. Save the results
df = pd.DataFrame(master_data)
#Save newly scraped data with datetime for easy recognition
today = datetime.now().strftime("%Y_%m_%d")
filename = f"data/raw/new_scrape_{today}.csv"

df.to_csv(filename, index=False)
print(f"---Saved new data to {filename}")
# Save as JSON for "Data Science" style processing later
df.to_json('data/raw/reddit_employment_json', orient='records', indent=4)

print(f'\n SUCCESS! Total posts collected: {len(df)}')


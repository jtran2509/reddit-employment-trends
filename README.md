# Comprehensive Market Intelligence Dashboard
## Purpose of the project

## How it works
Every Monday, when new data coming in:
1. Read newly-scraped data
2. Run `clean_database.py` to remove any duplicates that resulted from scraping the same posts twice
3. Read the old `reddit_master`
4. Combine the new dataset with the old dataset
5. Save them as the new `reddit_master`

## Tech Stacks

## Data Pipeline Structure
1. Data Extraction (scrape_reddit.py)
- Tasks: Scrape new data every monday
- How: Use `set` to compare with SQLite & stop scraping the duplicate posts from the moment calling API. Delete `author` column and add `scrape_date` for easy retrieval.
- Output: Append the newly-scraped data into the existing database `reddit_posts` 

2. Data Tranformation and Text Processing (text_pipeline.py)
- Tasks: Cleaning and scoring basic sentiments
- How: Only choose the posts that are not yet scored. Automatically locate posts in Vietnamese and translate to English. Use VADER score, TextBlob and assign `attitude` (positive, negative or neutral)
- Output: Append the scores to the table `processed_posts`

3. AI categorization (bert_analysis.py)
- Tasks: Use deep-learning model (BART-large-mnli) to categorize topic
- How: Use SQL to retrieve the newly-scraped data without the bert topic, use AI to categorize the newly scraped-data only
- Output: Save a new file that contains categories results

4. Data Merging (merge_bert.py)
- Tasks: Update the new result and append it to the original database
- How: Use Pandas's `update()` function to fill exactly the null cells based on `title` column without messing up the old data

5. Visualization & deployment (dashboard.py)
- Task: visualize the data on website
- How: Dashboard only "read" the clean data after all of the processing. WorkCloud is optimized to avoid overloading RAM.

## Advantage of Textblob and VADER
- Vader: optimized for social media but VADER tends to amplify polarity and often categorize too many posts as positives
- Textblob: offer a subjecctivity score (0.00 to 1.00) in addition to polarity (sentiment)

## Defining "pain points"
- A specific topic (BERT Topic) + Disappointment/Frustration (Negative Attitude/Negative VADER score)
- e.g. `Salary and Cost of Living` + (-0.85) VADER score => Salary is not high/competitve enough and the user is expressing their frustration/disappointment/complaint. 
- `Lack of Canadian Experience` + (-0.9) VADER score: sending out 500 CV but got no calls back -> User is expressing their disappoinment.

## Streanlit dashboard
1. Overview
- Number of jobs posts this week
- Subreddit activity
- Most common job titles

2. Location insights
- Map or bar chart of Canadian cities mentioned

3. Salary insights
- Salary distribution
- High-risks salaries

5. Topic trends
- Topics per week (via BERTopic)
- Rising and falling categories

6. Raw Reddit explorer
- Search bar
- Filter by subreddits, keyword, city or scam flag

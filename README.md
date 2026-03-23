# Reddit Canada Employment Trend
An end-to-end NLP & AI pipeline for analyzing job market insights from Reddit
[Link to Live Dashboard](https://reddit-employment-trends.streamlit.app/)
## Project overview
- This project aims to scrape Reddit data and analyze it from the Reddit community in Canada to find out "pain points" of job seekers and immigrants

## 🛠 Tech Stacks
- Data Source: Reddit API (RAW JSON fetching)
- Database: SQLite (Incremental Loading logic)
- NLP: VADER, TextBlob (Sentiment Analysis), Google Translate API
- AI model: BERT (facebook/bart-large-mini) for Zero-shot classification
- Dashboard: Streamlit & Plotly

## The Data Pipeline (Workflow)
Every Monday, when new data coming in:
1. Scraping: Scrape new data, use `set` to filter duplicates to make sure it doesn't mess up with the dashboard.
2. Text processing: Automatically translate Vietnamese posts to English and score the sentiment
3. AI labeling: Run BERT model on the new posts only to save resources and time
4. Data Merging: Update the newly-scraped dataset's label to the original database using update method
5. Visualization: Visualize the trend in the job market using Streamlit Cloud

If you want to see in details, [click here!](#data-pipeline-structure-specifically)

## Repository Structure
- `dashboard.py`: Main file to run web dashboard
- `scripts/`: contains all of the pipeline workflow (e.g. scraping data, cleaning text, etc.)
- `data/`: where the database lies
- `Dockerfile`: cau hinh environment to run the app. 


## Data Pipeline Structure (SPECIFICALLY)
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
1. Market pulse
- Community Sentiment Analysis overall
- Top topics per week (via BERT topic)
- Reddit's community attitude over a specific timeframe

2. Technical Skills
- Wordcloud: show users top keywords that was mentioned the most in the Reddit community
- Map or bar chart of Canadian cities mentioned

3. Immigration Insights
- Posts that are flagged as potential SCAMs
- Percentage of Positive/Negative in terms of topics

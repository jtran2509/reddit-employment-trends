# Comprehensive Market Intelligence Dashboard
## Purpose of the project

## How it works
Every Monday, when new data coming in:
1. Read newly-scraped data
2. Read the old `reddit_master`
3. Combine the new dataset with the old dataset
4. Remove duplicates: we might scrape the same old post from last week
5. Save them as the new `reddit_master`

## Tech Stacks

## Improvement 
- 



## Advantage of Textblob and VADER
- Vader: optimized for social media but VADER tends to amplify polarity and often categorize too many posts as positives
- Textblob: offer a subjecctivity score (0.00 to 1.00) in addition to polarity (sentiment)

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

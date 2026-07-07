# Reddit Canada Employment Trend
<!-- Badges Section -->
<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  </a>
  <a href="https://huggingface.co/facebook/bart-large-mnli">
    <img src="https://img.shields.io/badge/BERT-BART--large--mnli-yellow?style=for-the-badge&logo=HuggingFace&logoColor=white" alt="BERT Model">
  </a>
  <a href="https://www.microsoft.com/en-us/power-platform/products/power-bi">
    <img src="https://img.shields.io/badge/Power%20BI-Dashboard-FFB81C?style=for-the-badge&logo=Power%20BI&logoColor=white" alt="Power BI">
  </a>
  <a href="https://www.sqlite.org/">
    <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=SQLite&logoColor=white" alt="SQLite">
  </a>
  <a href="https://github.com/your-username/your-repo-name/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  </a>
</p>
An end-to-end NLP & AI pipeline for analyzing job market insights from Reddit

# Demo link: [Reddit Employment Trends](https://reddit-employment-trends-c7mf5bu4wr68bgmejrorqu.streamlit.app/)

![Reddit Employment Trend Demo](https://i.imgur.com/NIjRIfT.gif)

## 📃 Project overview
- This project aims to help newcomers/immigrants get a better understanding of the Canada job market by scraping Reddit data and analyze it from the Reddit community in Canada. The ultimate purpose is to find out the "pain points" of job seekers and immigrants

## 🛠 Tech Stacks
- Data Source: Reddit API (RAW JSON fetching)
- Database: SQLite (Incremental Loading logic)
- NLP: VADER, TextBlob (Sentiment Analysis), Google Translate API
- AI model: BERT (facebook/bart-large-mini) for Zero-shot classification
- Dashboard: Streamlit & Plotly

## ⚙ The Data Pipeline (Workflow)
Every Monday, when new data coming in:
1. Scraping: Scrape new data, use `set` to filter duplicates to make sure it doesn't mess up with the dashboard.
2. Text processing: Automatically translate Vietnamese posts to English and score the sentiment
3. AI labeling: Run BERT model on the new posts only to save resources and time
4. Data Merging: Update the newly-scraped dataset's label to the original database using update method
5. Visualization: Visualize the trend in the job market using Streamlit Cloud

If you want to see the details, [click here!](#data-pipeline-structure-specifically)

## 📂 Repository Structure
- `dashboard.py`: Main file to run web dashboard
- `scripts/`: contains all of the pipeline workflow (e.g. scraping data, cleaning text, etc.)
- `data/`: where the database lies
- `Dockerfile`: cau hinh environment to run the app. 


## 🧰 Data Pipeline Structure (SPECIFICALLY)
1. Data Extraction (scrape_reddit.py)
- Tasks: Scrape new data every Monday (in planning phase)
- How: Use `set` to compare with SQLite & stop scraping duplicate posts from the moment the API. Delete the `author` column and add `scrape_date` for easy retrieval.
- Output: Append the newly scraped data into the existing database `reddit_posts`  - incremental loading

2. Data Transformation and Text Processing (text_pipeline.py)
- Tasks: Cleaning and scoring basic sentiments
- How: Only choose the posts that are not yet scored. Automatically locate posts in Vietnamese and translate to English. Use VADER score, TextBlob and assign `attitude` (positive, negative or neutral)
- Output: Append the scores to the table `processed_posts`

3. AI categorization (bert_analysis.py)
- Tasks: Use deep-learning model (BART-large-mnli) to categorize topics
- How: Use SQL to retrieve the newly scraped data without the bert topic, use AI to categorize the newly scraped-data only
- Output: Save a new file that contains categories' results

4. Data Merging (merge_bert.py)
- Tasks: Update the new result and append it to the original database
- How: Use Pandas's `update()` function to fill exactly the null cells based on `title` column without messing up the old data

5. Visualization & deployment (dashboard.py)
- Task: visualize the data on website
- How: Dashboard only "read" the clean data after all of the processing. WorkCloud is optimized to avoid overloading RAM.

## 👍 Advantage of TextBlob and VADER
- **VADER (Valence Aware Dictionary and Sentiment Reasoner)**: specfifically optimized for social media contexts. VADER can handle slang, capitalization (e.g. "FRUSTRATED), and emojis. However, VADER tends to amplify polarity and often categorize too many posts as positive
- ** TextBlob **: to balance VADER'S polarity, TextBlob offers a subjectivity score (0.00 to 1.00) in addition to polarity (sentiment), which is crucial for identifying "pain points"

## 🤕 Defining "pain points"
- A specific topic (BERT Topic) + Disappointment/Frustration (Negative Attitude/Negative VADER score)
- e.g. `Salary and Cost of Living` + (-0.85) VADER score => Salary is not high/competitve enough and the user is expressing their frustration/disappointment/complaint. 
- `Lack of Canadian Experience` + (-0.9) VADER score: sending out 500 CV but got no calls back -> User is expressing their disappoinment.

## 🆙 What can be improved upon this work
- When more & more dataset coming in with different languages, we can build more extensive text_pipeline that includes:
* Classify languages for each posts that is not exclusive to Vietnamese but also other languages (Japanses, French, Spanish, Chinese, Korean, etc.)
* Translating non-Englilsh sentence into English
* Combine all of the post-translate-English sentences and do the BERT topic
- Machine learning-wise:
* Scam detector (Realistic Classifier): create a "Text" box so users can paste in the hiring posts of a recruiter, and the model will give the results saying how confident it is that this hiring message is a SCAM 
* Time series analysis - whether there's an increase in the number of posts about SCAMs. **Any relevance to the new immigration policies?**
* Instead of VADER, can utilize HuggingFace pipeline for more nuanced results

## 👨‍💼 Business Impact
* **Strategic Insights for Newcomers**: provides a data-driven reality check on the Canadian Job market, helping immigrants identify systemic barriers (e.g. Canadian experiments are the hot topic) and prepare more effective integration strategies
* **Risk Mitigation & Fraud Awareness**: by analyzing frequency and sentiment trends, the pipeline has the potential to flag emerging recruitment scams, protecting vulnerable job seekers from financial and professional harm.
* **Data-driven Advocacy for Policymakers**: offers evidence-based insights into the "pain points" of international talent. 

## 📖 Streanlit dashboard
1. Market pulse
- Community Sentiment Analysis overall
- Top Occupations Mentioned Most during the time frame
- Reddit's community attitude over a specific timeframe (P/N)

2. Technical Skills
- Wordcloud: show users top keywords that was mentioned the most in the Reddit community
- Map or bar chart of Canadian cities mentioned in each Subreddit

3. Immigration Insights
- Posts that are flagged as potential SCAMs or SCAM-arising-concerns.
- "Pain points" posts that talks about Reddits' users frustration according to each Subreddit topic

import sqlite3
import pandas as pd
from transformers import pipeline

# Download Zero-shot Classification model (BART-Large)
print("⏳ Is downloading AI model from Hugging Face... (will take several minutes)")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("✅ Sucessfully loaded model done!")

# Connect to database
db_path = "data/raw/reddit_employment.db"
conn = sqlite3.connect(db_path)

# Only get 50 lines to test
# query = "SELECT title, full_text FROM processed_posts" # 1st time running the code for >8000 posts
query = "SELECT title, final_en_text FROM processed_posts WHERE bert_topic IS NULL"
df_unlabeled = pd.read_sql_query(query, conn)
conn.close()

# Define aspect we want to change the label
candidate_labels = ["Resume & Interview Struggles", "LMIA, Visa & Immigrations",
                    "Fake Jobs & Scam Warning", "Workplace-related & Layoffs",
                    "Salary & Cost of Living", "Lack of Canadian Exp.",
                    "Career, Network and Education"]

# Function to categorize each posts
def get_bert_topic(text):
    # Only get the first 1500 characters, if longer -> error
    short_text = str(text)[:1500]

    # Machine will categorize each title
    result = classifier(short_text, candidate_labels)
    top_label = result['labels'][0]
    top_score = result['scores'][0]

    return top_label, top_score

# Run BERT on the newly scraped dataset
if df_unlabeled.empty:
    print("All of the posts has been categoried by BERT!")
else:
    print(f"🧠 Starting BERT for {len(df_unlabeled)} new posts")
    df_unlabeled[['bert_topic', 'confidence_score']] = df_unlabeled['final_en_text'].apply(lambda x: pd.Series(get_bert_topic(x)))
    # Check the results
    print("\n --- Results from BERT analysis")
    print(df_unlabeled[['title', 'bert_topic', 'confidence_score']].head(10))

    # Save the results to the new CSV file
    df_unlabeled[['title', 'bert_topic', 'confidence_score']].to_csv("new_bert_results.csv", index = False)
    print("Complete labeling the newly scraped posts!")
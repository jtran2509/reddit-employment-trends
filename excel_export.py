import sqlite3
import pandas as pd

# Connect to SQLite 
conn = sqlite3.connect("data/raw/reddit_employment.db")

# Load the data"
df = pd.read_sql_query("SELECT * FROM processed_posts", conn)

# Export df into excel
df.to_excel("reddit_processed_posts.xlsx", index=False)

conn.close()
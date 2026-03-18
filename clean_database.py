# Clean duplicate posts after scraping new data

import sqlite3
import pandas as pd

db_path = r"data/raw/reddit_employment.db"
conn = sqlite3.connect(db_path)

# Read all of the data from SQL into dataframe
df = pd.read_sql_query("SELECT * FROM reddit_posts", conn)
print(f"--- Total lines collected now: {len(df)}")

# Delete duplicate resulted from scraping
df_clean = df.drop_duplicates(subset=['title'], keep="first")

print(f"Total lines after deleting duplicates: {len(df_clean)}")
print(f"Removed total: {len(df) - len(df_clean)} of duplicate lines")

# Overwrite the new clean df into database
try:
    df_clean.to_sql("reddit_posts", conn, if_exists="replace", index=False)
    print(f"Updated the new clean database")
except Exception as e:
    print(f"Error when updating {e}")
finally:
    conn.close()
import pandas as pd
import sqlite3

# Read old CSV file
old_file_path = r"data/raw/new_scrape_monday.csv"
df_old = pd.read_csv(old_file_path)

print(f"Is processing old file: {old_file_path}")

# 2. Delete the `author` column
if "author" in df_old.columns:
    df_old = df_old.drop(columns=["author"])
    print("Deleted 'author' column from the old dataset")

# 3. Adding `scraped_date` column
df_old['scrape_date'] = "2026-02-11"

# 4. Add to dataframe
db_path = "data/raw/reddit_employment.db"
conn = sqlite3.connect(db_path)

try:
    df_old.to_sql("reddit_posts", conn, if_exists="replace", index=False)
    print(f"Moved {len(df_old)} lines into database succesfully.")
except Exception as e:
    print(f"!! Error {e}")
finally:
    conn.close()
    
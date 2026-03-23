# Merge only the newly-scraped posts to the existing database"

import sqlite3
import pandas as pd

db_path = "data/raw/reddit_employment.db"
# csv_path = "data/raw/bert_full_result.csv" # 1st time running
csv_path = "data/raw/new_bert_results.csv"

print("Is reading datasets...")
# Read the current database
conn = sqlite3.connect(db_path)
# Read all of the posts present in the database after BERT analysis
df_db = pd.read_sql_query("SELECT * FROM processed_posts", conn)

# Read result from newly-scraped file
df_new_bert = pd.read_csv(csv_path)

#Merge 2 tables together
print("Is merging 2 tables together...")

# Set title column to index to notify Pandas which row to merge
df_db.set_index("title", inplace=True)
df_new_bert.set_index("title", inplace=True)

# Get the new data from df_new_bert to append to the existing df_db
df_db.update(df_new_bert)

# Reset index to turn "title" back to normal column
df_db.reset_index(inplace=True)

#Overwrite back to the database
# df_final = pd.merge(df_db, df_new_bert, on="title", how="left")

# #Save them together
# try:
#     df_final.to_sql("processed_posts", conn, if_exists="replace", index=False)
#     print("✅ Finished combining! The table 'processed_posts' is now updated with BERT topic.")
# except Exception as e:
#     print(f"Error when combining {e}")
# finally: 
#     conn.close()
df_db.to_sql("processed_posts", conn, if_exists="replace", index=False)
conn.close()
print("✅ Finish updating! Open Streamlit to see newly-update data!")
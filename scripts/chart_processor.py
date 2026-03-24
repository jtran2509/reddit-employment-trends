import pandas as pd 
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

## PART 1: Processing data
professions_keywords = {
    'IT/Tech': ['it', 'tech', 'software', 'developer', 'engineer', 'data scientist', 'programmer', 'cybersecurity', 'ai', 'devops', 'web development', 'frontend', 'backend', 'fullstack'],
    'Marketing': ['marketing', 'digital marketing', 'seo', 'sem', 'social media', 'content creator', 'advertising', 'brand', 'campaign'],
    'Cook/Chef': ['cook', 'chef', 'kitchen', 'restaurant', 'food service', 'hospitality'],
    'Healthcare': ['nurse', 'doctor', 'physician', 'healthcare', 'medical', 'hospital', 'caregiver', 'pharmacist'],
    'Trades': ['carpenter', 'electrician', 'plumber', 'welder', 'mechanic', 'construction'],
    'Admin/Office': ['admin', 'administrative', 'assistant', 'office manager', 'receptionist'],
    'Retail': ['retail', 'sales associate', 'cashier', 'store manager'],
    'Logistics': ['driver', 'logistics', 'warehouse', 'supply chain', 'trucker'],
    'Education': ['teacher', 'educator', 'professor', 'school', 'tutor'] }

## Lists of big cities in Canada
cities = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Edmonton', 'Ottawa', 'Winnipeg',
          'Quebec City', 'Hamilton', 'Kitchener', 'London', 'Victoria', 'Halifax',
          'Brossard', 'Brampton', 'Missisauga']

def get_profession_count(df, profession_keywords):
    profession_counts = {profession: 0 for profession in professions_keywords.keys()}

    for text in df['final_en_text']:
        if pd.isna(text):
            continue
        text_lower = text.lower()

        for profession, keywords in professions_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    profession_counts[profession] +=1
                    break # only count once per profession per post, some post might contains more keyword
    # Convert to Dataframe for plotting
    profession_df = pd.DataFrame(profession_counts.items(), columns=["Profession", "Count"])
    # Sort for better visualization
    return profession_df.sort_values(by="Count", ascending=True)

def get_cities_count(df, cities_list):
    ## Initialize a dictionary to store the list of city_mentioned
    def find_cities(text):
        if pd.isna(text):
            return "Unknown"
        text_lower = text.lower()
        for city in cities:
            if city.lower() in text_lower:
                return city
        return "Not Mentioned"
    
    df['city_mentioned']= df['final_en_text'].apply(find_cities)
    # Remove the posts that don't contain cities
    city_counts = df[df['city_mentioned'] != 'Not Mentioned']['city_mentioned'].value_counts()
    # Convert to Dataframe for plotting
    city_df = pd.DataFrame(city_counts.items(), columns=["City", "Count"])
    # Sort for better visualization
    return city_df.sort_values(by="Count", ascending=True)

## PART 2: PLOTTING THE DATA
def plot_bar_chart(df, x_col, y_col, title, color_scale='Virisdis'):
    fig = px.bar(df, x=x_col, y=y_col, orientation="h", title=title,
                 labels={x_col: "Mentions", y_col: y_col},
                 color=x_col, text=x_col)
    fig.update_layout(showlegend=False)
    return fig

def generate_wordcloud(text_series, custom_stopwords):
    all_text = " ".join(str(text) for text in text_series if pd.notna(text))
    wc = WordCloud(width=1000, height=500, random_state=42, 
                                background_color="white",
                                stopwords=custom_stopwords,
                                colormap="magma").generate(all_text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig

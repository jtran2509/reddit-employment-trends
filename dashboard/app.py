import streamlit as st
import os
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import plotly.express as px
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import warnings
from visualizer import generate_wordcloud, filter_posts_by_occupation, PROFESSIONS_KEYWORDS
from data_loader import (
    load_raw_data, load_occupation_data, 
    load_cities_data, load_sentiment_data, 
    load_trend_data, load_pain_points, 
    load_lmia_scam_posts, calculate_sentiment_stats,
    compute_trend_from_filtered)

# Call css.file
def local_css(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, file_name)
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Page config
st.set_page_config(
    page_title="Reddit Employment Pulse",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =================================
# Load dataset
df = load_raw_data()
df['date'] = pd.to_datetime(df['date']).dt.date
df_trend = load_trend_data(df)
df_occupations = load_occupation_data(df)
num_occupations = len(df_occupations)
sentiment_counts, avg_vader, avg_textblob, sentiment_msg = load_sentiment_data(df)

total_mentions = df_occupations['Mentions'].sum()
top_occupation = df_occupations.iloc[-1]['Occupation']
top_mentions = df_occupations.iloc[-1]['Mentions']
top_percentage = round((top_mentions / total_mentions) *100, 1)

# ====== HEADER ==============
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="pulse-header">', unsafe_allow_html=True)
    st.markdown('<h1 style="margin:0;">📊 Reddit Employment Pulse</h1>', unsafe_allow_html=True)
    st.markdown('<span class="live-badge">🔴 LIVE</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<p style="color:#a0a0b0; text-align:right;">Last updated: {datetime.now().strftime("%b %d, %H:%M")}<br>{len(df):,} posts analyzed</p>', unsafe_allow_html=True)

placeholder = st.empty()
with placeholder.container():
    st.markdown(f'<p style="color:#a0a0b0; text-align:right;">🕐 Live as of {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
                unsafe_allow_html=True)

# =====SIDEBAR FILTERS ========
with st.sidebar:
    st.markdown("## 🎛 Filter")

    # Date range
    st.markdown("### 📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=df['date'].min())
    with col2:
        end_date = st.date_input("To", value=df['date'].max())

    # Convert after  date_input
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    #Subreddit filter
    st.markdown("### 🌎 Subreddit")

    # Get the subreddit sets that we scraped!
    all_subreddits = sorted(df['subreddit'].unique().tolist())
    if "subreddit_select" not in st.session_state:
        st.session_state['subreddit_select'] = all_subreddits

    subreddits = st.multiselect(
        "Select communities",
        options = all_subreddits,
        default= st.session_state.get('subreddit_select', all_subreddits),
        key='subreddit_multiselect'
    )
    st.session_state['subreddit_select'] = subreddits

    col_select1, col_select2 = st.columns(2)
    with col_select1:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state['subreddit_select'] = all_subreddits
            st.rerun()
    
    with col_select2:
        if st.button("❌ Clear All", use_container_width=True):
            st.session_state['subreddit_select'] = []
            st.rerun()

    # Sentiment Filter
    st.markdown("### 🧐 Sentiment")
    sentiment_filter = st.radio(
        "Show",
        options=["All", "Positive", "Neutral", "Negative"],
        horizontal=True
    )

    st.markdown("---")
    st.markdown(f"*Data refreshed: {datetime.now().strftime('%H:%M:%S')}*")
    if st.button("🔁 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# === APPLY FILTER TO CHOSEN SUBREDDIT ====
# Filter subreddit
if subreddits:
    df_filtered = df[df['subreddit'].isin(subreddits)]
else:
    df_filtered = df.copy()

# Filter date range
df_filtered = df_filtered[
    (df_filtered['date'] >= start_date) &
    (df_filtered['date'] <= end_date)
]
# Filter sentiment
if sentiment_filter != "All":
    if sentiment_filter == "Negative":
        # Negative có thể là "Worried/Negative 😟" hoặc "Negative"
        df_filtered = df_filtered[df_filtered['attitude'].str.contains('Negative|Worried', case=False, na=False)]
    else:
        df_filtered = df_filtered[df_filtered['attitude'].str.contains(sentiment_filter, case=False, na=False)]

# METRIC CARDS
# ============================================
sent_stats = calculate_sentiment_stats(df_filtered)
df_trend_filtered = compute_trend_from_filtered(df_filtered)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'''
    <div class="metric-card">
    <p style="color:#a0a0b0; font-size:0.85rem; margin:0 0 0.5rem 0;">📋 Total Posts Analyzed</p>
    <p style="color:#00f5d4; font-size:2rem; font-weight:800; margin:0;">{len(df_filtered):,}</p>
    <p style="color:#a0a0b0; font-size:0.8rem; margin:0.5rem 0 0 0;">Across all subreddits</p>
    </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
    <div class="metric-card">
    <p style="color:#a0a0b0; font-size:0.85rem; margin:0 0 0.5rem 0;">🏆 Top Occupation</p>
    <p style="color:#00f5d4; font-size:2rem; font-weight:800; margin:0;">{top_occupation}</p>
    <p style="color:#a0a0b0; font-size:0.8rem; margin:0.5rem 0 0 0;">{top_mentions:,} mentions ({top_percentage}%)</p>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
    <p style="color:#a0a0b0; font-size:0.85rem; margin:0 0 0.5rem 0;">😊 Positive Sentiment</p>
    <p style="color:#00f5d4; font-size:2rem; font-weight:800; margin:0;">{sent_stats['pos_pct']}%</p>
    <p style="color:#a0a0b0; font-size:0.8rem; margin:0.5rem 0 0 0;">{sent_stats['total']:,} filtered posts</p>
    </div>
    ''', unsafe_allow_html=True)

with col4:
        st.markdown(f'''
        <div class="metric-card">
            <p style="color:#a0a0b0; font-size:0.85rem; margin:0 0 0.5rem 0;">🔍 Occupations Tracked</p>
            <p style="color:#00f5d4; font-size:2rem; font-weight:800; margin:0;">{num_occupations}</p>
            <p style="color:#a0a0b0; font-size:0.8rem; margin:0.5rem 0 0 0;">Unique categories</p>
        </div>
        ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# ============================================

# MAIN CONTENT
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💬 Deep Dive", "💡 Insights"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        # Interactive bar chart with Plotly
        fig = px.bar(
            df_occupations,
            x = "Mentions",
            y="Occupation",
            orientation="h",
            color="Mentions",
            color_continuous_scale="viridis",
            title="Occupation Distribution"
        )
        fig.update_layout(template="plotly_dark", 
                          height=500,
                          plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)",
                          yaxis={'categoryorder':'total ascending'}
                          )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown('### 💡 Key Takeaway')
        st.markdown(f'**{top_occupation}** dominates the conversation with **{top_percentage}%** of all occupation mentions.')
        st.markdown('')
        # Finf most positive and most negative occupation
        if not df_filtered.empty:
            # Get the top 5 occupations
            top_5_occ = df_occupations.tail(5)['Occupation'].tolist()
            best_occ, best_pos = None, 0
            worst_occ, worst_neg = None, 0

            for occ in top_5_occ:
                occ_posts = filter_posts_by_occupation(df_filtered, occ)
                if not occ_posts.empty and len(occ_posts) >=3:
                    occ_stats = calculate_sentiment_stats(occ_posts)
                    if occ_stats['pos_pct'] > best_pos:
                        best_pos = occ_stats['pos_pct']
                        best_occ = occ
                    if occ_stats['neg_pct'] > worst_neg:
                        worst_neg = occ_stats['neg_pct']
                        worst_occ = occ
            st.markdown('')
            if best_occ:
                st.markdown(f"📈 **Most positive**: {best_occ} ({best_pos}% positive)")

            if worst_occ:
                st.markdown(f"📈 **Most negative**: {worst_occ} ({worst_neg}% negative)")

            # Insights regarding top occupations
            top_occ_posts = filter_posts_by_occupation(df_filtered, top_occupation)
            if not top_occ_posts.empty:
                top_occ_stats = calculate_sentiment_stats(top_occ_posts)
                st.markdown("")
                st.markdown(f'*{top_occupation} sentiment: {top_occ_stats["pos_pct"]}% positive, {top_occ_stats["neg_pct"]}% negative ({len(top_occ_posts)} posts)*')
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        fig_sentiment = px.pie(
            values=[sent_stats['pos_val'], sent_stats['neu_val'], sent_stats['neg_val']],
            names=["Positive 😁", "Neutral 😐", "Negative 😣"],
            title="Overall Sentiment Distribution",
            color_discrete_sequence=['#00f5d4', '#ffd166', '#ff6b6b'],
            hole=0.4 # Donut chart
        )
        fig_sentiment.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sentiment, use_container_width=True)
    with col4:
        # Time-series trend
        st.markdown("### 📈 Sentiment Trend")
        if df_trend_filtered is not None and not df_trend_filtered.empty:
            trend_melted = df_trend_filtered.melt(
                id_vars=['date'],
                value_vars = ['Positive', 'Neutral', 'Negative'],
                var_name = 'Sentiment',
                value_name = "Count"
            )
            fig_trend = px.line(
                trend_melted,
                x="date",
                y = "Count",
                color = "Sentiment",
                color_discrete_map= {
                    'Positive': '#00f5d4',
                    'Neutral': '#ffd166',
                    'Negative': '#ff6b6b'
                },
                title="Sentiment Trend Over Time"
            )
            fig_trend.update_layout(
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor="rgba(0,0,0,0)",
                height=400
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis")
        

with tab2:
    st.markdown("## 💬 Occupation Deep Dive")

    occ_options = ['📊 All Occupations'] + df_occupations['Occupation'].tolist()
    selected_occ = st.selectbox("Select Occupation to analyze:", occ_options)

    # ===== XỬ LÝ THEO LỰA CHỌN =====
    if selected_occ == "📊 All Occupations":
        # --- HIỂN THỊ TỔNG QUAN TẤT CẢ OCCUPATIONS ---
        all_occ_text = df_filtered['final_en_text'].dropna()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 😎 Overall Sentiment Distribution")
            if not df_filtered.empty:
                fig_all_sent = px.pie(
                    values=[sent_stats['pos_val'], sent_stats['neu_val'], sent_stats['neg_val']],
                    names=['Positive 😁', 'Neutral 😐', 'Negative 😣'],
                    color_discrete_sequence=['#00f5d4', '#ffd166', '#ff6b6b'],
                    hole=0.4,
                    title="Sentiment Across All Occupations"
                )
                fig_all_sent.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=400
                )
                st.plotly_chart(fig_all_sent, use_container_width=True)
            else:
                st.info("No data available with current filters.")

        with col2:
            st.markdown("### 🔑 Top Keywords - All Occupations")
            if not all_occ_text.empty:
                wc_fig = generate_wordcloud(
                    all_occ_text,
                    title="Keywords Across All Occupations"
                )
                if wc_fig:
                    st.pyplot(wc_fig, use_container_width=True)
                else:
                    st.info("Not enough text to generate word cloud.")
            else:
                st.info("No data available for word cloud.")

    else:
        # --- HIỂN THỊ CHO TỪNG OCCUPATION CỤ THỂ ---
        occ_posts = filter_posts_by_occupation(df_filtered, selected_occ)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 😊 Sentiment for {selected_occ}")

            if not occ_posts.empty and "attitude" in occ_posts.columns:
                occ_sentiment = occ_posts['attitude'].value_counts()

                # Đổi tên hiển thị cho đẹp (bỏ emoji gốc, nhóm lại)
                rename_map = {}
                for k in occ_sentiment.index:
                    if 'Positive' in k:
                        rename_map[k] = 'Positive 😊'
                    elif 'Neutral' in k:
                        rename_map[k] = 'Neutral 😐'
                    elif 'Negative' in k or 'Worried' in k:
                        rename_map[k] = 'Negative 😞'
                    else:
                        rename_map[k] = k  # Giữ nguyên nếu không khớp

                occ_sentiment_renamed = occ_sentiment.rename(index=rename_map)
                # Gộp các key trùng nhau (nếu có)
                occ_sentiment_final = occ_sentiment_renamed.groupby(level=0).sum()

                fig_occ_sent = px.bar(
                    x=occ_sentiment_final.index,
                    y=occ_sentiment_final.values,
                    color=occ_sentiment_final.index,
                    color_discrete_map={
                        'Positive 😊': '#00f5d4',
                        'Neutral 😐': '#ffd166',
                        'Negative 😞': '#ff6b6b'
                    },
                    title=f"Sentiment Breakdown: {selected_occ}",
                    labels={"x": "Sentiment", "y": "Number of Posts"}
                )
                fig_occ_sent.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_occ_sent, use_container_width=True)

                total_occ = len(occ_posts)
                st.caption(f"📌 {total_occ} posts mention {selected_occ}")
            else:
                st.info(f"No posts found mentioning {selected_occ} in the selected filters.")

        with col2:
            st.markdown(f"### 🔑 Top Keywords - {selected_occ}")

            if not occ_posts.empty:
                wc_fig = generate_wordcloud(
                    occ_posts['final_en_text'],
                    title=f"Keywords in {selected_occ} Discussions"
                )
                if wc_fig:
                    st.pyplot(wc_fig, use_container_width=True)
                else:
                    st.info("Not enough text to generate word cloud.")
            else:
                st.info("No data available for word cloud.")

    # ===== SAMPLE POSTS (CHUNG CHO CẢ HAI) =====
    st.markdown("---")
    st.markdown("### 📝 Sample Posts from Reddit")

    # Nếu đang chọn 1 occupation cụ thể, lấy sample từ posts của occupation đó
    if selected_occ != "📊 All Occupations":
        occ_posts = filter_posts_by_occupation(df_filtered, selected_occ)
        sample_source = occ_posts if not occ_posts.empty else df_filtered
    else:
        sample_source = df_filtered

    sample_posts = sample_source.nlargest(5, 'score')[['title', 'subreddit', 'date',
                                                        'score', 'url', 'attitude']]

    if not sample_posts.empty:
        for i, row in sample_posts.iterrows():
            sentiment_color = {
                "Positive": "#00f5d4",
                "Neutral": "#ffd166",
                "Negative": "#ff6b6b"
            }.get(row['attitude'], "#a0a0b0")

            st.markdown(f'''
            <div class="metric-card" style="margin-bottom: 0.8rem;">
                <p style="color:{sentiment_color}; font-size:0.8rem; margin:0 0 0.3rem 0;">
                    r/{row['subreddit']} • {row['date']} • ⬆️ {row['score']} upvotes • {row['attitude']}
                </p>
                <p style="color:#e0e0e0; margin:0; font-size:0.95rem;">{str(row['title'])[:200]}{"..." if len(str(row['title'])) > 200 else ""}</p>
                <a href="{row['url']}" target="_blank" style="color:#00f5d4; font-size:0.75rem;">🔗 View on Reddit →</a>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No posts found with current filters.")

with tab3:
    st.markdown("## 💡 Data-Driven Insights")
    insight_col1, insight_col2 = st.columns(2)

    # ======== CALCULATE REAL INSIGHTS =======

    # Insight 1: Sentiment Distribution
    pos_pct= sent_stats['pos_pct']
    neg_pct = sent_stats['neg_pct']
    neu_pct = sent_stats['neu_pct']
        
    # Insight 1: Top subreddit by negativity
    if "attitude" in df_filtered.columns and "subreddit" in df_filtered.columns:
        sub_sentiment = df_filtered.groupby("subreddit")['attitude'].value_counts().unstack(fill_value=0)
        if "Negative" in sub_sentiment.columns:
            most_negative_sub = sub_sentiment['Negative'].idxmax()
            most_negative_pct = round(
                sub_sentiment.loc[most_negative_sub, "Negative"] / 
                sub_sentiment.loc[most_negative_sub].sum() * 100, 1
            )
        else:
            most_negative_sub = "N/A"
            most_negative_pct = 0
    else:
        most_negative_sub = "N/A"
        most_negative_pct = 0

    # Insight 3: Trend direction
    if df_trend_filtered is not None and len(df_trend_filtered) >= 3:
        recent_avg = df_trend_filtered['avg_vader'].tail(7).mean() if "avg_vader" in df_trend.columns else 0
        older_avg = df_trend_filtered['avg_vader'].head(7).mean() if "avg_vader" in df_trend.columns else 0
        trend_direction = "Up 📈" if recent_avg > older_avg else "down 📉"
        trend_change = round(abs(recent_avg - older_avg) * 100, 1)
    else:
        trend_direction = "stable ➡ "
        trend_change = 0

    # ===== SHOW INSIGHTS ======
    with insight_col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### ⚠ Warning Signals")
        st.markdown(f"**{neg_pct}%** of posts are negative/neutral in the selected period.")
        st.markdown(f"r/{most_negative_sub} is the most negative community ({most_negative_pct}% negative)")
        st.markdown(f"- Sentiment trend is going **{trend_direction}** by {trend_change}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with insight_col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 🌞 Positive Trends")
        st.markdown(f" - **{pos_pct}%** of posts express positive sentiment.")
        st.markdown(f" - **{top_occupation}** is the most discussed occupation ({top_percentage}% of posts)")
        if sentiment_msg and '**' in sentiment_msg:
            mood_word = sentiment_msg.split('**')[1]
        else:
            mood_word = 'neutral'
        st.markdown(f"- Average VADER score: **{avg_vader:.2f}** ({mood_word})")

        if avg_textblob > 0.05:
            objectivity_score = "slightly positive tone"
        elif avg_textblob < -0.05:
            objectivity_score = "Slightly negative tone"    
        else:
            objectivity_score = "mostly neutral/factual tone."
        st.markdown(f"- 📊 TextBlob polarity: **{avg_textblob:.2f}** ({objectivity_score})")
        st.markdown('</div>', unsafe_allow_html=True)

    # ======== WEEKLY SUMMARY ===========
    # Weekly summary
    st.markdown("### 📊 Weekly Summary")

    # CREATE SUMMARY BASED ON THE SCRAPED-DATA
    summary_parts = []

    if sentiment_counts is not None:
        summary_parts.append(
            f"During <strong>{start_date}</strong> to <strong>{end_date}</strong>, "
            f"<strong>{pos_pct}%</strong> of {len(df_filtered):,} analyzed posts were positive, "
            f"while <strong>{neg_pct}%</strong> expressed concerns.")
    
    if most_negative_sub != "N/A":
        summary_parts.append(f"The r/<strong>{most_negative_sub}</strong> community showed the highest level of concern "
                           f"at <strong>{most_negative_pct}%</strong> negative posts.")
    
    if trend_direction != "stable ➡️":
        summary_parts.append(f"Overall sentiment is trending <strong>{trend_direction}</strong>, "
                           f"shifting by <strong>{trend_change}%</strong> compared to the previous period.")
    
    summary_parts.append(f"<strong>{top_occupation}</strong> dominates discussions, "
                        f"representing <strong>{top_percentage}%</strong> of all occupation mentions across the platform.")
    
    full_summary = " ".join(summary_parts)
    
    st.markdown(f'''
    <div class="metric-card">
        <p style="color:#e0e0e0; line-height:1.6;">{full_summary}</p>
    </div>
    ''', unsafe_allow_html=True)
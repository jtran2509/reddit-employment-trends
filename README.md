# Comprehensive Market Intelligence Dashboard

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

**Scatter Plot** (Upvotes vs Number of Comments): xác định những chủ đề gây tranh cãi (debatable) hoặc được "quan tâm" nhất. Những bài ít vote nhưng nhiều cmmt thường là chủ đề gây tranh cãi.

**Time Series Line chart (post Volume/Time)**: Theo dõi số lượng bài đăng theo tuần/tháng. Nếu có 1 đợt sóng bài đăng đột ngột, có thể do 1 chính sách mới vừa ra đời.


**Heatmap** (Sentiment vs. Time of Day/Day of Week): xem thử liệu các bài đăng vào thứ 2 (khi scrape) thường mang tâm trạng gì so với các ngày khác.


**Topic modelling visualization (LDAvis)**: nhóm các bài viết thành chủ đề tự động => Cho thấy các bong bóng chủ đều tách biệt nhau như thế nào

Plot for hard skills likes: Python, SQL, Java, etc.

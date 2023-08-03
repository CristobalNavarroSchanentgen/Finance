# SIMPLE FINANCIAL NEWS POLARITY REPORT USING NEWSAPI


import requests
from textblob import TextBlob

# Define the endpoint and parameters
url = 'https://newsapi.org/v2/everything'
parameters = {
    'q': 'finance OR economy OR stock',
    'pageSize': 100,
    'language': 'en',
    'sources': 'bloomberg,financial-times,reuters',
    'apiKey': 'your-api-key'
}

# Fetch the news
response = requests.get(url, params=parameters)
data = response.json()

# Initializing variables to calculate average
total_polarity = 0
total_polarity_modified = 0
total_articles = 0

# Analyzing sentiment
for article in data['articles']:
    headline = article['title']
    description = article['description']
    text = headline + ' ' + description
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    total_polarity += sentiment_score
    total_polarity_modified += sentiment_score if sentiment_score != 0.0 else 1
    total_articles += 1
    print(f"Headline: {headline}")
    print(f"Sentiment Score: {sentiment_score}")
    print()

# Calculating average
average_polarity = round(total_polarity / total_articles, 4)
average_polarity_modified = round(total_polarity_modified / total_articles, 4)

print(f"Average Polarity: {average_polarity}")
print(f"Average Polarity (with 0.0 as 1): {average_polarity_modified}")

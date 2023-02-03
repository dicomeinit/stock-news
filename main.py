import requests
from twilio.rest import Client

import config

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = config.stock_api_key
NEWS_API_KEY = config.news_api_key

AUTH_TOKEN = config.twilio_auth_token
ACCOUNT_SID = config.twilio_account_sid
TWILIO_PHONE_NUMBER = config.twilio_phone_num
MY_PHONE_NUMBER = config.my_phone_num

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
response.raise_for_status()

# When stock price increase/decreases by 1% between yesterday and the day before yesterday then print("Get News").

# Get yesterday's closing stock price

data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = float(yesterday_data["4. close"])

# Get the day before yesterday's closing stock price

day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = float(day_before_yesterday_data["4. close"])

# Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20.

positive_diff = abs(yesterday_closing_price - day_before_yesterday_closing_price)
up_down = None
if positive_diff > 0:
    up_down = "🔺"
else:
    up_down = "🔻"


#  Work out the percentage difference in price between closing price yesterday and closing price the day
#  before yesterday.

percentage_diff = round((positive_diff/yesterday_closing_price) * 100)

# Instead of printing ("Get News"), use the News API to get articles related to the COMPANY_NAME.

if abs(percentage_diff) >= 1:

    news_parameters = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    articles = news_response.json()["articles"]
    three_articles = articles[:3]

    formatted_articles = [f"{STOCK_NAME}: {up_down}{percentage_diff}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
    print(formatted_articles)

    # Send each article as a separate message via Twilio.

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # Format the message:

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )

    """
    TSLA: 🔺2%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
    or
    "TSLA: 🔻5%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
    """

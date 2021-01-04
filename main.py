# --- IMPORTS ---
import requests
import os
import datetime as dt
from newsapi import NewsApiClient
from twilio.rest import Client

# --- CONSTANTS ---
# Stock Market
STOCK = "TSLA"
COMPANY_NAME = "Tesla"
STOCK_API_URL = "https://www.alphavantage.co/query"
print(os.environ.get("ALPHAVANTAGE_API_KEY"))
STOCK_PARAMETERS = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": os.environ.get("ALPHAVANTAGE_API_KEY")
}

# News
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_PARAMETERS = {
    "q": COMPANY_NAME,
    "APIkEY": NEWS_API_KEY
}

# Twilio
TWILIO_API_URL = ""
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
USER_PHONE_NUMBER = os.environ.get("PHONE_NUMBER")


# --- FUNCTIONS ---
def main():
    # STEP 1: Use https://www.alphavantage.co
    # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
    response = requests.get(url=STOCK_API_URL, params=STOCK_PARAMETERS)
    data_dict = response.json()

    # Get latest two closing prices
    last_two_days = [value for key, value in data_dict["Time Series (Daily)"].items()][:2]
    print(last_two_days)

    # Compare both close prices
    # try:
    one_day_closing_price = float(last_two_days[0]["4. close"])
    two_days_closing_price = float(last_two_days[1]["4. close"])
    # except KeyError:
    # print("The markets are closed.")
    # return

    difference = one_day_closing_price - two_days_closing_price
    five_percent = two_days_closing_price / 10
    percent_diff = round(difference / two_days_closing_price * 100, 2)

    print(difference, five_percent)
    if abs(difference) >= abs(five_percent):
        print("Get News!")

        is_up = percent_diff >= 0
        up_or_down = "🔻"
        if is_up:
            up_or_down = "🔺"

        print(f"There was a {percent_diff}% {up_or_down} in the stock value for "
              f"the {COMPANY_NAME}. date: {dt.datetime.today().date()}")

        # STEP 2: Use https://newsapi.org
        # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
        news_response = NewsApiClient(api_key=NEWS_API_KEY)
        top_headlines = news_response.get_top_headlines(q=COMPANY_NAME, language="en")["articles"][:3]
        print(top_headlines)

        # STEP 3: Use https://www.twilio.com Send a separate message with the percentage change and each article's
        # title and description to your phone number. Twilio Client
        twilio_client = Client(username=TWILIO_SID, password=TWILIO_AUTH_TOKEN)

        # Send messages
        for data in top_headlines:
            date = data["publishedAt"].split("T")
            message = twilio_client.messages.create(
                from_=TWILIO_PHONE_NUMBER,
                to=USER_PHONE_NUMBER,
                body=f"{STOCK}: {up_or_down}{percent_diff}%\n"
                     f"Title: {data['title']}\n"
                     f"Brief: {data['description']}\n"
                     f"date: {date[0]}\n"
                     f"url: {data['url']}"
            )
            print(message.sid)
        # Optional: Format the SMS message like this:
        """
        TSLA: 🔺2%
        Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
        Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds 
        and prominent investors are required to file by the SEC The 13F filings show 
        the funds' and investors' portfolio positions as of March 31st, near the height 
        of the coronavirus market crash.
        or
        "TSLA: 🔻5%
        Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
        Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds 
        and prominent investors are required to file by the SEC The 13F filings show 
        the funds' and investors' portfolio positions as of March 31st, near the height 
        of the coronavirus market crash.
        """


# --- RUN ---
if __name__ == '__main__':
    main()

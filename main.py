import requests
import smtplib

# Relative to the Stock API
STOCK_NAME = "TSLA"  # Stock of your preference
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_APIKEY = "YOUR_OWN_KEY"
# -------------------------

# Relative to the News API
COMPANY_NAME = "Tesla Inc"  # Company of your preference
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_APIKEY = "YOUR_OWN_KEY"
# ------------------------

# Relative to the email sender
EMAIL_SENDER = "YOUR_OWN_SENDER"
PASSWORD = "YOUR_OWN_PASSWORD"  # Use app passwords > "https://support.google.com/mail/answer/185833?hl=en"
RECEIVER_EMAIL = "YOUR_OWN_RECEIVER"
# ----------------------------


def get_stock_data():
    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK_NAME,
        "apikey": STOCK_APIKEY
    }

    response = requests.get(url=STOCK_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()
    return data


def get_news_data():
    parameters = {
        "q": COMPANY_NAME,
        "sortBY": "relevancy",
        "sortBy": "popularity",
        "apiKey": NEWS_APIKEY
    }

    response = requests.get(url=NEWS_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()
    return data


def send_email(my_message):
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=EMAIL_SENDER, password=PASSWORD)
        connection.sendmail(from_addr=EMAIL_SENDER, to_addrs=RECEIVER_EMAIL, msg=my_message)


stock_data = get_stock_data()

closing_prices = []
for day in stock_data["Time Series (Daily)"].items():
    closing_prices.append(day[1]["4. close"])

yesterday_closing_price = float(closing_prices[0])
before_yesterday_cp = float(closing_prices[1])

closing_percentage = ((yesterday_closing_price * 100) / before_yesterday_cp) - 100
closing_percentage_str = "{:.2f}".format(closing_percentage)

print(f"The closing price between yesterday and the day before yesterday was {closing_percentage_str}%")

if abs(closing_percentage) > 5:
    print("Sending the latest news to the user....\n")
    if closing_percentage > 0:
        symbol = "🔺"
    else:
        symbol = "🔻"

    news_data = get_news_data()

    last_news = news_data["articles"][0:3]  # Last 3 news in the case, but for other number just needs to change
    articles_and_headlines = [[element["title"], element["description"]] for element in last_news]
    messages = [f"Headline: {part[0]}\nBrief: {part[1]}\n\n" for part in articles_and_headlines]

    message = f"Subject: {STOCK_NAME}: {symbol}{closing_percentage_str}% | Get news!!!\n\n"

    for part in messages:
        message += part

    message_bytes = message.encode('utf-8')

    send_email(message_bytes)

else:
    print("No message to user.")

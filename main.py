import requests
import selectorlib
import smtplib
import ssl
import os
import time
import sqlite3

URL = "http://programmer100.pythonanywhere.com/tours/"
PASSWORD = os.getenv("GMAIL_WEBCAM_MESSAGE")
SENDER = os.getenv("GMAIL_EMAIL_ADDRESS")
RECEIVER = os.getenv("GMAIL_EMAIL_ADDRESS")

connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, message)
    print("Email was sent!")


def store(extracted_local):
    row_local = extracted_local.split(",")
    row_local = [item.strip() for item in row_local]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row_local)
    connection.commit()


def read(extracted_local):
    row_local = extracted_local.split(",")
    row_local = [item.strip() for item in row_local]
    band, city, date = row_local
    cursor = connection.cursor()
    cursor.execute("SELECT band, date FROM events WHERE band=? AND city=? "
                   "AND date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message="Hey, new event was found!")
        time.sleep(2)

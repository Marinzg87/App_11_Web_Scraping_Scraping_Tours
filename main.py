import requests
import selectorlib
import smtplib
import ssl
import os

URL = "http://programmer100.pythonanywhere.com/tours/"
PASSWORD = os.getenv("GMAIL_WEBCAM_MESSAGE")
SENDER = os.getenv("GMAIL_EMAIL_ADDRESS")
RECEIVER = os.getenv("GMAIL_EMAIL_ADDRESS")


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
    with open("data.txt", "a") as file:
        file.write(extracted_local + "\n")


def read(extracted_local):
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    scraped = scrape(URL)
    extracted = extract(scraped)
    print(extracted)
    content = read(extracted)
    if extracted != "No upcoming tours":
        if extracted not in content:
            store(extracted)
            send_email(message="Hey, new event was found!")

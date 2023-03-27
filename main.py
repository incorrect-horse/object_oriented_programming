import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3


URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class Event:
    def scrape(self, url):
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("files/extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    def send(self, message):
        host = "smtp.gmail.com"
        port = 465

        username = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("SEND_EMAIL")

        receiver = os.getenv("EMAIL_ADDRESS")
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)

        print("email sent")
        return


class Data:
    def __init__(self):
        self.connection = sqlite3.connect("files/data.db")

    def store(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
        self.connection.commit()
        return

    def read(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        band, city, date = row
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE band_name=? AND city=? AND date=?",
                       (band, city, date))
        contents = cursor.fetchall()
        return contents


if __name__ == "__main__":
    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            data = Data()
            content = data.read(extracted)
            if not content:
                data.store(extracted)
                message = f"""\
Subject: New Event Notification.

A new concert event was found:
{extracted}
"""
                message = message.encode("utf-8")
                email = Email()
                email.send(message)
            else:
                print("Event already logged, no email sent")
        time.sleep(2)

import os
import smtplib
from email.mime.text import MIMEText
from classes import CLASSES

gmail_address = os.environ["GMAIL_ADDRESS"]
gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
to_email = os.environ["TO_EMAIL"]

class_key = os.environ["CLASS_KEY"]
info = CLASSES[triggered_cron]

body = f"Booking opens now for {info['name']} ({info['class_day']} {info['class_time']})! 🏋️"

msg = MIMEText(body)
msg["Subject"] = "FFC Class Reminder"
msg["From"] = gmail_address
msg["To"] = to_email

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(gmail_address, gmail_app_password)
    server.sendmail(gmail_address, [to_email], msg.as_string())

print(f"Sent: {body}")

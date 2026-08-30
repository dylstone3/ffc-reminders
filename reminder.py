import os
from twilio.rest import Client
from classes import CLASSES

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
from_number = os.environ["TWILIO_FROM_NUMBER"]
to_number = os.environ["MY_PHONE_NUMBER"]


# GitHub tells us which cron schedule triggered this run
triggered_cron = os.environ["TRIGGERED_CRON"]
info = CLASSES[triggered_cron]


body = info['name']

client = Client(account_sid, auth_token)
message = client.messages.create(body=body, from_=from_number, to=to_number)

print(f"Sent: {body}")
print(f"SID: {message.sid}")

